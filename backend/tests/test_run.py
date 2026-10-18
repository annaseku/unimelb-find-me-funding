"""Tests for backend.normaliser.run, the normaliser's command-line entry
point: argument handling and the summary it prints."""

# mutation-check: characterisation

from __future__ import annotations

import sqlite3
import sys

import pytest

from backend.crawler.storage import init_db, save_opportunity
from backend.normaliser import run as run_module
from backend.normaliser.pipeline import load_normalised
from backend.normaliser.rules import load_fixture_rows
from backend.tests.conftest import TODAY


@pytest.fixture
def crawler_db(tmp_path):
    """A crawler database holding the fixture rows, not yet normalised."""
    db = tmp_path / "crawler.db"
    init_db(str(db))
    for row in load_fixture_rows():
        fields = {
            "title": row.title,
            "raw_text": row.raw_text,
            "deadline_raw": row.deadline_raw,
            "deadline_parsed": row.deadline_parsed,
            "funding_amount_raw": row.funding_amount_raw,
            "eligibility_snippet": row.eligibility_snippet,
        }
        save_opportunity(row.url, fields, row.source_query or "", db_path=str(db))
    return db


@pytest.fixture
def no_llm_factory(monkeypatch):
    """Fail the test if run.py builds an LLM extractor: no test may reach the LLM provider."""
    calls = []
    monkeypatch.setattr(run_module, "extractor_from_env", lambda: calls.append(1))
    return calls


def _run(monkeypatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["run", *args])
    run_module.main()


def _summary(output: str) -> dict[str, str]:
    return dict(line.split(": ", 1) for line in output.splitlines() if ": " in line)


def test_run_normalises_every_crawled_row_and_reports_it(
    monkeypatch, capsys, crawler_db, no_llm_factory
):
    _run(monkeypatch, "--db", str(crawler_db), "--today", TODAY.isoformat(), "--no-llm")

    summary = _summary(capsys.readouterr().out)
    rows = len(load_fixture_rows())
    assert summary["rows read"] == str(rows)
    assert int(summary["normalised"]) > 0
    assert summary["llm calls"] == "0"
    assert summary["API data source"] == f"FMF_DATA_SOURCE=sqlite FMF_DB_PATH={crawler_db}"

    with sqlite3.connect(crawler_db) as conn:
        assert len(load_normalised(conn)) == int(summary["normalised"])


def test_a_second_run_skips_unchanged_rows_unless_forced(
    monkeypatch, capsys, crawler_db, no_llm_factory
):
    args = ("--db", str(crawler_db), "--today", TODAY.isoformat(), "--no-llm")
    _run(monkeypatch, *args)
    normalised = _summary(capsys.readouterr().out)["normalised"]

    _run(monkeypatch, *args)
    second = _summary(capsys.readouterr().out)
    assert second["normalised"] == "0"
    assert second["skipped unchanged"] == normalised

    _run(monkeypatch, *args, "--force")
    assert _summary(capsys.readouterr().out)["normalised"] == normalised


def test_no_llm_never_builds_an_extractor(monkeypatch, capsys, crawler_db, no_llm_factory):
    _run(monkeypatch, "--db", str(crawler_db), "--no-llm")
    assert no_llm_factory == []


def test_without_no_llm_the_extractor_comes_from_the_environment(
    monkeypatch, capsys, crawler_db, no_llm_factory
):
    _run(monkeypatch, "--db", str(crawler_db), "--today", TODAY.isoformat())
    assert no_llm_factory == [1]


def test_a_malformed_today_is_rejected(monkeypatch, capsys, crawler_db, no_llm_factory):
    with pytest.raises(SystemExit) as exit_info:
        _run(monkeypatch, "--db", str(crawler_db), "--today", "01/09/2026")
    assert exit_info.value.code == 2
