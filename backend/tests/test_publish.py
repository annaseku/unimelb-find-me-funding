"""Tests for backend.data.publish that need no database: the mock records'
content hashes and the command-line entry point. Writing to Postgres is
tested against a real one in test_postgres_repository.py."""

from __future__ import annotations

import pytest

from backend.data import publish as publish_module
from backend.data.publish import main, records_from_mock, records_from_sqlite


@pytest.fixture
def published(monkeypatch):
    """Capture what main() would write, so the CLI's argument handling can be
    tested without a database."""
    calls = []

    def fake_publish(database_url, records):
        calls.append((database_url, records))
        return len(records)

    monkeypatch.setattr(publish_module, "publish", fake_publish)
    return calls


def test_mock_hashes_are_stable_so_republishing_unchanged_data_is_a_no_op():
    first = [r.content_hash for r in records_from_mock()]
    second = [r.content_hash for r in records_from_mock()]
    assert first == second


def test_every_mock_opportunity_gets_its_own_hash():
    hashes = [r.content_hash for r in records_from_mock()]
    assert len(set(hashes)) == len(hashes)


def test_main_refuses_to_run_without_a_database_url(monkeypatch, published, capsys):
    monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    with pytest.raises(SystemExit) as exit_info:
        main(["--source", "mock"])
    assert exit_info.value.code == 2
    assert "no database URL" in capsys.readouterr().err
    assert published == []


def test_main_reads_the_url_from_the_environment(monkeypatch, published, capsys):
    monkeypatch.setenv("FMF_DATABASE_URL", "postgresql://env-url")
    assert main(["--source", "mock"]) == 0

    url, records = published[0]
    assert url == "postgresql://env-url"
    assert len(records) == len(records_from_mock())
    assert f"published {len(records)} opportunities from mock" in capsys.readouterr().out


def test_main_publishes_a_crawler_database_with_source_sqlite(published, normalised_sqlite_db):
    main(
        [
            "--source",
            "sqlite",
            "--db-path",
            str(normalised_sqlite_db),
            "--database-url",
            "postgresql://flag-url",
        ]
    )

    url, records = published[0]
    assert url == "postgresql://flag-url"
    expected = {r.opportunity.id for r in records_from_sqlite(normalised_sqlite_db)}
    assert {r.opportunity.id for r in records} == expected
