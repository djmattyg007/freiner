import time
import unittest
import unittest.mock

import pymemcache

from freiner import RateLimitItemPerSecond, RateLimitItemPerMinute
from freiner.storage.memcached import MemcachedStorage
from freiner.strategies import (
    FixedWindowRateLimiter,
    FixedWindowElasticExpiryRateLimiter
)
from tests import fixed_start


class MemcachedStorageTests(unittest.TestCase):
    def setUp(self):
        pymemcache.Client(("localhost", 22122)).flush_all()
        self.storage_url = "memcached://localhost:22122"

    # TODO: Re-do this once URIs go to named constructors
    # Also add a test for "missing dependency" in the named constructor
    # def test_options(self):
    #     with unittest.mock.patch(
    #         "freiner.storage.memcached.pymemcache"
    #     ) as get_dependency:
    #         storage = MemcachedStorage(self.storage_url, connect_timeout=1)
    #         storage.check()
    #         self.assertEqual(
    #             pymemcache.Client.call_args[1]['connect_timeout'], 1
    #         )

    @fixed_start
    def test_fixed_window(self):
        storage = MemcachedStorage("memcached://localhost:22122")
        self.assertTrue(storage.check())

        limiter = FixedWindowRateLimiter(storage)
        per_min = RateLimitItemPerSecond(10)
        start = time.time()
        count = 0
        while time.time() - start < 0.5 and count < 10:
            self.assertTrue(limiter.hit(per_min))
            count += 1
        self.assertFalse(limiter.hit(per_min))
        while time.time() - start <= 1:
            time.sleep(0.1)
        self.assertTrue(limiter.hit(per_min))

    @fixed_start
    def test_fixed_window_cluster(self):
        storage = MemcachedStorage("memcached://localhost:22122,localhost:22123")
        self.assertTrue(storage.check())

        limiter = FixedWindowRateLimiter(storage)
        per_min = RateLimitItemPerSecond(10)
        start = time.time()
        count = 0
        while time.time() - start < 0.5 and count < 10:
            self.assertTrue(limiter.hit(per_min))
            count += 1
        self.assertFalse(limiter.hit(per_min))
        while time.time() - start <= 1:
            time.sleep(0.1)
        self.assertTrue(limiter.hit(per_min))

    @fixed_start
    def test_fixed_window_with_elastic_expiry(self):
        storage = MemcachedStorage("memcached://localhost:22122")
        self.assertTrue(storage.check())

        limiter = FixedWindowElasticExpiryRateLimiter(storage)
        per_sec = RateLimitItemPerSecond(2, 2)

        self.assertTrue(limiter.hit(per_sec))
        time.sleep(1)
        self.assertTrue(limiter.hit(per_sec))
        self.assertFalse(limiter.test(per_sec))
        time.sleep(1)
        self.assertFalse(limiter.test(per_sec))
        time.sleep(1)
        self.assertTrue(limiter.test(per_sec))

    @fixed_start
    def test_fixed_window_with_elastic_expiry_cluster(self):
        storage = MemcachedStorage("memcached://localhost:22122,localhost:22123")
        self.assertTrue(storage.check())

        limiter = FixedWindowElasticExpiryRateLimiter(storage)
        per_sec = RateLimitItemPerSecond(2, 2)

        self.assertTrue(limiter.hit(per_sec))
        time.sleep(1)
        self.assertTrue(limiter.hit(per_sec))
        self.assertFalse(limiter.test(per_sec))
        time.sleep(1)
        self.assertFalse(limiter.test(per_sec))
        time.sleep(1)
        self.assertTrue(limiter.test(per_sec))

    def test_clear(self):
        storage = MemcachedStorage("memcached://localhost:22122")
        self.assertTrue(storage.check())

        limiter = FixedWindowRateLimiter(storage)
        per_min = RateLimitItemPerMinute(1)
        limiter.hit(per_min)
        self.assertFalse(limiter.hit(per_min))
        limiter.clear(per_min)
        self.assertTrue(limiter.hit(per_min))
