import pytest

from freiner import limits
from freiner.util import granularity_from_string, parse, parse_many


@pytest.mark.parametrize("rl_string", ("1 per second", "1/SECOND", "1 / Second"))
def test_single_seconds(rl_string: str):
    assert parse(rl_string) == limits.RateLimitItemPerSecond(1)


@pytest.mark.parametrize("rl_string", ("1 per minute", "1/MINUTE", "1/Minute"))
def test_single_minutes(rl_string: str):
    assert parse(rl_string) == limits.RateLimitItemPerMinute(1)


@pytest.mark.parametrize("rl_string", ("1 per hour", "1/HOUR", "1/Hour"))
def test_single_hours(rl_string: str):
    assert parse(rl_string) == limits.RateLimitItemPerHour(1)


@pytest.mark.parametrize("rl_string", ("1 per day", "1/DAY", "1 / Day"))
def test_single_days(rl_string: str):
    assert parse(rl_string) == limits.RateLimitItemPerDay(1)


@pytest.mark.parametrize("rl_string", ("1 per month", "1/MONTH", "1 / Month"))
def test_single_months(rl_string: str):
    assert parse(rl_string) == limits.RateLimitItemPerMonth(1)


@pytest.mark.parametrize("rl_string", ("1 per year", "1/Year", "1 / year"))
def test_single_years(rl_string: str):
    assert parse(rl_string) == limits.RateLimitItemPerYear(1)


def test_multiples():
    assert parse("1 per 3 hour").get_expiry() == 3 * 60 * 60
    assert parse("1 per 2 hours").get_expiry() == 2 * 60 * 60
    assert parse("1/2 day").get_expiry() == 2 * 24 * 60 * 60


def test_parse_many():
    parsed = parse_many("1 per 3 hour; 1 per second")

    assert len(parsed) == 2

    assert parsed[0].amount == 1
    assert parsed[0].get_expiry() == 3 * 60 * 60

    assert parsed[1].amount == 1
    assert parsed[1].get_expiry() == 1


def test_parse_many_csv():
    parsed = parse_many("200 per 4 days, 5 per 2 minutes")

    assert len(parsed) == 2

    assert parsed[0].amount == 200
    assert parsed[0].get_expiry() == 4 * 24 * 60 * 60

    assert parsed[1].amount == 5
    assert parsed[1].get_expiry() == 2 * 60


def test_invalid_string():
    with pytest.raises(ValueError):
        parse(None)

    with pytest.raises(ValueError):
        parse("1 per millenium")

    with pytest.raises(ValueError):
        granularity_from_string("millenium")

    with pytest.raises(ValueError):
        parse_many("1 per year; 2 per decade")
