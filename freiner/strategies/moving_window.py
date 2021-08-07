from freiner.limits import RateLimitItem
from freiner.storage import MovingWindowStorage

from . import WindowStats


class MovingWindowRateLimiter:
    """
    Reference: :ref:`moving-window`
    """

    def __init__(self, storage: MovingWindowStorage):
        if not isinstance(storage, MovingWindowStorage):
            msg = f"Moving Window rate limiting is not implemented for storage of type {storage.__class__.__name__}"
            raise TypeError(msg)

        self.storage: MovingWindowStorage = storage

    def hit(self, item: RateLimitItem, *identifiers) -> bool:
        """
        creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """
        return self.storage.acquire_entry(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )

    def test(self, item: RateLimitItem, *identifiers) -> bool:
        """
        checks  the rate limit and returns True if it is not
        currently exceeded.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """

        _, acquired_count = self.storage.get_moving_window(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )

        return acquired_count < item.amount

    def get_window_stats(self, item: RateLimitItem, *identifiers) -> WindowStats:
        """
        returns the number of requests remaining within this limit.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: tuple (reset time (float), remaining (int))
        """
        window_start, window_items = self.storage.get_moving_window(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )
        reset = window_start + item.get_expiry()
        return WindowStats(reset, item.amount - window_items)

    def clear(self, item: RateLimitItem, *identifiers) -> None:
        self.storage.clear(item.key_for(*identifiers))


__all__ = [
    "MovingWindowRateLimiter",
]
