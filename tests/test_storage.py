import re
import time

import pytest

from freiner.strategies import MovingWindowRateLimiter


def test_pluggable_storage_no_moving_window():
    class MyStorage:
        def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
            return 1

        def get(self, key: str) -> int:
            return 0

        def get_expiry(self, key: str) -> int:
            return int(time.time())

    storage = MyStorage()

    errmsg = re.escape("MovingWindowRateLimiting is not implemented for storage of type MyStorage")
    with pytest.raises(TypeError, match=errmsg):
        # Ignore the type error here because that's exactly what we're testing for.
        MovingWindowRateLimiter(storage)  # type: ignore


def test_pluggable_storage_moving_window():
    class MyStorage:
        def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
            return 1

        def get(self, key: str) -> int:
            return 0

        def get_expiry(self, key: str) -> int:
            return int(time.time())

        def check(self) -> bool:
            return True

        def clear(self, key: str):
            pass

        def reset(self):
            pass

        def acquire_entry(self, *a, **k) -> bool:
            return True

        def get_moving_window(self, *a, **k):
            return time.time(), 1

    storage = MyStorage()
    strategy = MovingWindowRateLimiter(storage)
    assert strategy.storage is storage
