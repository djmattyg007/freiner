import re
from typing import Sequence, Type, cast

from .limits import GRANULARITIES, RateLimitItem


# TODO: Remove {1}
SEPARATORS = re.compile(r"[,;|]{1}")
# TODO: Mark second group as non-capturing, adjust parse_many to remove _ variable
SINGLE_EXPR = re.compile(
    r"""
    \s*([0-9]+)
    \s*(/|\s*per\s*)
    \s*([0-9]+)
    *\s*(hour|minute|second|day|month|year)s?\s*""",
    re.IGNORECASE | re.VERBOSE,
)
EXPR = re.compile(
    r"^{SINGLE}(:?{SEPARATORS}{SINGLE})*$".format(
        SINGLE=SINGLE_EXPR.pattern, SEPARATORS=SEPARATORS.pattern
    ),
    re.IGNORECASE | re.VERBOSE,
)


def parse_many(limit_string: str) -> Sequence[RateLimitItem]:
    """
    parses rate limits in string notation containing multiple rate limits
    (e.g. '1/second; 5/minute')

    :param string limit_string: rate limit string using :ref:`ratelimit-string`
    :raise ValueError: if the string notation is invalid.
    :return: a list of :class:`RateLimitItem` instances.
    """
    if not isinstance(limit_string, str):
        raise TypeError("Invalid rate limit string supplied.")

    if not EXPR.match(limit_string):
        raise ValueError(f"Failed to parse rate limit string: {limit_string}")

    limits = []
    for limit in SEPARATORS.split(limit_string):
        # This cast is fine because we already verified that it will match
        # in the EXPR.match check above.
        limit_match = cast(re.Match, SINGLE_EXPR.match(limit))
        amount, _, multiples, granularity_string = limit_match.groups()
        granularity = granularity_from_string(granularity_string)
        limits.append(granularity(amount, multiples))

    return tuple(limits)


def parse(limit_string: str) -> RateLimitItem:
    """
    parses a single rate limit in string notation
    (e.g. '1/second' or '1 per second'

    :param string limit_string: rate limit string using :ref:`ratelimit-string`
    :raise ValueError: if the string notation is invalid.
    :return: an instance of :class:`RateLimitItem`
    """
    return parse_many(limit_string)[0]


def granularity_from_string(granularity_string: str) -> Type[RateLimitItem]:
    """
    :param granularity_string:
    :return: a subclass of :class:`RateLimitItem`
    :raise ValueError:
    """
    for granularity in GRANULARITIES.values():
        if granularity.check_granularity_string(granularity_string):
            return granularity

    raise ValueError(f"No granularity matched for: {granularity_string}")
