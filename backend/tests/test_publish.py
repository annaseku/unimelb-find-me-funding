"""Tests for backend.data.publish that need no Postgres: the corpus records'
content hashes and the command-line entry point. Writing to Postgres is
tested against a real one in test_postgres_repository.py."""

# mutation-check: characterisation

from __future__ import annotations

import pytest

from backend.data import publish as publish_module
from backend.data.publish import PublishStats, main, records_from_sqlite
from backend.evals.corpus import corpus_records


@pytest.fixture
def published(monkeypatch):
    """Capture what main() would write, so the CLI's argument handling can be
    tested without a database."""
    calls = []

    def fake_publish(database_url, records, rejected_urls=()):
        calls.append((database_url, records, list(rejected_urls)))
        return PublishStats(published=len(records), removed=0)

    monkeypatch.setattr(publish_module, "publish", fake_publish)
    return calls


def test_corpus_hashes_are_stable_so_republishing_unchanged_data_is_a_no_op():
    first = [r.content_hash for r in corpus_records()]
    second = [r.content_hash for r in corpus_records()]
    assert first == second


def test_every_corpus_opportunity_gets_its_own_hash():
    hashes = [r.content_hash for r in corpus_records()]
    assert len(set(hashes)) == len(hashes)


def test_main_refuses_to_run_without_a_database_url(monkeypatch, published, capsys):
    monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    with pytest.raises(SystemExit) as exit_info:
        main([])
    assert exit_info.value.code == 2
    assert "no database URL" in capsys.readouterr().err
    assert published == []


def test_main_reads_the_url_from_the_environment(monkeypatch, published, capsys, corpus_db):
    monkeypatch.setenv("FMF_DATABASE_URL", "postgresql://env-url")
    assert main(["--db-path", str(corpus_db)]) == 0

    url, records, _ = published[0]
    assert url == "postgresql://env-url"
    assert len(records) == len(corpus_records())
    assert f"published {len(records)} opportunities from {corpus_db}" in capsys.readouterr().out


def test_main_publishes_a_crawler_database(published, normalised_sqlite_db):
    main(
        [
            "--db-path",
            str(normalised_sqlite_db),
            "--database-url",
            "postgresql://flag-url",
        ]
    )

    url, records, rejected_urls = published[0]
    assert url == "postgresql://flag-url"
    expected = {r.opportunity.id for r in records_from_sqlite(normalised_sqlite_db)}
    assert {r.opportunity.id for r in records} == expected
    assert rejected_urls == ["https://www.example-news.org/2026/07/university-announces-new-lab"]


def test_main_uses_the_default_crawler_database(monkeypatch, published, capsys, tmp_path):
    from backend.evals.seed_sqlite import seed

    monkeypatch.chdir(tmp_path)
    seed("funding_crawler.db")
    assert main(["--database-url", "postgresql://flag-url"]) == 0
    assert len(published[0][1]) == 30
    assert capsys.readouterr().out == (
        "published 30 opportunities from funding_crawler.db\n"
        "removed 0 that are not funding opportunities\n"
    )


def test_main_rejects_the_removed_source_argument(published, capsys):
    with pytest.raises(SystemExit) as error:
        main(["--source", "mock", "--database-url", "postgresql://flag-url"])
    assert error.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
    assert published == []
