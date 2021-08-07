from typing import Any, NamedTuple

from typing_extensions import Protocol, runtime_checkable

from freiner.limits import RateLimitItem


class WindowStats(NamedTuple):
    reset_time: float
    remaining_count: int


@runtime_checkable
class RateLimiter(Protocol):
    def hit(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        :return: True/False
        """

    def test(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Checks the rate limit and returns True if it is not currently exceeded.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        :return: True/False
        """

    def get_window_stats(self, item: RateLimitItem, *identifiers: Any) -> WindowStats:
        """
        Returns the number of requests remaining within this limit.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        :return: tuple (reset time (float), remaining (int))
        """

    def clear(self, item: RateLimitItem, *identifiers: Any) -> None:
        """
        Resets the request counter for a given limit to zero.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of stringable objects to uniquely identify the limit
        """


__all__ = [
    "RateLimiter",
    "WindowStats",
]
