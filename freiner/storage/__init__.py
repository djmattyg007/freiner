from typing import Protocol, Tuple

from freiner.errors import FreinerConfigurationError
from .memory import MemoryStorage


# When support for python3.7 is dropped, @runtime_checkable should be added to this
class Storage(Protocol):
    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        increments the counter for a given rate limit key

        :param str key: the key to increment
        :param int expiry: amount in seconds for the key to expire in
        :param bool elastic_expiry: whether to keep extending the rate limit
         window every hit.
        """

    def get(self, key: str) -> int:
        """
        :param str key: the key to get the counter value for
        """

    def get_expiry(self, key: str) -> int:
        """
        :param str key: the key to get the expiry for
        """

    def check(self) -> bool:
        """
        check if storage is healthy
        """

    def reset(self):
        """
        reset storage to clear limits
        """

    def clear(self, key: str):
        """
        resets the rate limit key
        :param str key: the key to clear rate limits for
        """

class MovingWindowStorage(Storage):
    def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
        """
        :param str key: rate limit key to acquire an entry in
        :param int limit: amount of entries allowed
        :param int expiry: expiry of the entry
        :param bool no_add: if False an entry is not actually acquired
         but instead serves as a 'check'
        :rtype: bool
        """

    def get_moving_window(self, key: str, limit: int, expiry) -> Tuple[int, int]:
        """
        returns the starting point and the number of entries in the moving window

        :param str key: rate limit key
        :param int limit: amount of entries allowed
        :param int expiry: expiry of entry
        :return: (start of window, number of acquired entries)
        """

__all__ = [
    "FreinerConfigurationError",
    "Storage",
    "MovingWindowStorage",
    "MemoryStorage",
]
