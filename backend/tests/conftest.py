"""Shared test fixtures.

Every date-sensitive test uses TODAY instead of the real clock so the suite
does not start failing as mock deadlines drift into the past.
"""

from datetime import date

import pytest

TODAY = date(2026, 9, 1)


@pytest.fixture
def today() -> date:
    return TODAY
