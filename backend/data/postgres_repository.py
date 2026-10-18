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

import json
from collections.abc import Iterable
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import errors
from psycopg.types.json import Jsonb

from backend.data.repository import OpportunityRepository
from backend.normaliser.models import NormalisedRecord, PipelineRun
from backend.normaliser.pipeline import NORMALISED_TABLE, RUNS_TABLE
from backend.ranking.models import Opportunity

# Importing this module loads backend/.env, so FMF_DATABASE_URL can live in a
# file rather than an export in every shell. Both the API's postgres branch
# and publish.py reach Postgres through here, so one load covers both.
# load_dotenv never overrides a variable already set, which is what keeps
# Render's dashboard values authoritative in the deployed service.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def init_schema(conn: psycopg.Connection) -> None:
    """Create `normalised_opportunities` and `pipeline_runs` if they don't already exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RUNS_TABLE} (
            finished_at TIMESTAMPTZ NOT NULL,
            run_json JSONB NOT NULL
        )
        """
    )
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


def _dumps_without_nul(obj: object) -> str:
    """jsonb cannot hold \\u0000, which a crawled binary page can leave in a
    text field; the normaliser strips NUL on read, this is the last line."""
    return json.dumps(obj).replace("\\u0000", "")


def upsert_records(conn: psycopg.Connection, records: Iterable[NormalisedRecord]) -> int:
    """Insert or refresh one batch of normalised records, keyed on URL to
    match the SQLite pipeline's upsert semantics. Returns the row count."""
    rows = [
        (
            record.opportunity.id,
            record.opportunity.url,
            record.content_hash,
            Jsonb(record.opportunity.model_dump(mode="json"), dumps=_dumps_without_nul),
            Jsonb(record.provenance, dumps=_dumps_without_nul),
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


def insert_run(conn: psycopg.Connection, run: PipelineRun) -> None:
    conn.execute(
        f"INSERT INTO {RUNS_TABLE} (finished_at, run_json) VALUES (%s, %s)",
        (run.finished_at, Jsonb(run.model_dump(mode="json"))),
    )


class PostgresRepository(OpportunityRepository):
    """Loads every row from `normalised_opportunities` once, at construction
    time, exactly as SqliteRepository does. A database that has not been
    migrated yet (the table doesn't exist) yields an empty repository rather
    than raising, so a fresh deployment serves zero results instead of 500s."""

    def __init__(self, database_url: str) -> None:
        opportunities, last_run, rule_only = self._load(database_url)
        super().__init__(opportunities, last_run, rule_only)

    @staticmethod
    def _load(database_url: str) -> tuple[list[Opportunity], PipelineRun | None, int]:
        with psycopg.connect(database_url) as conn:
            try:
                row = conn.execute(
                    f"SELECT run_json FROM {RUNS_TABLE} ORDER BY finished_at DESC LIMIT 1"
                ).fetchone()
                last_run = PipelineRun.model_validate(row[0]) if row else None
            except errors.UndefinedTable:
                conn.rollback()
                last_run = None
            try:
                cursor = conn.execute(
                    f"SELECT opportunity_json, provenance_json->>'summary' FROM {NORMALISED_TABLE}"
                )
            except errors.UndefinedTable:
                return [], last_run, 0
            rows = cursor.fetchall()
            # JSONB comes back already decoded, so there is no json.loads here.
            opportunities = [Opportunity(**row[0]) for row in rows]
            return opportunities, last_run, sum(row[1] != "llm" for row in rows)
