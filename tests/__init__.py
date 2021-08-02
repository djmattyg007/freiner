import functools
import math
import time


def fixed_start(fn):
    @functools.wraps(fn)
    def _inner(*args, **kwargs):
        start = time.time()
        while time.time() < math.ceil(start):
            time.sleep(0.01)
        return fn(*args, **kwargs)

    return _inner
