from urllib.parse import urlparse

from freiner.errors import FreinerConfigurationError
from .memory import MemoryStorage

from .base import Storage
from .registry import SCHEMES
from .redis import RedisStorage
from .redis_cluster import RedisClusterStorage
from .redis_sentinel import RedisSentinelStorage
from .memcached import MemcachedStorage


def storage_from_string(storage_string, **options):
    """
    factory function to get an instance of the storage class based
    on the uri of the storage

    :param storage_string: a string of the form method://host:port
    :return: an instance of :class:`flask_limiter.storage.Storage`
    """
    scheme = urlparse(storage_string).scheme
    if scheme not in SCHEMES:
        raise FreinerConfigurationError(
            "unknown storage scheme : %s" % storage_string
        )
    return SCHEMES[scheme](storage_string, **options)


__all__ = [
    "storage_from_string",
    "Storage",
    "MemoryStorage",
    "RedisStorage",
    "RedisClusterStorage",
    "RedisSentinelStorage",
    "MemcachedStorage",
]
