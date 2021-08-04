Freiner Documentation
--------------------

**Freiner** provides utilities to implement rate limiting using various strategies
and storage backends such as redis & memcached.

.. toctree::
    :hidden:

    string-notation
    custom-storage
    storage
    strategies
    api
    changelog

.. currentmodule:: freiner

Quickstart
----------

Initialize the storage backend::

    from freiner import storage
    memory_storage = storage.MemoryStorage()

Initialize a rate limiter with the :ref:`moving-window` strategy::

    from freiner import strategies
    moving_window = strategies.MovingWindowRateLimiter(memory_storage)

Initialize a rate limit using the :ref:`ratelimit-string`::

    from freiner import parse
    one_per_minute = parse("1/minute")

Initialize a rate limit explicitly using a subclass of :class:`RateLimitItem`::

    from freiner import RateLimitItemPerSecond
    one_per_second = RateLimitItemPerSecond(1, 1)

Test the limits::

    assert moving_window.hit(one_per_minute, "test_namespace", "foo") == True
    assert moving_window.hit(one_per_minute, "test_namespace", "foo") == False
    assert moving_window.hit(one_per_minute, "test_namespace", "bar") == True

    assert moving_window.hit(one_per_second, "test_namespace", "foo") == True
    assert moving_window.hit(one_per_second, "test_namespace", "foo") == False
    time.sleep(1)
    assert moving_window.hit(one_per_second, "test_namespace", "foo") == True

Check specific limits without hitting them::

    assert moving_window.hit(one_per_second, "test_namespace", "foo") == True
    while not moving_window.test(one_per_second, "test_namespace", "foo"):
        time.sleep(0.01)
    assert moving_window.hit(one_per_second, "test_namespace", "foo") == True

Clear a limit::

    assert moving_window.hit(one_per_minute, "test_namespace", "foo") == True
    assert moving_window.hit(one_per_minute, "test_namespace", "foo") == False
    moving_window.clear(one_per_minute", "test_namespace", "foo")
    assert moving_window.hit(one_per_minute, "test_namespace", "foo") == True

Development
-----------

Since `Freiner` integrates with various backend storages, local development and running tests
can require some setup. These are all scaffolded using ``docker`` and ``docker-compose``. Everything
should be started and stopped automatically when running tests::

    invoke test

References
----------

* `Redis rate limiting pattern #2 <https://redis.io/commands/INCR>`_
* `DomainTools redis rate limiter <https://github.com/DomainTools/rate-limit>`_
