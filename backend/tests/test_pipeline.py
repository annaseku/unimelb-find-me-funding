"""Tests for backend.normaliser.pipeline: reading crawled rows out of the
crawler's SQLite database, normalising them into `normalised_opportunities`,
skip-on-unchanged behaviour, and the LLM extractor's gap-filling and
failure paths."""

from __future__ import annotations

import json
import sqlite3
from datetime import date

import pytest

from backend.crawler.storage import (
    get_all_opportunities,
    init_db,
    mark_fetch_failed,
    save_opportunity,
)
from backend.normaliser.llm import ExtractedFields, FakeExtractor
from backend.normaliser.pipeline import load_latest_run, load_normalised, normalise_database
from backend.normaliser.rules import load_fixture_rows
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
    with sqlite3.connect(str(crawler_db)) as conn:
        records = load_normalised(conn)
    assert len(records) == 5
    ids = {record.opportunity.id for record in records}
    assert len(ids) == 5


def test_fetch_failed_row_is_never_read(crawler_db):
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    with sqlite3.connect(str(crawler_db)) as conn:
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
    with sqlite3.connect(str(crawler_db)) as conn:
        records = load_normalised(conn)
    assert all(record.used_llm for record in records)


def test_llm_failures_still_write_rule_only_records(crawler_db):
    class RaisingExtractor:
        def extract(self, title: str, url: str, text: str) -> ExtractedFields:
            raise RuntimeError("boom")

    stats = normalise_database(crawler_db, TODAY, extractor=RaisingExtractor())

    assert stats.llm_failures == 5
    assert stats.normalised == 5
    with sqlite3.connect(str(crawler_db)) as conn:
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
    with sqlite3.connect(str(db)) as conn:
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
    with sqlite3.connect(str(db)) as conn:
        row = conn.execute("SELECT opportunity_json FROM normalised_opportunities").fetchone()
    assert "\\u0000" not in row[0]
    assert "\x00" not in row[0]
    assert json.loads(row[0])["title"] == "Grant guidelines"


class _GeminiError(Exception):
    """Shaped like google.genai.errors.APIError: code, status, message, details."""

    def __init__(self, code, status, message="", quota_ids=(), retry_delay=None):
        details = [
            {
                "@type": "type.googleapis.com/google.rpc.QuotaFailure",
                "violations": [{"quotaId": q} for q in quota_ids],
            }
        ]
        if retry_delay:
            details.append(
                {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": retry_delay}
            )
        self.code, self.status, self.message = code, status, message
        self.details = {"error": {"code": code, "status": status, "details": details}}
        super().__init__(f"{code} {status}. {message}")


PER_MINUTE = "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
PER_DAY = "GenerateRequestsPerDayPerProjectPerModel-FreeTier"


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


def test_a_per_minute_rate_limit_is_waited_out_and_the_row_still_gets_the_llm(crawler_db):
    """Regression (crawl run 39112367229): the free tier's 5-a-minute cap used
    to switch the whole run to rules-only after the fifth call."""
    rate_limited = _GeminiError(429, "RESOURCE_EXHAUSTED", quota_ids=[PER_MINUTE], retry_delay="8s")
    extractor = _ScriptedExtractor([rate_limited, rate_limited])
    waits = []
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=waits.append)

    assert waits == [9.0, 9.0]
    assert stats.rate_limit_waits == 2
    assert stats.llm_failures == 0
    assert stats.llm_stop_reason is None
    assert stats.llm_calls == stats.rows_read
    assert all(r.used_llm for r in _load(crawler_db))


def test_the_daily_quota_switches_the_rest_of_the_run_to_rules_only(crawler_db):
    extractor = _ScriptedExtractor(
        [_GeminiError(429, "RESOURCE_EXHAUSTED", "Quota exceeded", quota_ids=[PER_DAY])]
    )
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=pytest.fail)
    assert extractor.calls == 1
    assert stats.llm_failures == 1
    assert stats.llm_stop_reason == "daily_quota"
    assert stats.llm_stop_detail == "429 RESOURCE_EXHAUSTED: Quota exceeded"
    assert stats.normalised == stats.rows_read
    assert all(not r.used_llm for r in _load(crawler_db))


def test_a_429_without_quota_details_is_treated_as_the_daily_quota(crawler_db):
    extractor = _ScriptedExtractor([_GeminiError(429, "RESOURCE_EXHAUSTED")])
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=pytest.fail)
    assert stats.llm_stop_reason == "daily_quota"


@pytest.mark.parametrize(
    ("code", "status", "message"),
    [
        (400, "INVALID_ARGUMENT", "API key not valid. Please pass a valid API key."),
        (403, "PERMISSION_DENIED", "Your project has been denied access."),
        (400, "FAILED_PRECONDITION", "User location is not supported for the API use."),
    ],
)
def test_a_key_or_plan_error_stops_llm_use_for_the_run(crawler_db, code, status, message):
    extractor = _ScriptedExtractor([_GeminiError(code, status, message)])
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=pytest.fail)
    assert extractor.calls == 1
    assert stats.llm_stop_reason == "plan_error"
    assert stats.llm_stop_detail.startswith(f"{code} {status}")


def test_a_one_off_row_error_does_not_stop_the_run(crawler_db):
    extractor = _ScriptedExtractor([_GeminiError(500, "INTERNAL")])
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, sleep=pytest.fail)
    assert stats.llm_failures == 1
    assert stats.llm_stop_reason is None
    assert stats.llm_calls == stats.rows_read - 1


def test_each_run_is_recorded_with_its_llm_outcome(crawler_db):
    extractor = _ScriptedExtractor(
        [_GeminiError(429, "RESOURCE_EXHAUSTED", "Quota exceeded", quota_ids=[PER_DAY])]
    )
    normalise_database(crawler_db, TODAY, extractor=extractor)
    with sqlite3.connect(str(crawler_db)) as conn:
        run = load_latest_run(conn)
    assert run is not None
    assert run.llm_stop_reason == "daily_quota"
    assert run.llm_failures == 1


def test_a_run_without_an_extractor_is_recorded_as_not_configured(crawler_db):
    normalise_database(crawler_db, TODAY)
    with sqlite3.connect(str(crawler_db)) as conn:
        assert load_latest_run(conn).llm_stop_reason == "not_configured"


def _load(db):
    with sqlite3.connect(str(db)) as conn:
        return load_normalised(conn)
