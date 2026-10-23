"""Read deadline dates the way Australian funders write them."""

from __future__ import annotations

import re
from datetime import date, datetime

from dateutil import parser as dateutil_parser

_ISO_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")

# A fuzzy parse can grab a stray number as the year; outside this range it is a misparse.
_EARLIEST_YEAR = 2020
_LATEST_YEAR = 2100


def parse_date_text(text: str) -> date | None:
    """Return the date in `text`, or None.

    ISO dates are read as written. Everything else is read day first, so 03/04/2026 is
    3 April; dateutil's dayfirst flag alone would also flip 2026-04-03 to 4 March.
    """
    iso = _ISO_RE.search(text)
    try:
        if iso:
            parsed = date(*(int(part) for part in iso.groups()))
        else:
            parsed = dateutil_parser.parse(
                text, fuzzy=True, dayfirst=True, default=datetime(1900, 1, 1)
            ).date()
    except (ValueError, OverflowError):
        return None
    return parsed if _EARLIEST_YEAR <= parsed.year <= _LATEST_YEAR else None
