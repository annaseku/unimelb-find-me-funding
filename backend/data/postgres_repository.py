"""Serves normalised opportunities out of a Postgres database, through the
same repository interface the mock- and SQLite-backed repositories already
implement, so switching the API's data source stays a one-line environment
change (see `get_repository` in backend/data/repository.py).

The table mirrors the crawler database's `normalised_opportunities` exactly,
with JSONB in place of the TEXT JSON columns, so `backend/data/publish.py`
can copy records across without reshaping them.

Deployment note: Render's network is IPv4-only and Supabase's direct
connection string resolves to IPv6, so FMF_DATABASE_URL must be a Supavisor
*session mode* pooler URL (port 5432, host aws-N-<region>.pooler.supabase.com).
Transaction mode (6543) does not support prepared statements, which psycopg
uses by default.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import errors
from psycopg.types.json import Jsonb

from backend.data.repository import OpportunityRepository
from backend.normaliser.models import NormalisedRecord
from backend.normaliser.pipeline import NORMALISED_TABLE
from backend.ranking.models import Opportunity

# Importing this module loads backend/.env, so FMF_DATABASE_URL can live in a
# file rather than an export in every shell. Both the API's postgres branch
# and publish.py reach Postgres through here, so one load covers both.
# load_dotenv never overrides a variable already set, which is what keeps
# Render's dashboard values authoritative in the deployed service.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def init_schema(conn: psycopg.Connection) -> None:
    """Create `normalised_opportunities` if it doesn't already exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {NORMALISED_TABLE} (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            content_hash TEXT NOT NULL,
            opportunity_json JSONB NOT NULL,
            provenance_json JSONB NOT NULL,
            used_llm BOOLEAN NOT NULL DEFAULT FALSE,
            normalised_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def upsert_records(conn: psycopg.Connection, records: Iterable[NormalisedRecord]) -> int:
    """Insert or refresh one batch of normalised records, keyed on URL to
    match the SQLite pipeline's upsert semantics. Returns the row count."""
    rows = [
        (
            record.opportunity.id,
            record.opportunity.url,
            record.content_hash,
            Jsonb(record.opportunity.model_dump(mode="json")),
            Jsonb(record.provenance),
            record.used_llm,
        )
        for record in records
    ]
    if not rows:
        return 0

    conn.cursor().executemany(
        f"""
        INSERT INTO {NORMALISED_TABLE} (
            id, url, content_hash, opportunity_json, provenance_json, used_llm, normalised_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, now())
        ON CONFLICT (url) DO UPDATE SET
            id = excluded.id,
            content_hash = excluded.content_hash,
            opportunity_json = excluded.opportunity_json,
            provenance_json = excluded.provenance_json,
            used_llm = excluded.used_llm,
            normalised_at = excluded.normalised_at
        """,
        rows,
    )
    return len(rows)


class PostgresRepository(OpportunityRepository):
    """Loads every row from `normalised_opportunities` once, at construction
    time, exactly as SqliteRepository does. A database that has not been
    migrated yet (the table doesn't exist) yields an empty repository rather
    than raising, so a fresh deployment serves zero results instead of 500s."""

    def __init__(self, database_url: str) -> None:
        super().__init__(self._load(database_url))

    @staticmethod
    def _load(database_url: str) -> list[Opportunity]:
        with psycopg.connect(database_url) as conn:
            try:
                cursor = conn.execute(f"SELECT opportunity_json FROM {NORMALISED_TABLE}")
            except errors.UndefinedTable:
                return []
            # JSONB comes back already decoded, so there is no json.loads here.
            return [Opportunity(**row[0]) for row in cursor.fetchall()]
