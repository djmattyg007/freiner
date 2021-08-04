import time

import pytest

from freiner.limits import RateLimitItemPerMinute, RateLimitItemPerSecond
from freiner.storage import MemoryStorage
from freiner.strategies import (
    FixedWindowElasticExpiryRateLimiter,
    FixedWindowRateLimiter,
    MovingWindowRateLimiter,
)

from tests import freeze_time


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


def test_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        limit = RateLimitItemPerSecond(10, 2)
        start = int(time.time())

        assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

        frozen_datetime.tick(1)
        assert limiter.hit(limit) is False
        assert limiter.get_window_stats(limit)[1] == 0
        assert limiter.get_window_stats(limit)[0] == start + 2

        frozen_datetime.tick(1)
        assert limiter.get_window_stats(limit)[1] == 10
        assert limiter.hit(limit) is True


def test_fixed_window_with_elastic_expiry(storage: MemoryStorage):
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        limit = RateLimitItemPerSecond(10, 2)
        start = int(time.time())

        assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

        frozen_datetime.tick(1)
        assert limiter.hit(limit) is False
        assert limiter.get_window_stats(limit)[1] == 0
        # three extensions to the expiry
        assert limiter.get_window_stats(limit)[0] == start + 3

        frozen_datetime.tick(1)
        assert limiter.hit(limit) is False

        frozen_datetime.tick(3)
        start = int(time.time())
        assert limiter.hit(limit) is True
        assert limiter.get_window_stats(limit)[1] == 9
        assert limiter.get_window_stats(limit)[0] == start + 2


def test_moving_window_in_memory(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with freeze_time() as frozen_datetime:
        limit = RateLimitItemPerMinute(10)
        for i in range(0, 5):
            assert limiter.hit(limit) is True
            assert limiter.hit(limit) is True
            assert limiter.get_window_stats(limit)[1] == 10 - ((i + 1) * 2)
            frozen_datetime.tick(10)

        assert limiter.get_window_stats(limit)[1] == 0
        assert limiter.hit(limit) is False

        frozen_datetime.tick(20)
        assert limiter.get_window_stats(limit)[1] == 2
        assert limiter.get_window_stats(limit)[0] == int(time.time() + 30)

        frozen_datetime.tick(31)
        assert limiter.get_window_stats(limit)[1] == 10


def test_test_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with freeze_time():
        limit = RateLimitItemPerSecond(2, 1)

        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is False
        assert limiter.hit(limit) is False


def test_test_moving_window(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with freeze_time():
        limit = RateLimitItemPerSecond(2, 1)

        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is False
        assert limiter.hit(limit) is False
