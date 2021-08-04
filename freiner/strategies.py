"""
rate limiting strategies
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from .limits import RateLimitItem
from .storage import MovingWindowStorage, Storage


class RateLimiter(metaclass=ABCMeta):
    def __init__(self, storage: Storage):
        self.storage: Storage = storage

    @abstractmethod
    def hit(self, item: RateLimitItem, *identifiers) -> bool:
        """
        creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """
        raise NotImplementedError

    @abstractmethod
    def test(self, item: RateLimitItem, *identifiers) -> bool:
        """
        checks  the rate limit and returns True if it is not
        currently exceeded.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """
        raise NotImplementedError

    @abstractmethod
    def get_window_stats(self, item: RateLimitItem, *identifiers):
        """
        returns the number of requests remaining and reset of this limit.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: tuple (reset time (int), remaining (int))
        """
        raise NotImplementedError

    def clear(self, item: RateLimitItem, *identifiers):
        return self.storage.clear(item.key_for(*identifiers))


class MovingWindowRateLimiter(RateLimiter):
    """
    Reference: :ref:`moving-window`
    """

    def __init__(self, storage: MovingWindowStorage):
        if not isinstance(storage, MovingWindowStorage):
            msg = f"MovingWindowRateLimiting is not implemented for storage of type {storage.__class__.__name__}"
            raise TypeError(msg)

        super().__init__(storage)
        if TYPE_CHECKING:
            self.storage: MovingWindowStorage = storage

    def hit(self, item: RateLimitItem, *identifiers) -> bool:
        """
        creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`RateLimitItem` instance
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

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """

        _, acquired_count = self.storage.get_moving_window(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )

        return acquired_count < item.amount

    def get_window_stats(self, item: RateLimitItem, *identifiers):
        """
        returns the number of requests remaining within this limit.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: tuple (reset time (int), remaining (int))
        """
        window_start, window_items = self.storage.get_moving_window(
            item.key_for(*identifiers), item.amount, item.get_expiry()
        )
        reset = window_start + item.get_expiry()
        return reset, item.amount - window_items


class FixedWindowRateLimiter(RateLimiter):
    """
    Reference: :ref:`fixed-window`
    """

    def hit(self, item: RateLimitItem, *identifiers) -> bool:
        """
        creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """
        return self.storage.incr(item.key_for(*identifiers), item.get_expiry()) <= item.amount

    def test(self, item: RateLimitItem, *identifiers) -> bool:
        """
        checks  the rate limit and returns True if it is not
        currently exceeded.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """
        return self.storage.get(item.key_for(*identifiers)) < item.amount

    def get_window_stats(self, item: RateLimitItem, *identifiers):
        """
        returns the number of requests remaining and reset of this limit.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: tuple (reset time (int), remaining (int))
        """
        remaining = max(0, item.amount - self.storage.get(item.key_for(*identifiers)))
        reset = self.storage.get_expiry(item.key_for(*identifiers))
        return reset, remaining


class FixedWindowElasticExpiryRateLimiter(FixedWindowRateLimiter):
    """
    Reference: :ref:`fixed-window-elastic`
    """

    def hit(self, item: RateLimitItem, *identifiers) -> bool:
        """
        creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """

        counter = self.storage.incr(
            item.key_for(*identifiers), item.get_expiry(), elastic_expiry=True
        )
        return counter <= item.amount
