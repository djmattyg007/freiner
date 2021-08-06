.. currentmodule:: freiner

Custom storage backends
-----------------------

TODO: This section is out of date. Gotta re-word it to discuss the Protocol classes.

The **Freiner** package ships with a few built-in storage implementations which allow you
to get started with some common data stores (redis & memcached) used for rate limiting.

Creating your own storage backend is relatively straightforward. The most important thing
is to fulfil the contract set out by :class:`freiner.storage.Storage`. This is a
:class:`typing.Protocol` class, so you don't need to extend it.

Examples
=======

The following example shows a simple storage backend.::

    class AwesomeStorage:
        def get(self, key: str) -> int:
            return 0

        def get_expiry(self, key: str) -> int:
            return -1

        def check(self) -> bool:
            return True

        def clear(self, key: str):
            pass

        def reset(self):
            pass

If you want to make use of the :ref:`moving-window` strategy, you'll need to implement
a couple of additional methods. These are detailed in the :class:`freiner.storage.MovingWindowStorage`
:class:`typing.Protocol` class.::

    class MovingAwesomeStorage(AwesomeStorage):
        def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
            return True

        def get_moving_window(self, key: str, limit: int, expiry: int) -> Tuple[int, int]:
            return int(time.time()), 0
