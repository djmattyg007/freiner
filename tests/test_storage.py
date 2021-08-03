import time

import pymemcache.client
import redis
import redis.sentinel
import unittest

from freiner.errors import FreinerConfigurationError
from freiner.storage import Storage, MemoryStorage
from freiner.storage.memcached import MemcachedStorage
from freiner.storage.redis import RedisStorage
from freiner.storage.redis_sentinel import RedisSentinelStorage
from freiner.strategies import MovingWindowRateLimiter

from tests import DOCKERDIR


class BaseStorageTests(unittest.TestCase):
    def setUp(self):
        self.redis_socket_path = DOCKERDIR / "redis" / "freiner.redis.sock"

        pymemcache.client.Client(("localhost", 22122)).flush_all()
        redis.from_url("unix://" + str(self.redis_socket_path)).flushall()
        redis.from_url("redis://localhost:7379").flushall()
        redis.from_url("redis://:sekret@localhost:7389").flushall()
        redis.sentinel.Sentinel([
            ("localhost", 26379)
        ]).master_for("localhost-redis-sentinel").flushall()

    # TODO: Check to see if these should be moved elsewhere
    # def test_storage_string(self):
    #     self.assertTrue(
    #         isinstance(storage_from_string("memory://"), MemoryStorage)
    #     )
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string("redis://localhost:7379"), RedisStorage
    #         )
    #     )
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string("redis+unix:///tmp/freiner.redis.sock"),
    #             RedisStorage
    #         )
    #     )
    #
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string("redis+unix://:password/tmp/freiner.redis.sock"),  # noqa: E501
    #             RedisStorage
    #         )
    #     )
    #
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string("memcached://localhost:22122"),
    #             MemcachedStorage
    #         )
    #     )
    #
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string("memcached://localhost:22122,localhost:22123"),  # noqa: E501
    #             MemcachedStorage
    #         )
    #     )
    #
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string("memcached:///tmp/freiner.memcached.sock"),
    #             MemcachedStorage
    #         )
    #     )
    #
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string(
    #                 "redis+sentinel://localhost:26379",
    #                 service_name="localhost-redis-sentinel"
    #             ), RedisSentinelStorage
    #         )
    #     )
    #     self.assertTrue(
    #         isinstance(
    #             storage_from_string(
    #                 "redis+sentinel://localhost:26379/localhost-redis-sentinel"
    #             ), RedisSentinelStorage
    #         )
    #     )
    #
    #     self.assertRaises(FreinerConfigurationError, storage_from_string, "blah://")
    #     self.assertRaises(
    #         FreinerConfigurationError, storage_from_string,
    #         "redis+sentinel://localhost:26379"
    #     )
    #     with unittest.mock.patch(
    #         "freiner.storage.redis_sentinel.get_dependency"
    #     ) as get_dependency:
    #         self.assertTrue(
    #             isinstance(
    #                 storage_from_string("redis+sentinel://:foobared@localhost:26379/localhost-redis-sentinel"),  # noqa: E501
    #                 RedisSentinelStorage
    #             )
    #         )
    #         self.assertEqual(
    #             get_dependency().Sentinel.call_args[1]['password'], 'foobared'
    #         )

    # TODO: Move these elsewhere, check tests shouldn't be tied to storage_from_string()
    # def test_storage_check(self):
    #     self.assertTrue(
    #         storage_from_string("memory://").check()
    #     )
    #     self.assertTrue(
    #         storage_from_string("redis://localhost:7379").check()
    #     )
    #     self.assertTrue(
    #         storage_from_string("redis://:sekret@localhost:7389").check()
    #     )
    #     self.assertTrue(
    #         storage_from_string(
    #             "redis+unix:///tmp/freiner.redis.sock"
    #         ).check()
    #     )
    #     self.assertTrue(
    #         storage_from_string("memcached://localhost:22122").check()
    #     )
    #     self.assertTrue(
    #         storage_from_string(
    #             "memcached://localhost:22122,localhost:22123"
    #         ).check()
    #     )
    #     self.assertTrue(
    #         storage_from_string(
    #             "memcached:///tmp/freiner.memcached.sock"
    #         ).check()
    #     )
    #     self.assertTrue(
    #         storage_from_string(
    #             "redis+sentinel://localhost:26379",
    #             service_name="localhost-redis-sentinel"
    #         ).check()
    #     )

    def test_pluggable_storage_no_moving_window(self):
        class MyStorage(Storage):
            def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
                return 1

            def get(self, key: str) -> int:
                return 0

            def get_expiry(self, key) -> int:
                return int(time.time())

        storage = MyStorage()
        self.assertRaises(
            NotImplementedError, MovingWindowRateLimiter, storage
        )

    def test_pluggable_storage_moving_window(self):
        class MyStorage(Storage):
            def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
                return 1

            def get(self, key: str) -> int:
                return 0

            def get_expiry(self, key: str) -> int:
                return int(time.time())

            def acquire_entry(self, *a, **k) -> bool:
                return True

            def get_moving_window(self, *a, **k):
                return (time.time(), 1)

        storage = MyStorage()
        strategy = MovingWindowRateLimiter(storage)
        assert strategy.storage is storage


