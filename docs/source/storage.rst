.. currentmodule:: freiner

================
Storage Backends
================

In-Memory
=========

The in-memory storage (:class:`freiner.storage.memory.MemoryStorage`).

.. _redis:

Redis
=====

Requires the location of the redis server and optionally the database number.
:code:`redis://localhost:6379` or :code:`redis://localhost:6379/N` (for database `N`).

If the redis server is listening over a unix domain socket you can use :code:`unix:///path/to/sock`
or :code:`unix:///path/to/socket?db=N` (for database `N`).

If the database is password protected the password can be provided in the url, for example
:code:`redis://:foobared@localhost:6379` or :code:`unix//:foobered/path/to/socket` if using
a Unix domain socket (UDS).

Depends on: `redis-py <https://redis-py.readthedocs.io/>`_

.. _redis-ssl:

Redis over SSL
==============

Redis does not support SSL natively, but it is recommended to use stunnel to provide SSL suport.
The official Redis client :code:`redis-py` supports redis connections over SSL with the scheme
:code:`rediss`. :code:`rediss://localhost:6379/0` just like the normal redis connection, just
with the new scheme.

Depends on: `redis-py <https://redis-py.readthedocs.io/>`_

.. _redis-sentinel:

Redis with Sentinel
===================

Requires the location(s) of the redis sentinal instances and the `service-name`
that is monitored by the sentinels.
:code:`redis+sentinel://localhost:26379/my-redis-service`
or :code:`redis+sentinel://localhost:26379,localhost:26380/my-redis-service`.

If the database is password protected the password can be provided in the url, for example
:code:`redis+sentinel://:sekret@localhost:26379/my-redis-service`

Depends on: `redis-py <https://redis-py.readthedocs.io/>`_

.. _redis-cluster:

Redis Cluster
=============

The Redis Cluster storage backend is currently provided on a best-effort basis, and is
currently not covered by tests. Patches are welcome.

Requires the location(s) of the redis cluster startup nodes (One is enough).
:code:`redis+cluster://localhost:7000`
or :code:`redis+cluster://localhost:7000,localhost:70001`

Depends on: `redis-py-cluster <https://redis-py-cluster.readthedocs.io/>`_

.. _memcached:

Memcached
=========

Requires the location of the memcached server(s). As such
the parameters is a comma separated list of :code:`{host}:{port}` locations such as
:code:`memcached://localhost:11211` or
:code:`memcached://localhost:11211,localhost:11212,192.168.1.1:11211` etc...
or a path to a unix domain socket such as :code:`memcached:///var/tmp/path/to/sock`

Depends on: `pymemcache <https://pymemcache.readthedocs.io/>`__
