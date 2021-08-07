from typing import NamedTuple

from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FixedWindowStorage(Protocol):
    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        Increments the counter for a given rate limit key.

        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        :param bool elastic_expiry: whether to keep extending the rate limit
         window every hit.
        """

    def get(self, key: str) -> int:
        """
        :param str key: the key to get the counter value for
        """

    def get_expiry(self, key: str) -> float:
        """
        :param str key: the key to get the expiry for
        """

    def clear(self, key: str):
        """
        Resets the rate limit key.

        :param str key: the key to clear rate limits for
        """


class MovingWindow(NamedTuple):
    start_time: float
    acquired_count: int


@runtime_checkable
class MovingWindowStorage(Protocol):
    def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
        """
        :param str key: rate limit key to acquire an entry in
        :param int limit: amount of entries allowed
        :param int expiry: expiry of the entry
        :param bool no_add: if False an entry is not actually acquired
         but instead serves as a 'check'
        :rtype: bool
        """

    def get_moving_window(self, key: str, limit: int, expiry: int) -> MovingWindow:
        """
        Returns the starting point and the number of entries in the moving window.

        :param str key: rate limit key
        :param int limit: amount of entries allowed
        :param int expiry: expiry of entry
        :return: (start of window, number of acquired entries)
        """

    def clear(self, key: str):
        """
        Resets the rate limit key.

        :param str key: the key to clear rate limits for
        """


__all__ = [
    "FixedWindowStorage",
    "MovingWindow",
    "MovingWindowStorage",
    "MemoryStorage",
]
