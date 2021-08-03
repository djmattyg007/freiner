import inspect
import threading
import time
from typing import List, Tuple, Union
from urllib.parse import urlparse

from ..errors import FreinerConfigurationError
from ..util import get_dependency


class MemcachedStorage:
    """
    Rate limit storage with memcached as backend.

    Depends on the `pymemcache` library.
    """
    MAX_CAS_RETRIES = 10

    def __init__(self, uri: str, **options):
        """
        :param str uri: memcached location of the form
         `memcached://host:port,host:port`, `memcached:///var/tmp/path/to/sock`
        :param options: all remaining keyword arguments are passed
         directly to the constructor of :class:`pymemcache.client.base.Client`
        :raise FreinerConfigurationError: when `pymemcache` is not available
        """
        parsed_uri = urlparse(uri)
        self.hosts: List[Union[Tuple[str, int], str]] = []
        for loc in parsed_uri.netloc.strip().split(","):
            if not loc:
                continue
            host, port = loc.split(":")
            self.hosts.append((host, int(port)))
        else:
            # filesystem path to UDS
            if parsed_uri.path and not parsed_uri.netloc and not parsed_uri.port:
                self.hosts = [parsed_uri.path]

        self.library = options.pop('library', 'pymemcache.client')
        self.cluster_library = options.pop('library', 'pymemcache.client.hash')
        self.client_getter = options.pop('client_getter', self.get_client)
        self.options = options

        if not get_dependency(self.library):
            raise FreinerConfigurationError(
                "memcached prerequisite not available."
                " please install %s" % self.library
            )  # pragma: no cover

        self.local_storage = threading.local()
        self.local_storage.storage = None

    def get_client(self, module, hosts, **kwargs):
        """
        returns a memcached client.
        :param module: the memcached module
        :param hosts: list of memcached hosts
        :return:
        """
        return (
            module.HashClient(hosts, **kwargs)
            if len(hosts) > 1 else module.Client(*hosts, **kwargs)
        )

    @property
    def storage(self):
        """
        lazily creates a memcached client instance using a thread local
        """
        if not (
            hasattr(self.local_storage, "storage")
            and self.local_storage.storage
        ):
            self.local_storage.storage = self.client_getter(
                get_dependency(
                    self.cluster_library if len(self.hosts) > 1
                    else self.library
                ),
                self.hosts, **self.options
            )

        return self.local_storage.storage

    def get(self, key) -> int:
        """
        :param str key: the key to get the counter value for
        """
        return int(self.storage.get(key) or 0)

    def clear(self, key):
        """
        :param str key: the key to clear rate limits for
        """
        self.storage.delete(key)

    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        increments the counter for a given rate limit key

        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        :param bool elastic_expiry: whether to keep extending the rate limit
         window every hit.
        """

        if not self.storage.add(key, 1, expiry, noreply=False):
            if elastic_expiry:
                value, cas = self.storage.gets(key)
                retry = 0

                while not self.storage.cas(key, int(value or 0) + 1, cas, expiry) and retry < self.MAX_CAS_RETRIES:
                    value, cas = self.storage.gets(key)
                    retry += 1

                self.storage.set(key + "/expires", expiry + time.time(), expire=expiry, noreply=False)
                return int(value or 0) + 1
            else:
                return self.storage.incr(key, 1)

        self.storage.set(key + "/expires", expiry + time.time(), expire=expiry, noreply=False)
        return 1

    def get_expiry(self, key: str) -> int:
        """
        :param str key: the key to get the expiry for
        """
        return int(float(self.storage.get(key + "/expires") or time.time()))

    def check(self) -> bool:
        """
        check if storage is healthy
        """
        try:
            self.storage.get("freiner-check")
            return True
        except:  # noqa
            return False
