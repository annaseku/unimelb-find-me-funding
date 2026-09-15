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
import sqlite3
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from backend.normaliser.llm import Extractor, merge
from backend.normaliser.models import CrawledRow, NormalisedRecord
from backend.normaliser.parsers import derive_status
from backend.normaliser.rules import content_hash, normalise_row
from backend.ranking.models import Opportunity

logger = logging.getLogger(__name__)

NORMALISED_TABLE = "normalised_opportunities"


@dataclass
class PipelineStats:
    rows_read: int = 0
    normalised: int = 0
    skipped_unchanged: int = 0
    llm_calls: int = 0
    llm_failures: int = 0


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


def read_crawled_rows(conn: sqlite3.Connection) -> list[CrawledRow]:
    """Every crawled row that fetched successfully (fetch_failed = 0)."""
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM opportunities WHERE fetch_failed = 0")
    return [CrawledRow(**dict(row)) for row in cursor.fetchall()]


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
                    extracted = extractor.extract(row.title or "", row.url, row.raw_text or "")
                except Exception:
                    logger.warning("LLM extraction failed for %s", row.url, exc_info=True)
                    stats.llm_failures += 1
                else:
                    record = merge(record, extracted)
                    # A model-supplied deadline can turn a rule-only "active"
                    # record into a closed one (or vice versa); re-derive
                    # status so the two never disagree.
                    record.opportunity.status = derive_status(record.opportunity.deadline, today)
                    stats.llm_calls += 1

            _upsert(conn, record)
            stats.normalised += 1

        conn.commit()

    return stats
