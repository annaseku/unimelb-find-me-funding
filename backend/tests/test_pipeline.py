"""Tests for backend.normaliser.pipeline: reading crawled rows out of the
crawler's SQLite database, normalising them into `normalised_opportunities`,
skip-on-unchanged behaviour, and the LLM extractor's gap-filling and
failure paths."""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import closing
from datetime import date

import httpx
import openai
import pytest

from backend.crawler.storage import (
    get_all_opportunities,
    init_db,
    mark_fetch_failed,
    save_opportunity,
)
from backend.normaliser.llm import ExtractedFields, FakeExtractor
from backend.normaliser.pipeline import (
    DEFAULT_RATE_LIMIT_WAIT_S,
    MAX_RATE_LIMIT_RETRIES,
    load_latest_run,
    load_normalised,
    normalise_database,
)
from backend.normaliser.rules import load_fixture_rows
from backend.ranking.models import OpportunityStatus
from backend.tests.conftest import TODAY

NEWS_URL = "https://www.example-news.org/2026/07/university-announces-new-lab"


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
def crawler_db(tmp_path):
    """A temp crawler database seeded with the five fixture rows, plus one
    extra row marked fetch_failed so the pipeline's WHERE clause is exercised."""
    db = tmp_path / "crawler.db"
    init_db(str(db))
    for row in load_fixture_rows():
        save_opportunity(row.url, _row_fields(row), row.source_query or "", db_path=str(db))

    failed_url = "https://www.example-failed.org/grants/gone"
    save_opportunity(failed_url, {"title": "Gone", "raw_text": "gone"}, "gone", db_path=str(db))
    mark_fetch_failed(failed_url, db_path=str(db))

    return db


def test_first_run_reads_and_normalises_every_row_with_no_skips(crawler_db):
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    assert stats.normalised == 5
    assert stats.skipped_unchanged == 0


def test_second_run_skips_every_unchanged_row(crawler_db):
    normalise_database(crawler_db, TODAY)
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    assert stats.normalised == 0
    assert stats.skipped_unchanged == 5


def test_force_reruns_every_row_even_when_unchanged(crawler_db):
    normalise_database(crawler_db, TODAY)
    stats = normalise_database(crawler_db, TODAY, force=True)
    assert stats.normalised == 5
    assert stats.skipped_unchanged == 0


def test_load_normalised_returns_five_valid_records_with_unique_ids(crawler_db):
    normalise_database(crawler_db, TODAY)
    with closing(sqlite3.connect(str(crawler_db))) as conn, conn:
        records = load_normalised(conn)
    assert len(records) == 5
    ids = {record.opportunity.id for record in records}
    assert len(ids) == 5


def test_fetch_failed_row_is_never_read(crawler_db):
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    with closing(sqlite3.connect(str(crawler_db))) as conn, conn:
        records = load_normalised(conn)
    assert NEWS_URL in {record.opportunity.url for record in records}
    assert "https://www.example-failed.org/grants/gone" not in {
        record.opportunity.url for record in records
    }


def test_unchanged_row_is_reprocessed_once_an_extractor_becomes_available(crawler_db):
    normalise_database(crawler_db, TODAY)  # rule-only pass: used_llm stays False

    extractor = FakeExtractor(ExtractedFields(summary="A model-written summary."))
    stats = normalise_database(crawler_db, TODAY, extractor=extractor)

    assert stats.normalised == 5
    assert stats.skipped_unchanged == 0
    assert stats.llm_calls == 5
    with closing(sqlite3.connect(str(crawler_db))) as conn, conn:
        records = load_normalised(conn)
    assert all(record.used_llm for record in records)


def test_llm_failures_still_write_rule_only_records(crawler_db):
    class RaisingExtractor:
        def extract(self, title: str, url: str, text: str) -> ExtractedFields:
            raise RuntimeError("boom")

    stats = normalise_database(crawler_db, TODAY, extractor=RaisingExtractor())

    assert stats.llm_failures == 5
    assert stats.normalised == 5
    with closing(sqlite3.connect(str(crawler_db))) as conn, conn:
        records = load_normalised(conn)
    assert len(records) == 5
    assert all(not record.used_llm for record in records)


