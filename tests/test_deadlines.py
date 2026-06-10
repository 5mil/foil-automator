import datetime
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from main import _add_business_days, init_db, add_request


def test_business_days_skip_weekend():
    # Friday + 5 business days = next Friday (skip sat/sun)
    fri = datetime.date(2026, 6, 5)  # Friday
    result = _add_business_days(fri, 5)
    assert result == datetime.date(2026, 6, 12), f"Expected 2026-06-12, got {result}"


def test_business_days_mid_week():
    mon = datetime.date(2026, 6, 1)  # Monday
    result = _add_business_days(mon, 5)
    assert result == datetime.date(2026, 6, 8)


def test_twenty_business_days():
    sub = datetime.date(2026, 6, 10)
    result = _add_business_days(sub, 20)
    assert result.weekday() < 5  # must land on a weekday
    assert result > sub
