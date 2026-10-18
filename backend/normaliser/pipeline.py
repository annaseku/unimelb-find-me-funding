"""Runs the normaliser over one crawler SQLite database: reads every row
that fetched successfully, drops pages that are not funding opportunities,
applies the rule-based parsers, optionally asks the LLM extractor to fill the
prose-derived gaps, and writes the result into a `normalised_opportunities`
table in the same database file. A page whose content hash has not changed
since the last run is skipped, unless `force` is set or the row has never been
touched by an extractor that is now available.

Dropped pages are listed in `rejected_pages`, with the reason, so the
publisher can remove them from Postgres too."""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from backend.normaliser.llm import Extractor, merge
from backend.normaliser.models import CrawledRow, NormalisedRecord
from backend.normaliser.parsers import derive_status
from backend.normaliser.relevance import reject_reason
from backend.normaliser.rules import content_hash, normalise_row
from backend.ranking.models import Opportunity

logger = logging.getLogger(__name__)

NORMALISED_TABLE = "normalised_opportunities"
REJECTED_TABLE = "rejected_pages"
MODEL_REJECTION = "model: not a funding opportunity"


@dataclass
class PipelineStats:
    rows_read: int = 0
    normalised: int = 0
    skipped_unchanged: int = 0
    rejected: int = 0
    llm_calls: int = 0
    llm_failures: int = 0
    llm_quota_exhausted: bool = False


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


def init_rejected_table(conn: sqlite3.Connection) -> None:
    """Create the rejected_pages table if it doesn't already exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {REJECTED_TABLE} (
            url TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
        """
    )


def _reject(conn: sqlite3.Connection, url: str, row_hash: str, reason: str) -> None:
    """Record why a page was dropped and remove any record it had before."""
    conn.execute(
        f"""
        INSERT INTO {REJECTED_TABLE} (url, content_hash, reason, rejected_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            content_hash = excluded.content_hash,
            reason = excluded.reason,
            rejected_at = excluded.rejected_at
        """,
        (url, row_hash, reason, datetime.now(UTC).isoformat()),
    )
    conn.execute(f"DELETE FROM {NORMALISED_TABLE} WHERE url = ?", (url,))


def load_rejected_urls(conn: sqlite3.Connection) -> list[str]:
    """Every URL the pipeline has dropped; empty for a database it never ran on."""
    init_rejected_table(conn)
    return [row[0] for row in conn.execute(f"SELECT url FROM {REJECTED_TABLE}")]


def _model_rejections(conn: sqlite3.Connection) -> dict[str, str]:
    """URL to content_hash for pages the model has already ruled out, so an
    unchanged page does not spend LLM quota on every run."""
    cursor = conn.execute(
        f"SELECT url, content_hash FROM {REJECTED_TABLE} WHERE reason = ?", (MODEL_REJECTION,)
    )
    return {url: row_hash for url, row_hash in cursor.fetchall()}


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


def quota_exhausted(exc: BaseException) -> bool:
    """A provider saying the day's free quota is gone: retrying every remaining
    row would only burn time, so the run continues rules-only."""
    return getattr(exc, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(exc)


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
) -> PipelineStats:
    """Read every crawled row out of `db_path`, normalise it, and upsert the
    result into `normalised_opportunities` in the same file."""
    stats = PipelineStats()

    with sqlite3.connect(str(db_path)) as conn:
        init_normalised_table(conn)
        init_rejected_table(conn)
        existing = _existing_state(conn)
        model_rejected = _model_rejections(conn)
        rows = read_crawled_rows(conn)
        stats.rows_read = len(rows)

        for row in rows:
            row_hash = content_hash(row)
            reason = reject_reason(row)
            if reason is None and not force and model_rejected.get(row.url) == row_hash:
                reason = MODEL_REJECTION
            if reason is not None:
                _reject(conn, row.url, row_hash, reason)
                stats.rejected += 1
                continue

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
                    extracted = extractor.extract(row.title or "", row.url, row.raw_text or "")
                except Exception as exc:
                    logger.warning("LLM extraction failed for %s", row.url, exc_info=True)
                    stats.llm_failures += 1
                    if quota_exhausted(exc):
                        logger.warning("LLM quota exhausted; the rest of this run is rules-only")
                        stats.llm_quota_exhausted = True
                        extractor = None
                else:
                    stats.llm_calls += 1
                    if extracted.is_funding_opportunity is False:
                        _reject(conn, row.url, row_hash, MODEL_REJECTION)
                        stats.rejected += 1
                        continue
                    record = merge(record, extracted)
                    # A model-supplied deadline can turn a rule-only "active"
                    # record into a closed one (or vice versa); re-derive
                    # status so the two never disagree.
                    record.opportunity.status = derive_status(record.opportunity.deadline, today)

            conn.execute(f"DELETE FROM {REJECTED_TABLE} WHERE url = ?", (row.url,))
            stats.normalised += write_records(conn, [record])

        conn.commit()

    return stats
