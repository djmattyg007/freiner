.. currentmodule:: freiner

=======================
Custom storage backends
=======================

The **Freiner** package ships with a few built-in storage implementations which allow you
to get started with some common data stores (redis & memcached) used for rate limiting.

Creating your own storage backend is relatively straightforward. Each type of strategy
(fixed-window and moving-window) has its own storage requirements, and a storage backend
can easily support both at the same time.

Fixed Window Storage
====================

You need to fulfil the contract set out by :class:`freiner.storage.FixedWindowStorage`.
This is a :py:class:`typing.Protocol` class, so you don't need to extend it.

The following example shows a fixed-window storage backend.::

    class MyFixedWindowStorage:
        def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
            return 1

        def get(self, key: str) -> int:
            return 0

        def get_expiry(self, key: str) -> int:
            return -1

        def clear(self, key: str):
            pass

Moving Window Storage
=====================

You need to fulfil the contract set out by :class:`freiner.storage.MovingWindowStorage`.
This is a :py:class:`typing.Protocol` class, so you don't need to extend it.

The following example shows a moving-window storage backend.::

    class MyMovingWindowStorage:
        def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
            return True

        def get_moving_window(self, key: str, limit: int, expiry: int) -> Tuple[float, int]:
            return time.time(), 0

        def clear(self, key: str):
            pass
