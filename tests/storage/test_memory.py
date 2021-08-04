import time

import hiro
import pytest

from freiner import RateLimitItemPerMinute, RateLimitItemPerSecond
from freiner.storage import MemoryStorage
from freiner.strategies import FixedWindowRateLimiter, MovingWindowRateLimiter


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


def test_in_memory(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    with hiro.Timeline().freeze() as timeline:
        per_min = RateLimitItemPerMinute(10)

        for _ in range(0, 10):
            assert limiter.hit(per_min) is True
        assert limiter.hit(per_min) is False

        timeline.forward(61)
        assert limiter.hit(per_min) is True


def test_fixed_window_clear(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    per_min = RateLimitItemPerMinute(1)

    assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False

    limiter.clear(per_min)
    assert limiter.hit(per_min) is True


def test_moving_window_clear(storage: MemoryStorage):
    limiter = MovingWindowRateLimiter(storage)
    per_min = RateLimitItemPerMinute(1)

    assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False

    limiter.clear(per_min)
    assert limiter.hit(per_min) is True


def test_reset(storage: MemoryStorage):
    limiter = FixedWindowRateLimiter(storage)
    per_min = RateLimitItemPerMinute(10)

    for _ in range(0, 10):
        assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False

    storage.reset()
    for _ in range(0, 10):
        assert limiter.hit(per_min) is True
    assert limiter.hit(per_min) is False


def test_expiry(storage: MemoryStorage):
    with hiro.Timeline().freeze() as timeline:
        limiter = FixedWindowRateLimiter(storage)
        per_min = RateLimitItemPerMinute(10)
        for _ in range(0, 10):
            assert limiter.hit(per_min) is True

        timeline.forward(60)
        # touch another key and yield
        limiter.hit(RateLimitItemPerSecond(1))
        time.sleep(0.1)
        assert per_min.key_for() not in storage.storage


def test_expiry_moving_window(storage: MemoryStorage):
    with hiro.Timeline().freeze() as timeline:
        limiter = MovingWindowRateLimiter(storage)
        per_min = RateLimitItemPerMinute(10)
        per_sec = RateLimitItemPerSecond(1)

        for _ in range(0, 2):
            for _ in range(0, 10):
                assert limiter.hit(per_min) is True

            timeline.forward(60)
            assert limiter.hit(per_sec) is True

            timeline.forward(1)
            time.sleep(0.1)
            assert storage.events[per_min.key_for()] == []
