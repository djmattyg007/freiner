.. currentmodule:: freiner

===
API
===

Rate Limits
===========

Rate Limit Granularities
------------------------

.. autoclass:: freiner.limits.RateLimitItem
.. autoclass:: freiner.limits.RateLimitItemPerYear
.. autoclass:: freiner.limits.RateLimitItemPerMonth
.. autoclass:: freiner.limits.RateLimitItemPerDay
.. autoclass:: freiner.limits.RateLimitItemPerHour
.. autoclass:: freiner.limits.RateLimitItemPerMinute
.. autoclass:: freiner.limits.RateLimitItemPerSecond

Utility Methods
---------------

.. autofunction:: parse
.. autofunction:: parse_many

Strategies
==========

.. autoclass:: freiner.strategies.RateLimiter
.. autoclass:: freiner.strategies.WindowStats
.. autoclass:: freiner.strategies.fixed_window.FixedWindowRateLimiter
.. autoclass:: freiner.strategies.fixed_window_elastic.FixedWindowElasticExpiryRateLimiter
.. autoclass:: freiner.strategies.moving_window.MovingWindowRateLimiter

Storage
=======

Storage Protocol Classes
------------------------

.. autoclass:: freiner.storage.FixedWindowStorage
.. autoclass:: freiner.storage.MovingWindow
.. autoclass:: freiner.storage.MovingWindowStorage

.. _storage-backend-implementations:

Backend Implementations
-----------------------

In-Memory
^^^^^^^^^

.. autoclass:: freiner.storage.memory.MemoryStorage

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

Exceptions
==========

.. autoexception:: freiner.errors.FreinerConfigurationError

