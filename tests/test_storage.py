import re
import time
from typing import Tuple

import pytest

from freiner.strategies import FixedWindowRateLimiter, MovingWindowRateLimiter


def test_pluggable_storage_fixed_window():
    class MyStorage:
        def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
            return 1

        def get(self, key: str) -> int:
            return 0

        def get_expiry(self, key: str) -> int:
            return int(time.time())

        def clear(self, key: str):
            pass

    storage = MyStorage()
    strategy = FixedWindowRateLimiter(storage)
    assert strategy.storage is storage

    errmsg = re.escape(
        "Moving Window rate limiting is not implemented for storage of type MyStorage"
    )
    with pytest.raises(TypeError, match=errmsg):
        # Ignore the type error here because that's exactly what we're testing for.
        MovingWindowRateLimiter(storage)  # type: ignore


def test_pluggable_storage_moving_window():
    class MyStorage:
        def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
            return True

        def get_moving_window(self, key: str, limit: int, expiry: int) -> Tuple[float, int]:
            return time.time(), 1

        def clear(self, key: str):
            pass

    storage = MyStorage()
    strategy = MovingWindowRateLimiter(storage)
    assert strategy.storage is storage

    errmsg = re.escape(
        "Fixed Window rate limiting is not implemented for storage of type MyStorage"
    )
    with pytest.raises(TypeError, match=errmsg):
        # Ignore the type error here because that's exactly what we're testing for.
        FixedWindowRateLimiter(storage)  # type: ignore
