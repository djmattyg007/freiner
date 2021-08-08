import time
from typing import Any, List, Union
from urllib.parse import urlparse

import pymemcache

from freiner.errors import FreinerConfigurationError
from freiner.types import Host


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
    def from_uri(cls, uri: str, **options: Any) -> "MemcachedStorage":
        """
        :param uri: URI of the form `memcached://host:port,host:port`or `memcached:///run/path/to/sock`.
        :param options: All remaining keyword arguments are passed directly to the constructor
                        of :class:`pymemcache.client.base.Client`.
        :raises FreinerConfigurationError: When no hosts could be parsed from the supplied URI.
        """

        parsed_uri = urlparse(uri)
        hosts: List[Union[Host, str]] = []
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
        Retrieve the current request count for the given rate limit key.

        :param key: The key to get the counter value for.
        """

        return int(self._client.get(key) or 0)

    def clear(self, key: str) -> None:
        """
        Resets the rate limit for the given key.

        :param key: The key to clear rate limits for.
        """
        self._client.delete(key)

    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        Increments the counter for the given rate limit key.

        :param key: The key to increment.
        :param expiry: Amount in seconds for the key to expire in.
        :param elastic_expiry: Whether to keep extending the rate limit window every hit.
        """

        if self._client.add(key, 1, expiry, noreply=False):
            self._set_expiry(key, expiry)
            return 1

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

        self._set_expiry(key, expiry)
        return int(value or 0) + 1

    def _set_expiry(self, key: str, expiry: int):
        self._client.set(key + "/expires", expiry + time.time(), expire=expiry, noreply=False)

    def get_expiry(self, key: str) -> float:
        """
        Retrieve the expected expiry time for the given rate limit key.

        :param key: The key to get the expiry time for.
        """

        return float(self._client.get(key + "/expires") or time.time())

    def check(self) -> bool:
        """
        Check if the connection to the storage backend is healthy.
        """

        try:
            self._client.get("freiner-check")
            return True
        except:  # noqa
            return False


__all__ = [
    "MemcachedClient",
    "MemcachedStorage",
]
