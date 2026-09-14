"""Tests for backend.data.sqlite_repository.SqliteRepository: serving
normalised opportunities out of a crawler database through the same
repository interface the mock-backed repository already implements."""

from __future__ import annotations

import pytest

from backend.crawler.storage import init_db, save_opportunity
from backend.data.sqlite_repository import SqliteRepository
from backend.normaliser.pipeline import normalise_database
from backend.normaliser.rules import load_fixture_rows
from backend.tests.conftest import TODAY


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
def normalised_db(tmp_path):
    db = tmp_path / "crawler.db"
    init_db(str(db))
    for row in load_fixture_rows():
        save_opportunity(row.url, _row_fields(row), row.source_query or "", db_path=str(db))
    normalise_database(db, TODAY)
    return db


def test_repository_serves_every_normalised_opportunity(normalised_db):
    repo = SqliteRepository(normalised_db)
    assert len(repo.all()) == 5


def test_get_returns_a_normalised_opportunity_by_id(normalised_db):
    repo = SqliteRepository(normalised_db)
    some_id = repo.all()[0].id
    found = repo.get(some_id)
    assert found is not None
    assert found.id == some_id


def test_get_returns_none_for_an_unknown_id(normalised_db):
    repo = SqliteRepository(normalised_db)
    assert repo.get("does-not-exist") is None


def test_missing_normalised_table_yields_an_empty_repository(tmp_path):
    db = tmp_path / "empty.db"
    init_db(str(db))  # only the crawler's own table exists; nothing normalised yet
    repo = SqliteRepository(db)
    assert repo.all() == []
