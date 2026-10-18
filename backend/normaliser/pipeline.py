"""Runs the normaliser over one crawler SQLite database: reads every row
that fetched successfully, applies the rule-based parsers, optionally asks
the LLM extractor to fill the prose-derived gaps, and writes the result into
a `normalised_opportunities` table in the same database file. A page whose
content hash has not changed since the last run is skipped, unless `force`
is set or the row has never been touched by an extractor that is now
available."""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal

from backend.normaliser.llm import ExtractedFields, Extractor, merge
from backend.normaliser.models import CrawledRow, LlmStopReason, NormalisedRecord, PipelineRun
from backend.normaliser.parsers import derive_status
from backend.normaliser.rules import content_hash, normalise_row
from backend.ranking.models import Opportunity

logger = logging.getLogger(__name__)

NORMALISED_TABLE = "normalised_opportunities"
RUNS_TABLE = "pipeline_runs"

# Per-minute rate limits are waited out, not treated as the end of the run.
MAX_RATE_LIMIT_RETRIES = 5
DEFAULT_RATE_LIMIT_WAIT_S = 60.0
MAX_RATE_LIMIT_WAIT_S = 120.0

# Gemini statuses meaning the key, billing or plan itself is the problem.
PLAN_ERROR_STATUSES = frozenset({"PERMISSION_DENIED", "UNAUTHENTICATED", "FAILED_PRECONDITION"})

LlmErrorKind = Literal["rate_limit", "daily_quota", "plan_error", "row_error"]


@dataclass
class PipelineStats:
    rows_read: int = 0
    normalised: int = 0
    skipped_unchanged: int = 0
    llm_calls: int = 0
    llm_failures: int = 0
    rate_limit_waits: int = 0
    llm_stop_reason: LlmStopReason | None = None
    llm_stop_detail: str = ""


def init_normalised_table(conn: sqlite3.Connection) -> None:
    """Create the normalised_opportunities table if it doesn't already exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {NORMALISED_TABLE} (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            content_hash TEXT NOT NULL,
            opportunity_json TEXT NOT NULL,
            provenance_json TEXT NOT NULL,
            used_llm INTEGER NOT NULL DEFAULT 0,
            normalised_at TEXT NOT NULL
        )
        """
    )


def _without_nul(value: object) -> object:
    """Postgres rejects NUL inside text and JSON; a crawled PDF or binary page
    can carry them, and SQLite stores them without complaint."""
    return value.replace("\x00", "") if isinstance(value, str) else value


def read_crawled_rows(conn: sqlite3.Connection) -> list[CrawledRow]:
    """Every crawled row that fetched successfully (fetch_failed = 0)."""
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM opportunities WHERE fetch_failed = 0")
    return [
        CrawledRow(**{key: _without_nul(value) for key, value in dict(row).items()})
        for row in cursor.fetchall()
    ]


def _error_details(exc: BaseException) -> list[dict]:
    """The `error.details` list of a Gemini APIError, or [] for anything else."""
    body = getattr(exc, "details", None)
    error = body.get("error") if isinstance(body, dict) else None
    details = error.get("details") if isinstance(error, dict) else None
    return [d for d in details if isinstance(d, dict)] if isinstance(details, list) else []


def _retry_delay(details: list[dict]) -> float:
    for detail in details:
        match = re.fullmatch(r"([\d.]+)s", str(detail.get("retryDelay", "")))
        if match:
            return min(float(match.group(1)) + 1, MAX_RATE_LIMIT_WAIT_S)
    return DEFAULT_RATE_LIMIT_WAIT_S


def classify_llm_error(exc: BaseException) -> tuple[LlmErrorKind, float]:
    """What a failed LLM call means for the rest of the run, plus how long to
    wait before retrying when it is only a per-minute rate limit.

    The free tier's per-minute cap (5 requests a minute on gemini-2.5-flash)
    returns the same 429 RESOURCE_EXHAUSTED as the daily cap; only the
    QuotaFailure quotaId tells them apart. A 429 that names no per-minute
    quota is treated as the daily one."""
    code = getattr(exc, "code", None)
    status = str(getattr(exc, "status", "") or "")
    details = _error_details(exc)
    if code == 429 or "RESOURCE_EXHAUSTED" in str(exc):
        quota_ids = [
            str(v.get("quotaId", ""))
            for d in details
            for v in d.get("violations", [])
            if isinstance(v, dict)
        ]
        if quota_ids and all("PerMinute" in q for q in quota_ids):
            return "rate_limit", _retry_delay(details)
        return "daily_quota", 0
    if code in (401, 403) or status in PLAN_ERROR_STATUSES:
        return "plan_error", 0
    if code == 400 and "API key" in str(exc):
        return "plan_error", 0
    return "row_error", 0


def _short_error(exc: BaseException) -> str:
    """Code, status and message only; safe to show on screen (no key, no page text)."""
    parts = [str(getattr(exc, "code", "") or ""), str(getattr(exc, "status", "") or "")]
    message = str(getattr(exc, "message", "") or "").split("\n")[0][:200]
    return " ".join(p for p in parts if p) + (f": {message}" if message else "")


def _extract_with_retries(
    extractor: Extractor,
    row: CrawledRow,
    stats: PipelineStats,
    sleep: Callable[[float], None],
) -> ExtractedFields:
    """One extractor call, waiting out per-minute rate limits. Any other
    error (or a rate limit that outlasts the retries) propagates."""
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            return extractor.extract(row.title or "", row.url, row.raw_text or "")
        except Exception as exc:
            kind, wait = classify_llm_error(exc)
            if kind != "rate_limit" or attempt == MAX_RATE_LIMIT_RETRIES:
                raise
            stats.rate_limit_waits += 1
            logger.info("LLM per-minute limit hit; waiting %.0fs", wait)
            sleep(wait)
    raise AssertionError("unreachable")


