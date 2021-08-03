import time
from typing import cast, Callable, List, Tuple

from ..util import get_dependency
from ..errors import FreinerConfigurationError


class RedisInteractor:
    SCRIPT_MOVING_WINDOW = """
        local items = redis.call('lrange', KEYS[1], 0, tonumber(ARGV[2]))
        local expiry = tonumber(ARGV[1])
        local a = 0
        local oldest = nil
        for idx=1,#items do
            if tonumber(items[idx]) >= expiry then
                a = a + 1
                if oldest == nil then
                    oldest = tonumber(items[idx])
                end
            else
                break
            end
        end
        return {oldest, a}
        """

    SCRIPT_ACQUIRE_MOVING_WINDOW = """
        local entry = redis.call('lindex', KEYS[1], tonumber(ARGV[2]) - 1)
        local timestamp = tonumber(ARGV[1])
        local expiry = tonumber(ARGV[3])
        if entry and tonumber(entry) >= timestamp - expiry then
            return false
        end
        local limit = tonumber(ARGV[2])
        local no_add = tonumber(ARGV[4])
        if 0 == no_add then
            redis.call('lpush', KEYS[1], timestamp)
            redis.call('ltrim', KEYS[1], 0, limit - 1)
            redis.call('expire', KEYS[1], expiry)
        end
        return true
        """

    SCRIPT_CLEAR_KEYS = """
        local keys = redis.call('keys', KEYS[1])
        local res = 0
        for i=1,#keys,5000 do
            res = res + redis.call(
                'del', unpack(keys, i, math.min(i+4999, #keys))
            )
        end
        return res
        """

    SCRIPT_INCR_EXPIRE = """
        local current
        current = redis.call("incr",KEYS[1])
        if tonumber(current) == 1 then
            redis.call("expire",KEYS[1],ARGV[1])
        end
        return current
    """

    def initialize_storage(self, storage):
        moving_window_script = storage.register_script(
            self.SCRIPT_MOVING_WINDOW
        )
        self.lua_moving_window = cast(Callable[[Tuple[str], Tuple[int, int]], Tuple[int, int]], moving_window_script)

        acquire_window_script = storage.register_script(
            self.SCRIPT_ACQUIRE_MOVING_WINDOW
        )
        self.lua_acquire_window = cast(Callable[[Tuple[str], Tuple[float, int, int, int]], bool], acquire_window_script)

        clear_keys_script = storage.register_script(
            self.SCRIPT_CLEAR_KEYS
        )
        self.lua_clear_keys = cast(Callable[[Tuple[str]], int], clear_keys_script)

        incr_expire_script = storage.register_script(
            RedisStorage.SCRIPT_INCR_EXPIRE
        )
        self.lua_incr_expire = cast(Callable[[Tuple[str], Tuple[int]], int], incr_expire_script)

    def _incr(self, key: str, expiry: int, connection, elastic_expiry: bool = False):
        """
        increments the counter for a given rate limit key

        :param connection: Redis connection
        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        """
        value = connection.incr(key)
        if elastic_expiry or value == 1:
            connection.expire(key, expiry)
        return value

    def _get(self, key: str, connection) -> int:
        """
        :param connection: Redis connection
        :param str key: the key to get the counter value for
        """
        return int(connection.get(key) or 0)

    def _clear(self, key: str, connection):
        """
        :param str key: the key to clear rate limits for
        :param connection: Redis connection
        """
        connection.delete(key)

    def get_moving_window(self, key: str, limit: int, expiry: int) -> Tuple[int, int]:
        """
        returns the starting point and the number of entries in the moving
        window

        :param str key: rate limit key
        :param int limit: amount of entries allowed
        :param int expiry: expiry of entry
        :return: (start of window, number of acquired entries)
        """
        timestamp = time.time()
        window = self.lua_moving_window((key,), (int(timestamp - expiry), limit))
        return window or (int(timestamp), 0)

    def _acquire_entry(self, key: str, limit: int, expiry: int, connection, no_add: bool = False) -> bool:
        """
        :param str key: rate limit key to acquire an entry in
        :param int limit: amount of entries allowed
        :param int expiry: expiry of the entry
        :param bool no_add: if False an entry is not actually acquired but
         instead serves as a 'check'
        :param connection: Redis connection
        :return: True/False
        """
        timestamp = time.time()
        acquired = self.lua_acquire_window(
            (key,),
            (timestamp, limit, expiry, int(no_add)),
        )
        return bool(acquired)

    def _get_expiry(self, key: str, connection=None) -> int:
        """
        :param str key: the key to get the expiry for
        :param connection: Redis connection
        """
        return int(max(connection.ttl(key), 0) + time.time())

    def _check(self, connection) -> bool:
        """
        :param connection: Redis connection
        check if storage is healthy
        """
        try:
            return connection.ping()
        except:  # noqa
            return False


class RedisStorage(RedisInteractor):
    """
    Rate limit storage with redis as backend.

    Depends on the `redis-py` library.
    """

    def __init__(self, uri: str, **options):
        """
        :param str uri: uri of the form `redis://[:password]@host:port`,
         `redis://[:password]@host:port/db`,
         `rediss://[:password]@host:port`, `redis+unix:///path/to/sock` etc.
         This uri is passed directly to :func:`redis.from_url` except for the
         case of `redis+unix` where it is replaced with `unix`.
        :param options: all remaining keyword arguments are passed
         directly to the constructor of :class:`redis.Redis`
        :raise ConfigurationError: when the redis library is not available
        """
        if not get_dependency("redis"):
            raise FreinerConfigurationError(
                "redis prerequisite not available"
            )  # pragma: no cover
        uri = uri.replace('redis+unix', 'unix')
        # TODO: rename self.storage to self.connection
        self.storage = get_dependency("redis").from_url(uri, **options)
        self.initialize_storage(self.storage)

    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        increments the counter for a given rate limit key

        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        """
        if elastic_expiry:
            return self._incr(key, expiry, self.storage, elastic_expiry)
        else:
            return self.lua_incr_expire((key,), (expiry,))

    def get(self, key: str) -> int:
        """
        :param str key: the key to get the counter value for
        """
        return self._get(key, self.storage)

    def clear(self, key: str):
        """
        :param str key: the key to clear rate limits for
        """
        return self._clear(key, self.storage)

    def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
        """
        :param str key: rate limit key to acquire an entry in
        :param int limit: amount of entries allowed
        :param int expiry: expiry of the entry
        :param bool no_add: if False an entry is not actually acquired but
         instead serves as a 'check'
        :return: True/False
        """
        return self._acquire_entry(
            key, limit, expiry, self.storage, no_add=no_add
        )

    def get_expiry(self, key: str) -> int:
        """
        :param str key: the key to get the expiry for
        """
        return self._get_expiry(key, self.storage)

    def check(self) -> bool:
        """
        check if storage is healthy
        """
        return self._check(self.storage)

    def reset(self):
        """
        This function calls a Lua Script to delete keys prefixed with 'LIMITER'
        in block of 5000.

        .. warning::
           This operation was designed to be fast, but was not tested
           on a large production based system. Be careful with its usage as it
           could be slow on very large data sets.

        """

        cleared = self.lua_clear_keys(('LIMITER*',))
        return cleared