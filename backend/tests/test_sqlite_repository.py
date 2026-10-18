"""Tests for backend.data.sqlite_repository.SqliteRepository: serving
normalised opportunities out of a crawler database through the same
repository interface used by the API."""

from __future__ import annotations

import pytest

from backend.crawler.storage import init_db
from backend.data.sqlite_repository import SqliteRepository


def test_repository_serves_every_normalised_opportunity(normalised_sqlite_db):
    repo = SqliteRepository(normalised_sqlite_db)
    # Four of the five fixture rows; the normaliser drops the news page.
    assert len(repo.all()) == 4


def test_get_returns_a_normalised_opportunity_by_id(normalised_sqlite_db):
    repo = SqliteRepository(normalised_sqlite_db)
    some_id = repo.all()[0].id
    found = repo.get(some_id)
    assert found is not None
    assert found.id == some_id


def test_get_returns_none_for_an_unknown_id(normalised_sqlite_db):
    repo = SqliteRepository(normalised_sqlite_db)
    assert repo.get("does-not-exist") is None


def test_missing_normalised_table_yields_an_empty_repository(tmp_path):
    db = tmp_path / "empty.db"
    init_db(str(db))  # only the crawler's own table exists; nothing normalised yet
    repo = SqliteRepository(db)
    assert repo.all() == []


def test_missing_database_raises_without_creating_a_file(tmp_path):
    db = tmp_path / "missing.db"
    with pytest.raises(FileNotFoundError, match="no crawler database at") as error:
        SqliteRepository(db)
    assert str(db) in str(error.value)
    assert "python -m backend.evals.seed_sqlite" in str(error.value)
    assert "FMF_DATA_SOURCE=postgres" in str(error.value)
    assert not db.exists()
