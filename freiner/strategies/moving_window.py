from typing import Any

from freiner.limits import RateLimitItem
from freiner.storage import MovingWindowStorage

from . import WindowStats


class MovingWindowRateLimiter:
    """
    Reference: :ref:`moving-window`
    """

    def __init__(self, storage: MovingWindowStorage) -> None:
        if not isinstance(storage, MovingWindowStorage):
            msg = f"Moving Window rate limiting is not implemented for storage of type {storage.__class__.__name__}"
            raise TypeError(msg)

        self.storage: MovingWindowStorage = storage

    def hit(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Creates a hit on the rate limit and returns ``True`` if successful.

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the request was successful, or ``False`` if the rate limit had been exceeded.
        """

        return self.storage.acquire_entry(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )

    def test(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        Checks the rate limit and returns ``True`` if it is not currently exceeded.

        :param item: A :class:`freiner.limits.RateLimitItem` instance.
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: ``True`` if the rate limit has not yet been exceeded, or ``False`` if it has.
        """

        _, acquired_count = self.storage.get_moving_window(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )

        return acquired_count < item.amount

    def get_window_stats(self, item: RateLimitItem, *identifiers: Any) -> WindowStats:
        """
        Returns the number of requests remaining within this limit.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        :return: tuple (reset time (float), remaining (int))
        """

        window_start, window_items = self.storage.get_moving_window(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )
        reset = window_start + item.get_expiry()
        return WindowStats(reset, item.amount - window_items)

    def clear(self, item: RateLimitItem, *identifiers: Any) -> None:
        """
        Resets the request counter for a given limit to zero.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: A variable list of stringable objects to uniquely identify the limit.
        """

        self.storage.clear(item.key_for(*identifiers))


__all__ = [
    "MovingWindowRateLimiter",
]
