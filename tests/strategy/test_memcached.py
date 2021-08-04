import threading
import time
import traceback
from typing import Tuple

import pymemcache
import pytest

from freiner.limits import RateLimitItemPerSecond
from freiner.storage.memcached import MemcachedStorage
from freiner.strategies import FixedWindowElasticExpiryRateLimiter, MovingWindowRateLimiter


Host = Tuple[str, int]


@pytest.fixture
def default_host() -> Host:
    return "localhost", 22122


@pytest.fixture
def client(default_host: Host) -> pymemcache.Client:
    return pymemcache.Client(default_host)


@pytest.fixture
def pooled_client(default_host: Host) -> pymemcache.PooledClient:
    return pymemcache.PooledClient(default_host)


@pytest.fixture(autouse=True)
def flush_default_host(client: pymemcache.Client):
    client.flush_all()


def test_fixed_window_with_elastic_expiry(client: pymemcache.Client):
    storage = MemcachedStorage(client)
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    limit = RateLimitItemPerSecond(10, 2)

    assert all([limiter.hit(limit) for _ in range(0, 10)]) is True

    time.sleep(1)
    assert limiter.hit(limit) is False

    time.sleep(1)
    assert limiter.hit(limit) is False


def test_fixed_window_with_elastic_expiry_concurrency(pooled_client: pymemcache.PooledClient):
    storage = MemcachedStorage(pooled_client)
    limiter = FixedWindowElasticExpiryRateLimiter(storage)
    limit = RateLimitItemPerSecond(10, 2)

    start = int(time.time())

    def _c():
        for _ in range(0, 5):
            try:
                limiter.hit(limit)
            except Exception:
                traceback.print_exc()
                raise

    t1 = threading.Thread(target=_c)
    t2 = threading.Thread(target=_c)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    window_stats = limiter.get_window_stats(limit)
    assert window_stats[1] == 0
    assert start + 2 <= window_stats[0] <= start + 3
    assert storage.get(limit.key_for()) == 10


def test_moving_window(client: pymemcache.Client):
    storage = MemcachedStorage(client)
    with pytest.raises(TypeError):
        # Ignore the type error here because that's exactly what we're testing for.
        MovingWindowRateLimiter(storage)  # type: ignore
