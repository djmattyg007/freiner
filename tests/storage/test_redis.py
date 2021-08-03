import time
import unittest
import unittest.mock

import pytest
import redis

from freiner import RateLimitItemPerSecond, RateLimitItemPerMinute
from freiner.storage.redis import RedisStorage
from freiner.strategies import FixedWindowRateLimiter, MovingWindowRateLimiter

from tests import DOCKERDIR


@pytest.mark.unit
class SharedRedisTests(object):
    def test_fixed_window(self):
        limiter = FixedWindowRateLimiter(self.storage)
        per_second = RateLimitItemPerSecond(10)
        start = time.time()
        count = 0
        while time.time() - start < 0.5 and count < 10:
            self.assertTrue(limiter.hit(per_second))
            count += 1
        self.assertFalse(limiter.hit(per_second))
        while time.time() - start <= 1:
            time.sleep(0.1)
        [self.assertTrue(limiter.hit(per_second)) for _ in range(10)]

    def test_reset(self):
        limiter = FixedWindowRateLimiter(self.storage)
        for i in range(0, 10):
            rate = RateLimitItemPerMinute(i)
            limiter.hit(rate)
        self.assertEqual(self.storage.reset(), 10)

    def test_fixed_window_clear(self):
        limiter = FixedWindowRateLimiter(self.storage)
        per_min = RateLimitItemPerMinute(1)
        limiter.hit(per_min)
        self.assertFalse(limiter.hit(per_min))
        limiter.clear(per_min)
        self.assertTrue(limiter.hit(per_min))

    def test_moving_window_clear(self):
        limiter = MovingWindowRateLimiter(self.storage)
        per_min = RateLimitItemPerMinute(1)
        limiter.hit(per_min)
        self.assertFalse(limiter.hit(per_min))
        limiter.clear(per_min)
        self.assertTrue(limiter.hit(per_min))

    def test_moving_window_expiry(self):
        limiter = MovingWindowRateLimiter(self.storage)
        limit = RateLimitItemPerSecond(2)
        self.assertTrue(limiter.hit(limit))
        time.sleep(0.9)
        self.assertTrue(limiter.hit(limit))
        self.assertFalse(limiter.hit(limit))
        time.sleep(0.1)
        self.assertTrue(limiter.hit(limit))
        last = time.time()
        while time.time() - last <= 1:
            time.sleep(0.05)
        self.assertTrue(self.storage._client.keys("%s/*" % limit.namespace) == [])


@pytest.mark.unit
class RedisStorageTests(SharedRedisTests, unittest.TestCase):
    def setUp(self):
        self.storage_url = "redis://localhost:7379"
        self.storage = RedisStorage.from_uri(self.storage_url)
        redis.from_url(self.storage_url).flushall()

    # TODO: Re-do this once URIs go to named constructors
    # Also add a test for "missing dependency" in the named constructor
    # def test_init_options(self):
    #     with unittest.mock.patch(
    #         "freiner.storage.redis.get_dependency"
    #     ) as get_dependency:
    #         storage = RedisStorage(self.storage_url, connection_timeout=1)
    #         storage.check()
    #         self.assertEqual(
    #             get_dependency().from_url.call_args[1]["connection_timeout"], 1
    #         )


@pytest.mark.unit
class RedisUnixSocketStorageTests(SharedRedisTests, unittest.TestCase):
    def setUp(self):
        self.redis_socket_path = DOCKERDIR / "redis" / "freiner.redis.sock"

        self.storage_url = "unix://" + str(self.redis_socket_path)
        self.storage = RedisStorage.from_uri(self.storage_url)
        redis.from_url("unix://" + str(self.redis_socket_path)).flushall()

    # TODO: Re-do this once URIs go to named constructors
    # Also add a test for "missing dependency" in the named constructor
    # def test_init_options(self):
    #     with unittest.mock.patch(
    #         "freiner.storage.redis.get_dependency"
    #     ) as get_dependency:
    #         storage = RedisStorage(self.storage_url, connection_timeout=1)
    #         storage.check()
    #         self.assertEqual(
    #             get_dependency().from_url.call_args[1]["connection_timeout"], 1
    #         )
