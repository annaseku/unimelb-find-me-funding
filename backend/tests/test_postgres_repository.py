"""Tests for backend.data.postgres_repository and backend.data.publish:
serving normalised opportunities out of Postgres through the same repository
interface the SQLite repository implements.

These run against a real Postgres, never a fake, because the claim under test
is about what Postgres does with what we send (JSONB round-tripping, ON
CONFLICT upsert semantics, UndefinedTable on an unmigrated database). CI
provides one as a service container; locally, point FMF_TEST_DATABASE_URL at
any throwaway instance, for example:

    docker run -d --name fmf-test-pg -e POSTGRES_PASSWORD=test \\
        -e POSTGRES_DB=fmf_test -p 55432:5432 postgres:17-alpine
    export FMF_TEST_DATABASE_URL='postgresql://postgres:test@localhost:55432/fmf_test'
"""

from __future__ import annotations

import os

import psycopg
import pytest

from backend.data.postgres_repository import (
    PostgresRepository,
    init_schema,
    upsert_records,
)
from backend.data.publish import PublishStats, publish, records_from_sqlite
from backend.data.repository import get_repository
from backend.evals.corpus import corpus_records
from backend.normaliser.pipeline import NORMALISED_TABLE

DATABASE_URL = os.environ.get("FMF_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="set FMF_TEST_DATABASE_URL to run the Postgres repository tests",
)


@pytest.fixture
def database_url():
    """A schema-less database for one test: the table is dropped first so
    each test starts from a known state rather than a previous test's rows."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {NORMALISED_TABLE}")
        conn.commit()
    return DATABASE_URL


@pytest.fixture
def seeded(database_url):
    publish(database_url, corpus_records())
    return database_url


def test_unmigrated_database_yields_an_empty_repository(database_url):
    # The table has been dropped, so this is a deployment that has never
    # been published to. It must serve zero results, not raise.
    assert PostgresRepository(database_url).all() == []


def test_publish_writes_every_corpus_opportunity(database_url):
    expected = len(corpus_records())
    assert publish(database_url, corpus_records()) == PublishStats(published=expected, removed=0)
    assert len(PostgresRepository(database_url).all()) == expected


def test_repository_round_trips_an_opportunity_through_jsonb(seeded):
    source = {o.id: o for o in (r.opportunity for r in corpus_records())}
    for served in PostgresRepository(seeded).all():
        assert served == source[served.id], f"{served.id} changed in transit"


def test_publishing_twice_upserts_rather_than_duplicating(seeded):
    expected = len(corpus_records())
    publish(seeded, corpus_records())
    assert len(PostgresRepository(seeded).all()) == expected


def test_publishing_a_changed_opportunity_overwrites_the_stored_row(seeded):
    records = corpus_records()
    records[0].opportunity.title = "Renamed Scheme"
    publish(seeded, records)

    found = PostgresRepository(seeded).get(records[0].opportunity.id)
    assert found is not None
    assert found.title == "Renamed Scheme"


def test_get_returns_an_opportunity_by_id_and_none_for_unknown(seeded):
    repo = PostgresRepository(seeded)
    some_id = repo.all()[0].id
    assert repo.get(some_id) is not None
    assert repo.get("does-not-exist") is None


def test_publish_copies_a_normalised_crawler_database(database_url, normalised_sqlite_db):
    records = records_from_sqlite(normalised_sqlite_db)
    assert records, "fixture database should contain normalised records"

    publish(database_url, records)
    served = {o.id for o in PostgresRepository(database_url).all()}
    assert served == {r.opportunity.id for r in records}


def test_upsert_of_an_empty_batch_is_a_no_op(database_url):
    with psycopg.connect(database_url) as conn:
        init_schema(conn)
        assert upsert_records(conn, []) == 0
        conn.commit()
    assert PostgresRepository(database_url).all() == []


def test_get_repository_serves_postgres_when_the_env_selects_it(seeded, monkeypatch):
    monkeypatch.setenv("FMF_DATA_SOURCE", "postgres")
    monkeypatch.setenv("FMF_DATABASE_URL", seeded)
    get_repository.cache_clear()
    try:
        repo = get_repository()
        assert isinstance(repo, PostgresRepository)
        assert len(repo.all()) == len(corpus_records())
    finally:
        get_repository.cache_clear()


def test_postgres_without_a_url_fails_loudly_rather_than_falling_back(monkeypatch):
    # Silently falling back to another data source would make a misconfigured
    # deployment look healthy while serving illustrative data as real.
    monkeypatch.setenv("FMF_DATA_SOURCE", "postgres")
    monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    get_repository.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="FMF_DATABASE_URL"):
            get_repository()
    finally:
        get_repository.cache_clear()


def test_publish_accepts_text_that_still_carries_a_nul_byte(database_url):
    record = corpus_records()[0]
    record.opportunity.summary = "Binary page\x00 residue"
    publish(database_url, [record])
    stored = PostgresRepository(database_url).get(record.opportunity.id)
    assert stored is not None
    assert stored.summary == "Binary page residue"


def _with_url(record, url, title=None):
    record = record.model_copy(deep=True)
    record.opportunity.url = url
    record.opportunity.id = url
    if title is not None:
        record.opportunity.title = title
    return record


def test_publish_removes_the_urls_the_normaliser_rejected(seeded):
    rejected = corpus_records()[0].opportunity
    stats = publish(seeded, [], rejected_urls=[rejected.url, "https://never-published.org/"])
    assert stats == PublishStats(published=0, removed=1)
    assert PostgresRepository(seeded).get(rejected.id) is None
    assert len(PostgresRepository(seeded).all()) == len(corpus_records()) - 1


def test_publish_prunes_stored_pages_from_blocked_sites_and_bot_checks(database_url):
    # Rows published before the relevance rule existed, and not in this run.
    template = corpus_records()[0]
    stale = [
        _with_url(template, "https://en.wikipedia.org/wiki/Funding"),
        _with_url(template, "https://www.lms.ac.uk/grants/other-sources", "One moment, please..."),
    ]
    with psycopg.connect(database_url) as conn:
        init_schema(conn)
        upsert_records(conn, stale)
        conn.commit()

    stats = publish(database_url, corpus_records())

    assert stats == PublishStats(published=len(corpus_records()), removed=2)
    served = {o.url for o in PostgresRepository(database_url).all()}
    assert served == {r.opportunity.url for r in corpus_records()}


def test_published_urls_lists_every_stored_page(seeded):
    from backend.data.postgres_repository import published_urls

    assert published_urls(seeded) == sorted(r.opportunity.url for r in corpus_records())


def test_published_urls_of_an_unmigrated_database_is_empty(database_url):
    from backend.data.postgres_repository import published_urls

    assert published_urls(database_url) == []
