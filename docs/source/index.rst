=====================
Freiner Documentation
=====================

**Freiner** provides utilities to implement rate limiting using various strategies
and storage backends such as redis & memcached.

.. toctree::
    :hidden:

    string-notation
    strategies
    storage
    custom-storage
    api
    changelog

.. currentmodule:: freiner

Quickstart
==========

Initialize the storage backend::

    from freiner.storage import memory
    memory_storage = memory.MemoryStorage()

Initialize a rate limiter with the :ref:`moving-window` strategy::

    from freiner import strategies
    moving_window = strategies.MovingWindowRateLimiter(memory_storage)

Initialize a rate limit using the :ref:`ratelimit-string`::

    from freiner import parse
    one_per_minute = parse("1/minute")

Initialize a rate limit explicitly using a subclass of :class:`RateLimitItem`::

    from freiner import RateLimitItemPerSecond, RateLimitPerMinute
    one_per_second = RateLimitItemPerSecond(1, 1)
    ten_per_five_minutes = RateLimitPerMinute(10, 5)

Test the limits::

    ns = "test_namespace"
    assert moving_window.hit(one_per_minute, ns, "foo") == True
    assert moving_window.hit(one_per_minute, ns, "foo") == False
    assert moving_window.hit(one_per_minute, ns, "bar") == True

    assert moving_window.hit(one_per_second, ns, "foo") == True
    assert moving_window.hit(one_per_second, ns, "foo") == False
    time.sleep(1)
    assert moving_window.hit(one_per_second, ns, "foo") == True

Check specific limits without hitting them::

    assert moving_window.hit(one_per_second, ns, "foo") == True
    while not moving_window.test(one_per_second, ns, "foo"):
        time.sleep(0.01)
    assert moving_window.hit(one_per_second, ns, "foo") == True

Clear a limit::

    assert moving_window.hit(one_per_minute, ns, "foo") == True
    assert moving_window.hit(one_per_minute, ns, "foo") == False
    moving_window.clear(one_per_minute", ns, "foo")
    assert moving_window.hit(one_per_minute, ns, "foo") == True

Development
===========

Since `Freiner` integrates with various backend storages, local development and running tests
can require some setup. These are all scaffolded using ``docker`` and ``docker-compose``. Everything
should be started and stopped automatically when running tests::

    invoke test

References
----------

* `Redis rate limiting pattern #2 <https://redis.io/commands/INCR>`_
* `DomainTools redis rate limiter <https://github.com/DomainTools/rate-limit>`_