def test_crawled_table_is_untouched_by_the_pipeline(crawler_db):
    before = get_all_opportunities(str(crawler_db))
    normalise_database(crawler_db, TODAY)
    after = get_all_opportunities(str(crawler_db))

    assert len(before) == len(after)
    before_by_url = {row["url"]: row for row in before}
    after_by_url = {row["url"]: row for row in after}
    sample_url = before[0]["url"]
    assert before_by_url[sample_url] == after_by_url[sample_url]


def test_model_supplied_past_deadline_closes_a_record_with_no_rule_deadline(tmp_path):
    # The news page fixture row has no deadline at all, so the rules leave
    # it status ACTIVE. A model-supplied deadline in the past must close it:
    # normalise_database re-derives status after merge for exactly this case.
    news_row = next(r for r in load_fixture_rows() if r.url == NEWS_URL)
    assert news_row.deadline_raw is None
    assert news_row.deadline_parsed is None

    db = tmp_path / "single.db"
    init_db(str(db))
    save_opportunity(
        news_row.url, _row_fields(news_row), news_row.source_query or "", db_path=str(db)
    )

    past_deadline = date(2026, 1, 1)
    extractor = FakeExtractor(ExtractedFields(deadline=past_deadline))
    stats = normalise_database(db, TODAY, extractor=extractor)

    assert stats.normalised == 1
    assert stats.llm_calls == 1
    with closing(sqlite3.connect(str(db))) as conn, conn:
        records = load_normalised(conn)
    assert len(records) == 1
    record = records[0]
    assert record.opportunity.deadline == past_deadline
    assert record.opportunity.status.value == "closed"
    assert record.provenance["deadline"] == "llm"


def test_nul_bytes_from_a_binary_page_are_stripped_before_normalising(tmp_path):
    db = tmp_path / "crawler.db"
    init_db(str(db))
    save_opportunity(
        "https://example.org/binary.pdf",
        {
            "title": "Grant\x00 guidelines",
            "raw_text": "%PDF-1.4\x00\x00 Applications close 1 March 2027. Up to $50,000.",
            "deadline_raw": None,
            "deadline_parsed": None,
            "funding_amount_raw": "$50,000",
            "eligibility_snippet": None,
        },
        "test",
        db_path=str(db),
    )
    normalise_database(db, TODAY)
    with closing(sqlite3.connect(str(db))) as conn, conn:
        row = conn.execute("SELECT opportunity_json FROM normalised_opportunities").fetchone()
    assert "\\u0000" not in row[0]
    assert "\x00" not in row[0]
    assert json.loads(row[0])["title"] == "Grant guidelines"


def _provider_error(status, message="", headers=None):
    """The exception the openai SDK raises for an OpenRouter HTTP error, built
    from a real httpx response so status_code, message and headers match."""
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(status, headers=headers or {}, request=request)
    error_class = {
        401: openai.AuthenticationError,
        429: openai.RateLimitError,
        500: openai.InternalServerError,
    }.get(status, openai.APIStatusError)
    return error_class(message, response=response, body={"error": {"message": message}})


class _ScriptedExtractor:
    """Raises each queued error in turn, then succeeds."""

    def __init__(self, errors):
        self.errors = list(errors)
        self.calls = 0

    def extract(self, title, url, text):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return ExtractedFields(summary="Funds early-career research in marine biology.")


def test_a_rate_limit_is_waited_out_and_the_row_still_gets_the_llm(crawler_db):
    """Regression (crawl run 39112367229): a short rate limit used to switch
    the whole run to rules-only after the fifth call."""
    rate_limited = _provider_error(429, "Rate limit exceeded", {"retry-after": "8"})
    extractor = _ScriptedExtractor([rate_limited, rate_limited])
    waits = []
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=waits.append)

    assert waits == [9.0, 9.0]
    assert stats.rate_limit_waits == 2
    assert stats.llm_failures == 0
    assert stats.llm_stop_reason is None
    assert stats.llm_calls == stats.rows_read
    assert all(r.used_llm for r in _load(crawler_db))


def test_a_rate_limit_without_retry_after_waits_the_default(crawler_db):
    extractor = _ScriptedExtractor([_provider_error(429)])
    waits = []
    normalise_database(crawler_db, TODAY, extractor=extractor, sleep=waits.append)
    assert waits == [DEFAULT_RATE_LIMIT_WAIT_S]


