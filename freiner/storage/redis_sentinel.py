from typing import Optional
from urllib.parse import urlparse

from freiner.errors import FreinerConfigurationError

from .redis import RedisStorage


try:
    import redis.sentinel

    HAS_REDIS = True
except ImportError:  # pragma: no cover
    HAS_REDIS = False


class RedisSentinelStorage(RedisStorage):
    """
    Rate limit storage with redis sentinel as backend.

    Depends on `redis` library.
    """

    def __init__(self, sentinel: redis.sentinel.Sentinel, service_name: str):
        self._sentinel: redis.sentinel.Sentinel = sentinel
        self._service_name: str = service_name

        self._sentinel_master: redis.Redis = self._sentinel.master_for(self._service_name)
        self._sentinel_slave: redis.Redis = self._sentinel.slave_for(self._service_name)

        super().__init__(self._sentinel_master)

    @classmethod
    def from_uri(
        cls, uri: str, service_name: Optional[str] = None, **options
    ) -> "RedisSentinelStorage":
        """
        :param str uri: url of the form
         `redis+sentinel://host:port,host:port/service_name`
        :param Optional[str] service_name: sentinel service name
         (if not provided in `uri`)
        :param options: all remaining keyword arguments are passed
         directly to the constructor of :class:`redis.sentinel.Sentinel`
        :raise FreinerConfigurationError: when the redis library is not available
         or if the redis master host cannot be pinged.
        """

        if not HAS_REDIS:
            raise FreinerConfigurationError("Dependency 'redis' is not available.")

        parsed_uri = urlparse(uri)
        sentinel_configuration = []

        password = None
        if parsed_uri.password:
            password = parsed_uri.password

        for loc in parsed_uri.netloc[parsed_uri.netloc.find("@") + 1 :].split(","):
            host, port = loc.split(":")
            sentinel_configuration.append((host, int(port)))

        service_name = parsed_uri.path.replace("/", "") if parsed_uri.path else service_name
        if service_name is None:
            raise FreinerConfigurationError("'service_name' not provided")

        options.setdefault("socket_timeout", 0.2)

        sentinel = redis.sentinel.Sentinel(sentinel_configuration, password=password, **options)
        return cls(sentinel, service_name)

    def get(self, key: str) -> int:
        """
        :param str key: the key to get the counter value for
        """
        return self._get(key, self._sentinel_slave)

    def get_expiry(self, key: str) -> int:
        """
        :param str key: the key to get the expiry for
        """
        return self._get_expiry(key, self._sentinel_slave)

    def check(self) -> bool:
        """
        check if storage is healthy
        """
        return self._check(self._sentinel_slave)
