import time

import hiro
import pytest

from freiner.limits import RateLimitItemPerSecond, RateLimitItemPerMinute
from freiner.storage import MemoryStorage
from freiner.strategies import FixedWindowRateLimiter, FixedWindowElasticExpiryRateLimiter, MovingWindowRateLimiter


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


def test_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with hiro.Timeline().freeze() as timeline:
        limit = RateLimitItemPerSecond(10, 2)
        start = int(time.time())

        assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

        timeline.forward(1)
        assert limiter.hit(limit) is False
        assert limiter.get_window_stats(limit)[1] == 0
        assert limiter.get_window_stats(limit)[0] == start + 2

        timeline.forward(1)
        assert limiter.get_window_stats(limit)[1] == 10
        assert limiter.hit(limit) is True


def test_fixed_window_with_elastic_expiry(storage: MemoryStorage):
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    with hiro.Timeline().freeze() as timeline:
        limit = RateLimitItemPerSecond(10, 2)
        start = int(time.time())

        assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

        timeline.forward(1)
        assert limiter.hit(limit) is False
        assert limiter.get_window_stats(limit)[1] == 0
        # three extensions to the expiry
        assert limiter.get_window_stats(limit)[0] == start + 3

        timeline.forward(1)
        assert limiter.hit(limit) is False

        timeline.forward(3)
        start = int(time.time())
        assert limiter.hit(limit) is True
        assert limiter.get_window_stats(limit)[1] == 9
        assert limiter.get_window_stats(limit)[0] == start + 2


def test_moving_window_in_memory(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)

    with hiro.Timeline().freeze() as timeline:
        limit = RateLimitItemPerMinute(10)
        for i in range(0, 5):
            assert limiter.hit(limit) is True
            assert limiter.hit(limit) is True
            assert limiter.get_window_stats(limit)[1] == 10 - ((i + 1) * 2)
            timeline.forward(10)

        assert limiter.get_window_stats(limit)[1] == 0
        assert limiter.hit(limit) is False

        timeline.forward(20)
        assert limiter.get_window_stats(limit)[1] == 2
        assert limiter.get_window_stats(limit)[0] == int(time.time() + 30)

        timeline.forward(31)
        assert limiter.get_window_stats(limit)[1] == 10


def test_test_fixed_window(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with hiro.Timeline().freeze():
        limit = RateLimitItemPerSecond(2, 1)

        assert limiter.hit(limit) is True
        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is False
        assert limiter.hit(limit) is False


def test_test_moving_window(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    with hiro.Timeline().freeze():
        limit = RateLimitItemPerSecond(2, 1)

        assert limiter.hit(limit) is True
        assert limiter.test(limit) is True
        assert limiter.hit(limit) is True
        assert limiter.test(limit) is False
        assert limiter.hit(limit) is False
