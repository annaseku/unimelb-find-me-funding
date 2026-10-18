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
from backend.normaliser.pipeline import (
    MODEL_REJECTION,
    load_normalised,
    load_rejected_urls,
    normalise_database,
    write_records,
)
from backend.normaliser.rules import load_fixture_rows, normalise_row
from backend.tests.conftest import TODAY

NEWS_URL = "https://www.example-news.org/2026/07/university-announces-new-lab"
ARC_URL = (
    "https://www.arc.gov.au/funding-research/funding-schemes/discovery-program/discovery-projects"
)
# Of the five fixture rows, the news page is not a funding opportunity.
FUNDING_ROWS = 4


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


def test_first_run_normalises_every_funding_row_and_rejects_the_news_page(crawler_db):
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    assert stats.normalised == FUNDING_ROWS
    assert stats.rejected == 1
    assert stats.skipped_unchanged == 0


def test_second_run_skips_every_unchanged_row(crawler_db):
    normalise_database(crawler_db, TODAY)
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    assert stats.normalised == 0
    assert stats.skipped_unchanged == FUNDING_ROWS


def test_force_reruns_every_row_even_when_unchanged(crawler_db):
    normalise_database(crawler_db, TODAY)
    stats = normalise_database(crawler_db, TODAY, force=True)
    assert stats.normalised == FUNDING_ROWS
    assert stats.skipped_unchanged == 0


def test_load_normalised_returns_valid_records_with_unique_ids(crawler_db):
    normalise_database(crawler_db, TODAY)
    with sqlite3.connect(str(crawler_db)) as conn:
        records = load_normalised(conn)
    assert len(records) == FUNDING_ROWS
    ids = {record.opportunity.id for record in records}
    assert len(ids) == FUNDING_ROWS


def test_fetch_failed_row_is_never_read(crawler_db):
    stats = normalise_database(crawler_db, TODAY)
    assert stats.rows_read == 5
    with sqlite3.connect(str(crawler_db)) as conn:
        records = load_normalised(conn)
    assert ARC_URL in {record.opportunity.url for record in records}
    assert "https://www.example-failed.org/grants/gone" not in {
        record.opportunity.url for record in records
    }


def test_unchanged_row_is_reprocessed_once_an_extractor_becomes_available(crawler_db):
    normalise_database(crawler_db, TODAY)  # rule-only pass: used_llm stays False

    extractor = FakeExtractor(ExtractedFields(summary="A model-written summary."))
    stats = normalise_database(crawler_db, TODAY, extractor=extractor)

    assert stats.normalised == FUNDING_ROWS
    assert stats.skipped_unchanged == 0
    assert stats.llm_calls == FUNDING_ROWS
    with sqlite3.connect(str(crawler_db)) as conn:
        records = load_normalised(conn)
    assert all(record.used_llm for record in records)


def test_llm_failures_still_write_rule_only_records(crawler_db):
    class RaisingExtractor:
        def extract(self, title: str, url: str, text: str) -> ExtractedFields:
            raise RuntimeError("boom")

    stats = normalise_database(crawler_db, TODAY, extractor=RaisingExtractor())

    assert stats.llm_failures == FUNDING_ROWS
    assert stats.normalised == FUNDING_ROWS
    with sqlite3.connect(str(crawler_db)) as conn:
        records = load_normalised(conn)
    assert len(records) == FUNDING_ROWS
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
    # With its deadline fields cleared, the rules leave the ARC row status
    # ACTIVE. A model-supplied deadline in the past must close it:
    # normalise_database re-derives status after merge for exactly this case.
    arc_row = next(r for r in load_fixture_rows() if r.url == ARC_URL)
    fields = _row_fields(arc_row) | {"deadline_raw": None, "deadline_parsed": None}

    db = tmp_path / "single.db"
    init_db(str(db))
    save_opportunity(arc_row.url, fields, arc_row.source_query or "", db_path=str(db))

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
            "raw_text": "%PDF-1.4\x00\x00 Applications close 1 March 2027. Up to $50,000. "
            + "Eligibility: researchers employed at an Australian university. " * 4,
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


class _QuotaExhausted(Exception):
    code = 429


class _ExplodingExtractor:
    def __init__(self):
        self.calls = 0

    def extract(self, title, url, text):
        self.calls += 1
        raise _QuotaExhausted("429 RESOURCE_EXHAUSTED: quota exceeded")


def test_llm_quota_exhaustion_switches_the_rest_of_the_run_to_rules_only(crawler_db):
    extractor = _ExplodingExtractor()
    stats = normalise_database(crawler_db, TODAY, extractor=extractor)
    assert extractor.calls == 1
    assert stats.llm_failures == 1
    assert stats.llm_quota_exhausted is True
    assert stats.normalised + stats.rejected == stats.rows_read
    assert all(not r.used_llm for r in _load(crawler_db))


def _load(db):
    with sqlite3.connect(str(db)) as conn:
        return load_normalised(conn)


def _rejected(db) -> dict[str, str]:
    with sqlite3.connect(str(db)) as conn:
        return dict(conn.execute("SELECT url, reason FROM rejected_pages").fetchall())


def test_rejected_pages_are_recorded_with_a_reason_and_never_normalised(crawler_db):
    normalise_database(crawler_db, TODAY)
    assert list(_rejected(crawler_db)) == [NEWS_URL]
    assert NEWS_URL not in {r.opportunity.url for r in _load(crawler_db)}
    with sqlite3.connect(str(crawler_db)) as conn:
        assert load_rejected_urls(conn) == [NEWS_URL]


def test_a_page_normalised_before_the_filter_existed_is_removed(crawler_db):
    news_row = next(r for r in load_fixture_rows() if r.url == NEWS_URL)
    with sqlite3.connect(str(crawler_db)) as conn:
        write_records(conn, [normalise_row(news_row, TODAY)])
    assert NEWS_URL in {r.opportunity.url for r in _load(crawler_db)}

    normalise_database(crawler_db, TODAY)

    assert NEWS_URL not in {r.opportunity.url for r in _load(crawler_db)}


def test_the_model_can_reject_a_page_the_rules_accept(crawler_db):
    extractor = FakeExtractor(ExtractedFields(is_funding_opportunity=False))
    stats = normalise_database(crawler_db, TODAY, extractor=extractor)

    # The news page never reaches the model: the rules reject it first.
    assert len(extractor.calls) == FUNDING_ROWS
    assert stats.normalised == 0
    assert stats.rejected == 5
    assert _load(crawler_db) == []
    assert set(_rejected(crawler_db).values()) >= {MODEL_REJECTION}


def test_an_unchanged_page_the_model_rejected_is_not_sent_to_it_again(crawler_db):
    normalise_database(
        crawler_db, TODAY, extractor=FakeExtractor(ExtractedFields(is_funding_opportunity=False))
    )
    extractor = FakeExtractor(ExtractedFields(is_funding_opportunity=True))
    stats = normalise_database(crawler_db, TODAY, extractor=extractor)

    assert extractor.calls == []
    assert stats.rejected == 5

    # force re-judges them, and an accepted page leaves rejected_pages.
    stats = normalise_database(crawler_db, TODAY, extractor=extractor, force=True)
    assert stats.normalised == FUNDING_ROWS
    assert list(_rejected(crawler_db)) == [NEWS_URL]


def test_an_unset_model_verdict_keeps_the_page(crawler_db):
    stats = normalise_database(crawler_db, TODAY, extractor=FakeExtractor(ExtractedFields()))
    assert stats.normalised == FUNDING_ROWS
    assert stats.rejected == 1
