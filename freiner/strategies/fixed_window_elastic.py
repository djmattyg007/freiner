from typing import Any

from freiner.limits import RateLimitItem

from .fixed_window import FixedWindowRateLimiter


class FixedWindowElasticExpiryRateLimiter(FixedWindowRateLimiter):
    """
    Reference: :ref:`fixed-window-elastic`
    """

    def hit(self, item: RateLimitItem, *identifiers: Any) -> bool:
        """
        creates a hit on the rate limit and returns True if successful.

        :param item: a :class:`freiner.limits.RateLimitItem` instance
        :param identifiers: variable list of strings to uniquely identify the limit
        :return: True/False
        """

        counter = self.storage.incr(
            item.key_for(*identifiers), item.get_expiry(), elastic_expiry=True
        )
        return counter <= item.amount


__all__ = [
    "FixedWindowElasticExpiryRateLimiter",
]