def load_normalised(conn: sqlite3.Connection) -> list[NormalisedRecord]:
    """Every stored normalised record, rebuilt from its JSON columns."""
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(f"SELECT * FROM {NORMALISED_TABLE}")
    records = []
    for row in cursor.fetchall():
        opportunity = Opportunity(**json.loads(row["opportunity_json"]))
        provenance = json.loads(row["provenance_json"])
        records.append(
            NormalisedRecord(
                opportunity=opportunity,
                provenance=provenance,
                content_hash=row["content_hash"],
                used_llm=bool(row["used_llm"]),
            )
        )
    return records


def _existing_state(conn: sqlite3.Connection) -> dict[str, tuple[str, bool]]:
    """URL to (content_hash, used_llm) for every row already normalised."""
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(f"SELECT url, content_hash, used_llm FROM {NORMALISED_TABLE}")
    return {row["url"]: (row["content_hash"], bool(row["used_llm"])) for row in cursor.fetchall()}


def _upsert(conn: sqlite3.Connection, record: NormalisedRecord) -> None:
    opportunity_json = json.dumps(record.opportunity.model_dump(mode="json"))
    provenance_json = json.dumps(record.provenance)
    normalised_at = datetime.now(UTC).isoformat()
    conn.execute(
        f"""
        INSERT INTO {NORMALISED_TABLE} (
            id, url, content_hash, opportunity_json, provenance_json, used_llm, normalised_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            id = excluded.id,
            content_hash = excluded.content_hash,
            opportunity_json = excluded.opportunity_json,
            provenance_json = excluded.provenance_json,
            used_llm = excluded.used_llm,
            normalised_at = excluded.normalised_at
        """,
        (
            record.opportunity.id,
            record.opportunity.url,
            record.content_hash,
            opportunity_json,
            provenance_json,
            int(record.used_llm),
            normalised_at,
        ),
    )


def write_run(conn: sqlite3.Connection, run: PipelineRun) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RUNS_TABLE} (
            finished_at TEXT NOT NULL,
            run_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        f"INSERT INTO {RUNS_TABLE} (finished_at, run_json) VALUES (?, ?)",
        (run.finished_at.isoformat(), run.model_dump_json()),
    )


def load_latest_run(conn: sqlite3.Connection) -> PipelineRun | None:
    """The most recent run recorded in this database, or None before the first."""
    try:
        row = conn.execute(
            f"SELECT run_json FROM {RUNS_TABLE} ORDER BY finished_at DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    return PipelineRun.model_validate_json(row[0]) if row else None


def write_records(conn: sqlite3.Connection, records: Iterable[NormalisedRecord]) -> int:
    """Create the normalised table and upsert every record; return the count."""
    init_normalised_table(conn)
    written = 0
    for record in records:
        _upsert(conn, record)
        written += 1
    return written


def normalise_database(
    db_path: str | Path,
    today: date,
    extractor: Extractor | None = None,
    force: bool = False,
    sleep: Callable[[float], None] = time.sleep,
) -> PipelineStats:
    """Read every crawled row out of `db_path`, normalise it, and upsert the
    result into `normalised_opportunities` in the same file."""
    stats = PipelineStats()
    if extractor is None:
        stats.llm_stop_reason = "not_configured"

    with sqlite3.connect(str(db_path)) as conn:
        init_normalised_table(conn)
        existing = _existing_state(conn)
        rows = read_crawled_rows(conn)
        stats.rows_read = len(rows)

        for row in rows:
            row_hash = content_hash(row)
            stored = existing.get(row.url)
            if not force and stored is not None:
                stored_hash, stored_used_llm = stored
                # Skip only when the page hasn't changed AND either the
                # stored record already used the LLM, or there is no
                # extractor to run now (nothing new to gain from re-running).
                if stored_hash == row_hash and (stored_used_llm or extractor is None):
                    stats.skipped_unchanged += 1
                    continue

            record = normalise_row(row, today)

            if extractor is not None:
                try:
                    extracted = _extract_with_retries(extractor, row, stats, sleep)
                except Exception as exc:
                    logger.warning("LLM extraction failed for %s", row.url, exc_info=True)
                    stats.llm_failures += 1
                    kind, _ = classify_llm_error(exc)
                    if kind in ("daily_quota", "plan_error"):
                        logger.warning("LLM stopped (%s); the rest of this run is rules-only", kind)
                        stats.llm_stop_reason = kind
                        stats.llm_stop_detail = _short_error(exc)
                        extractor = None
                else:
                    record = merge(record, extracted)
                    # A model-supplied deadline can turn a rule-only "active"
                    # record into a closed one (or vice versa); re-derive
                    # status so the two never disagree.
                    record.opportunity.status = derive_status(record.opportunity.deadline, today)
                    stats.llm_calls += 1

            stats.normalised += write_records(conn, [record])

        write_run(
            conn,
            PipelineRun(
                finished_at=datetime.now(UTC),
                llm_calls=stats.llm_calls,
                llm_failures=stats.llm_failures,
                llm_stop_reason=stats.llm_stop_reason,
                llm_stop_detail=stats.llm_stop_detail,
            ),
        )
        conn.commit()

    return stats
