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
from datetime import UTC, datetime, timedelta

import psycopg
import pytest

from backend.data.postgres_repository import (
    PostgresRepository,
    init_schema,
    read_published_urls,
    upsert_records,
)
from backend.data.publish import publish, records_from_sqlite
from backend.data.repository import get_repository
from backend.evals.corpus import corpus_records
from backend.normaliser.models import PipelineRun
from backend.normaliser.pipeline import NORMALISED_TABLE, RUNS_TABLE
from backend.ranking.models import OpportunityStatus

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
        conn.execute(f"DROP TABLE IF EXISTS {RUNS_TABLE}")
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
    assert publish(database_url, corpus_records()) == expected
    assert len(PostgresRepository(database_url).all()) == expected


def test_repository_round_trips_an_opportunity_through_jsonb(seeded):
    source = {o.id: o for o in (r.opportunity for r in corpus_records())}
    for served in PostgresRepository(seeded).all():
        assert served == source[served.id], f"{served.id} changed in transit"


def test_read_published_urls_returns_every_seeded_url(seeded):
    assert sorted(read_published_urls(seeded)) == sorted(
        record.opportunity.url for record in corpus_records()
    )


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


def test_unpublished_database_has_no_last_run(database_url):
    repo = PostgresRepository(database_url)
    assert repo.last_run is None
    assert repo.rule_only_summaries == 0


def test_publish_records_the_run_and_the_latest_one_is_served(database_url):
    earlier = datetime(2026, 10, 18, 8, 0, tzinfo=UTC)
    publish(database_url, corpus_records(), PipelineRun(finished_at=earlier, llm_calls=3))
    publish(
        database_url,
        corpus_records(),
        PipelineRun(
            finished_at=earlier + timedelta(hours=1),
            llm_stop_reason="daily_quota",
            llm_stop_detail="429 RESOURCE_EXHAUSTED",
        ),
    )
    repo = PostgresRepository(database_url)
    assert repo.last_run.llm_stop_reason == "daily_quota"
    # The corpus records carry no "llm" summary provenance.
    assert repo.rule_only_summaries == len(repo.all())


def test_non_funding_round_trips_but_is_excluded_from_repository_counts(database_url):
    records = corpus_records()[:5]
    for record in records:
        record.opportunity.status = OpportunityStatus.ACTIVE
        record.provenance["summary"] = "rule"
    records[0].opportunity.status = OpportunityStatus.NOT_FUNDING
    records[1].opportunity.status = OpportunityStatus.NOT_FUNDING
    records[0].provenance["summary"] = "llm"
    records[2].provenance["summary"] = "llm"
    records[3].opportunity.status = OpportunityStatus.CLOSED
    publish(database_url, records)
    repo = PostgresRepository(database_url)
    assert len(repo.all()) == 5
    assert repo.funding_count == 3
    assert repo.rule_only_summaries == 2
    assert repo.get(records[0].opportunity.id).status == OpportunityStatus.NOT_FUNDING
