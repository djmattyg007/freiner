from urllib.parse import urlparse

try:
    import rediscluster
    HAS_REDISCLUSTER = True
except ImportError:
    HAS_REDISCLUSTER = False

from ..errors import FreinerConfigurationError
from .redis import RedisStorage


class RedisClusterStorage(RedisStorage):
    """
    Rate limit storage with redis cluster as backend

    Depends on `redis-py-cluster` library
    """

    def __init__(self, uri: str, **options):
        """
        :param str uri: url of the form
         `redis+cluster://[:password]@host:port,host:port`
        :param options: all remaining keyword arguments are passed
         directly to the constructor of :class:`rediscluster.RedisCluster`
        :raise FreinerConfigurationError: when the rediscluster library is not
         available or if the redis host cannot be pinged.
        """

        if not HAS_REDISCLUSTER:
            raise FreinerConfigurationError(
                "redis-py-cluster prerequisite not available"
            )

        parsed_uri = urlparse(uri)
        cluster_hosts = []
        for loc in parsed_uri.netloc.split(","):
            host, port = loc.split(":")
            cluster_hosts.append({"host": host, "port": int(port)})

        options.setdefault('max_connections', 1000)

        self.storage = rediscluster.RedisCluster(
            startup_nodes=cluster_hosts,
            **options
        )
        self.initialize_storage(self.storage)

    def reset(self):
        """
        Redis Clusters are sharded and deleting across shards
        can't be done atomically. Because of this, this reset loops over all
        keys that are prefixed with 'LIMITER' and calls delete on them, one at
        a time.

        .. warning::
         This operation was not tested with extremely large data sets.
         On a large production based system, care should be taken with its
         usage as it could be slow on very large data sets.
        """

        keys = self.storage.keys('LIMITER*')
        return sum([self.storage.delete(k.decode('utf-8')) for k in keys])
