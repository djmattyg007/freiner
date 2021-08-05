import time
from typing import List, Tuple, Union
from urllib.parse import urlparse

from freiner.errors import FreinerConfigurationError


try:
    import pymemcache

    HAS_MEMCACHED = True
except ImportError:  # pragma: no cover
    HAS_MEMCACHED = False


MemcachedClient = Union[pymemcache.Client, pymemcache.PooledClient, pymemcache.HashClient]


class MemcachedStorage:
    """
    Rate limit storage with memcached as backend.

    Depends on the `pymemcache` library.
    """

    MAX_CAS_RETRIES = 10

    def __init__(self, client: MemcachedClient):
        self._client: MemcachedClient = client

    @classmethod
    def from_uri(cls, uri: str, **options) -> "MemcachedStorage":
        """
        :param str uri: memcached location of the form
         `memcached://host:port,host:port`, `memcached:///run/path/to/sock`
        :param options: all remaining keyword arguments are passed
         directly to the constructor of :class:`pymemcache.client.base.Client`
        :raise FreinerConfigurationError: when `pymemcache` dependency is not available
        """

        if not HAS_MEMCACHED:
            raise FreinerConfigurationError("Dependency 'pymemcache' is not available.")

        parsed_uri = urlparse(uri)
        hosts: List[Union[Tuple[str, int], str]] = []
        for loc in parsed_uri.netloc.strip().split(","):
            if not loc:
                continue

            host, port = loc.split(":")
            hosts.append((host, int(port)))
        else:
            # filesystem path to UDS
            if parsed_uri.path and not parsed_uri.netloc and not parsed_uri.port:
                hosts = [parsed_uri.path]

        if not hosts:
            raise FreinerConfigurationError(f"No Memcached hosts parsed from URI: {uri}")

        if len(hosts) > 1:
            client = pymemcache.HashClient(hosts, **options)
        else:
            client = pymemcache.Client(*hosts, **options)
        return cls(client)

    def get(self, key: str) -> int:
        """
        :param str key: the key to get the counter value for
        """
        return int(self._client.get(key) or 0)

    def clear(self, key: str):
        """
        :param str key: the key to clear rate limits for
        """
        self._client.delete(key)

    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        increments the counter for a given rate limit key

        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        :param bool elastic_expiry: whether to keep extending the rate limit
         window every hit.
        """

        if not self._client.add(key, 1, expiry, noreply=False):
            if not elastic_expiry:
                return self._client.incr(key, 1) or 1

            value, cas = self._client.gets(key)
            retry = 0

            while (
                not self._client.cas(key, int(value or 0) + 1, cas, expiry)
                and retry < self.MAX_CAS_RETRIES
            ):
                value, cas = self._client.gets(key)
                retry += 1

            self._client.set(key + "/expires", expiry + time.time(), expire=expiry, noreply=False)
            return int(value or 0) + 1

        self._client.set(key + "/expires", expiry + time.time(), expire=expiry, noreply=False)
        return 1

    def get_expiry(self, key: str) -> int:
        """
        :param str key: the key to get the expiry for
        """
        return int(float(self._client.get(key + "/expires") or time.time()))

    def check(self) -> bool:
        """
        check if storage is healthy
        """
        try:
            self._client.get("freiner-check")
            return True
        except:  # noqa
            return False

    def reset(self):
        """
        Not implemented for Memcached.
        """
        pass
