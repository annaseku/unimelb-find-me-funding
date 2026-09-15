"""Shared test fixtures.

Every date-sensitive test uses TODAY instead of the real clock so the suite
does not start failing as mock deadlines drift into the past.
"""

from datetime import date

import pytest

from backend.crawler.storage import init_db, save_opportunity
from backend.normaliser.pipeline import normalise_database
from backend.normaliser.rules import load_fixture_rows

TODAY = date(2026, 9, 1)


@pytest.fixture
def today() -> date:
    return TODAY


def _row_fields(row) -> dict:
    return {
        "title": row.title,
        "raw_text": row.raw_text,
        "deadline_raw": row.deadline_raw,
        "deadline_parsed": row.deadline_parsed,
        "funding_amount_raw": row.funding_amount_raw,
        "eligibility_snippet": row.eligibility_snippet,
    }


@pytest.fixture
def normalised_sqlite_db(tmp_path):
    """A crawler database whose rows have been through the normaliser.

    Shared by the SQLite and Postgres repository tests: both need the same
    starting point, one to serve from it and one to copy out of it.
    """
    db = tmp_path / "crawler.db"
    init_db(str(db))
    for row in load_fixture_rows():
        save_opportunity(row.url, _row_fields(row), row.source_query or "", db_path=str(db))
    normalise_database(db, TODAY)
    return db
