import functools
import math
import time


def fixed_start(fn):
    @functools.wraps(fn)
    def __inner(*a, **k):
        start = time.time()
        while time.time() < math.ceil(start):
            time.sleep(0.01)
        return fn(*a, **k)
    return __inner
