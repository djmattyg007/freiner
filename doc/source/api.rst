.. currentmodule:: freiner

API
---

Storage
=======

======================
Abstract storage class
======================

.. autoclass:: freiner.storage.Storage

.. _storage-backend-implementations:

=======================
Backend Implementations
=======================

In-Memory
^^^^^^^^^

.. autoclass:: freiner.storage.MemoryStorage

Redis
^^^^^

.. autoclass:: freiner.storage.redis.RedisStorage

Redis Sentinel
^^^^^^^^^^^^^^

.. autoclass:: freiner.storage.redis_sentinel.RedisSentinelStorage

Redis Cluster
^^^^^^^^^^^^^

.. autoclass:: freiner.storage.redis_cluster.RedisClusterStorage

Memcached
^^^^^^^^^

.. autoclass:: freiner.storage.memcached.MemcachedStorage

Strategies
==========

.. autoclass:: freiner.strategies.RateLimiter
.. autoclass:: freiner.strategies.FixedWindowRateLimiter
.. autoclass:: freiner.strategies.FixedWindowElasticExpiryRateLimiter
.. autoclass:: freiner.strategies.MovingWindowRateLimiter

Rate Limits
===========

========================
Rate Limit Granularities
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

