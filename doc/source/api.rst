.. currentmodule:: freiner

API
----

Storage
=======

======================
Abstract storage class
======================
.. autoclass:: freiner.storage.Storage

.. _backend-implementation:

=======================
Backend Implementations
=======================

In-Memory
^^^^^^^^^
.. autoclass:: freiner.storage.MemoryStorage

Redis
^^^^^
.. autoclass:: freiner.storage.RedisStorage

Redis Cluster
^^^^^^^^^^^^^
.. autoclass:: freiner.storage.RedisClusterStorage

Redis Sentinel
^^^^^^^^^^^^^^
.. autoclass:: freiner.storage.RedisSentinelStorage

Memcached
^^^^^^^^^
.. autoclass:: freiner.storage.MemcachedStorage

Strategies
==========
.. autoclass:: freiner.strategies.RateLimiter
.. autoclass:: freiner.strategies.FixedWindowRateLimiter
.. autoclass:: freiner.strategies.FixedWindowElasticExpiryRateLimiter
.. autoclass:: freiner.strategies.MovingWindowRateLimiter

Rate Limits
===========

========================
Rate limit granularities
========================

.. autoclass:: RateLimitItem
.. autoclass:: RateLimitItemPerYear
.. autoclass:: RateLimitItemPerMonth
.. autoclass:: RateLimitItemPerDay
.. autoclass:: RateLimitItemPerHour
.. autoclass:: RateLimitItemPerMinute
.. autoclass:: RateLimitItemPerSecond

===============
Utility Methods
===============
.. autofunction:: parse
.. autofunction:: parse_many


Exceptions
==========
.. autoexception:: freiner.errors.FreinerConfigurationError