def test_a_rate_limit_that_outlasts_every_retry_stops_llm_use(crawler_db):
    extractor = _ScriptedExtractor(
        [_provider_error(429, "Rate limit exceeded")] * (MAX_RATE_LIMIT_RETRIES + 1)
    )
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=lambda s: None)
    assert extractor.calls == MAX_RATE_LIMIT_RETRIES + 1
    assert stats.llm_failures == 1
    assert stats.llm_stop_reason == "daily_quota"
    assert stats.llm_stop_detail == "429 Rate limit exceeded"
    assert stats.normalised == stats.rows_read


@pytest.mark.parametrize(
    ("status", "message"),
    [(401, "No auth credentials found"), (402, "Insufficient credits")],
)
def test_a_bad_key_or_empty_credit_stops_llm_use_for_the_run(crawler_db, status, message):
    extractor = _ScriptedExtractor([_provider_error(status, message)])
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=pytest.fail)
    assert extractor.calls == 1
    assert stats.llm_stop_reason == "plan_error"
    assert stats.llm_stop_detail == f"{status} {message}"
    assert all(not r.used_llm for r in _load(crawler_db))


@pytest.mark.parametrize(
    "error", [_provider_error(500), _provider_error(403), ValueError("bad JSON")]
)
def test_a_one_off_row_error_does_not_stop_the_run(crawler_db, error):
    extractor = _ScriptedExtractor([error])
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=pytest.fail)
    assert stats.llm_failures == 1
    assert stats.llm_stop_reason is None
    assert stats.llm_calls == stats.rows_read - 1


class _BarrierExtractor:
    """The first two calls only return once both are in flight, so a serial
    pipeline breaks the barrier and records failures."""

    def __init__(self):
        self.barrier = threading.Barrier(2, timeout=5)
        self.calls = 0
        self.lock = threading.Lock()

    def extract(self, title, url, text):
        with self.lock:
            self.calls += 1
            first_two = self.calls <= 2
        if first_two:
            self.barrier.wait()
        return ExtractedFields(summary=f"Summary of {url}.")


def test_llm_workers_run_extractor_calls_in_parallel(crawler_db):
    stats = normalise_database(crawler_db, TODAY, extractor=_BarrierExtractor(), llm_workers=4)
    assert stats.llm_failures == 0
    assert stats.llm_calls == stats.rows_read
    records = _load(crawler_db)
    assert all(r.opportunity.summary == f"Summary of {r.opportunity.url}." for r in records)


def test_a_bad_key_still_stops_llm_use_with_parallel_workers(crawler_db):
    extractor = _ScriptedExtractor([_provider_error(402, "Insufficient credits")] * 20)
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, llm_workers=4)
    assert stats.llm_stop_reason == "plan_error"
    assert stats.normalised == stats.rows_read
    assert all(not r.used_llm for r in _load(crawler_db))


def test_each_run_is_recorded_with_its_llm_outcome(crawler_db):
    extractor = _ScriptedExtractor([_provider_error(402, "Insufficient credits")])
    normalise_database(crawler_db, TODAY, extractor=extractor)
    with closing(sqlite3.connect(str(crawler_db))) as conn, conn:
        run = load_latest_run(conn)
    assert run is not None
    assert run.llm_stop_reason == "plan_error"
    assert run.llm_failures == 1


def test_a_run_without_an_extractor_is_recorded_as_not_configured(crawler_db):
    normalise_database(crawler_db, TODAY)
    with closing(sqlite3.connect(str(crawler_db))) as conn, conn:
        assert load_latest_run(conn).llm_stop_reason == "not_configured"


def _load(db):
    with closing(sqlite3.connect(str(db))) as conn, conn:
        return load_normalised(conn)


@pytest.mark.parametrize("deadline", [date(2027, 1, 1), date(2026, 1, 1), None])
def test_non_funding_status_survives_deadline_derivation_and_database_reload(tmp_path, deadline):
    row = next(r for r in load_fixture_rows() if r.url == NEWS_URL)
    db = tmp_path / "non-funding.db"
    init_db(str(db))
    save_opportunity(row.url, _row_fields(row), row.source_query or "", db_path=str(db))
    extractor = FakeExtractor(ExtractedFields(is_funding_opportunity=False, deadline=deadline))
    stats = normalise_database(db, TODAY, extractor=extractor)
    assert stats.normalised == stats.llm_calls == 1
    record = _load(db)[0]
    assert record.opportunity.deadline == deadline
    assert record.opportunity.status == OpportunityStatus.NOT_FUNDING
    assert record.provenance["status"] == "llm"
    assert record.used_llm
