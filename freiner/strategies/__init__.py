from typing import NamedTuple

from typing_extensions import Protocol, runtime_checkable

from freiner.limits import RateLimitItem


class WindowStats(NamedTuple):
    reset_time: float
    remaining_count: int


@runtime_checkable
class RateLimiter(Protocol):
    def hit(self, item: RateLimitItem, *identifiers) -> bool:
        """
        Creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        :return: True/False
        """

    def test(self, item: RateLimitItem, *identifiers) -> bool:
        """
        Checks the rate limit and returns True if it is not currently exceeded.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        :return: True/False
        """

    def get_window_stats(self, item: RateLimitItem, *identifiers) -> WindowStats:
        """
        Returns the number of requests remaining within this limit.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        :return: tuple (reset time (float), remaining (int))
        """

    def clear(self, item: RateLimitItem, *identifiers):
        """
        Resets the request counter for a given limit to zero.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        """


__all__ = [
    "RateLimiter",
    "WindowStats",
]
