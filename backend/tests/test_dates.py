"""Deadline dates are read the way Australian funders write them."""

from datetime import date

import pytest

from backend.crawler.dates import parse_date_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("03/04/2026", date(2026, 4, 3)),
        ("Applications close 3 April 2026, 5pm AEST", date(2026, 4, 3)),
        ("April 3, 2026", date(2026, 4, 3)),
        ("2026-04-03", date(2026, 4, 3)),
        ("Closing date: 2026-04-03 at 17:00", date(2026, 4, 3)),
    ],
)
def test_slash_dates_are_day_first_and_iso_dates_are_read_as_written(text, expected):
    assert parse_date_text(text) == expected


@pytest.mark.parametrize("text", ["no date here", "2026-13-45", "Since 1987 we have funded"])
def test_text_without_a_plausible_date_gives_none(text):
    assert parse_date_text(text) is None
