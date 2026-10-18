"""Tests for backend.data.sqlite_repository.SqliteRepository: serving
normalised opportunities out of a crawler database through the same
repository interface used by the API."""

from __future__ import annotations

import pytest

from backend.crawler.storage import init_db, save_opportunity
from backend.data.sqlite_repository import SqliteRepository
from backend.normaliser.llm import ExtractedFields, FakeExtractor
from backend.normaliser.pipeline import normalise_database
from backend.tests.conftest import TODAY


def test_repository_serves_every_normalised_opportunity(normalised_sqlite_db):
    repo = SqliteRepository(normalised_sqlite_db)
    assert len(repo.all()) == 5


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


def test_rule_only_summaries_counts_records_the_llm_did_not_summarise(normalised_sqlite_db):
    repo = SqliteRepository(normalised_sqlite_db)
    assert repo.rule_only_summaries == len(repo.all())
    assert repo.last_run.llm_stop_reason == "not_configured"


def test_an_llm_written_summary_is_not_counted_as_rule_only(tmp_path):
    db = tmp_path / "crawler.db"
    init_db(str(db))
    for n in range(2):
        save_opportunity(
            f"https://example.org/grant-{n}",
            {"title": f"Grant {n}", "raw_text": "Funds research."},
            "test",
            db_path=str(db),
        )
    normalise_database(db, TODAY, extractor=FakeExtractor(ExtractedFields(summary="AI summary.")))
    repo = SqliteRepository(db)
    assert repo.rule_only_summaries == 0
    assert repo.last_run.llm_calls == 2
