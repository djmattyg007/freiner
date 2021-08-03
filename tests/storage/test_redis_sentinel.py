import unittest
import unittest.mock

import redis.sentinel

from freiner.storage.redis_sentinel import RedisSentinelStorage
from tests.storage.test_redis import SharedRedisTests


class RedisSentinelStorageTests(SharedRedisTests, unittest.TestCase):
    def setUp(self):
        self.storage_url = 'redis+sentinel://localhost:26379'
        self.service_name = 'localhost-redis-sentinel'
        self.storage = RedisSentinelStorage.from_uri(
            self.storage_url,
            service_name=self.service_name
        )
        redis.sentinel.Sentinel([
            ("localhost", 26379)
        ]).master_for(self.service_name).flushall()

    # TODO: Re-do this once URIs go to named constructors
    # Also add a test for "missing dependency" in the named constructor
    # def test_init_options(self):
    #     url = self.storage_url + "/" + self.service_name
    #     with unittest.mock.patch(
    #         "freiner.storage.redis_sentinel.get_dependency"
    #     ) as get_dependency:
    #         storage = RedisSentinelStorage(url, connection_timeout=1)
    #         storage.check()
    #         self.assertEqual(
    #             get_dependency().Sentinel.call_args[1]['connection_timeout'], 1
    #         )
