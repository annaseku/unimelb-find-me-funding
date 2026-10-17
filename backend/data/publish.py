"""Publish a normalised crawler SQLite database to the deployed Postgres store.

Usage, from the repository root:

    export FMF_DATABASE_URL='postgresql://...pooler.supabase.com:5432/postgres'
    python -m backend.data.publish --db-path funding_crawler.db
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

import psycopg

from backend.data.postgres_repository import init_schema, upsert_records
from backend.normaliser.models import NormalisedRecord
from backend.normaliser.pipeline import load_normalised


def records_from_sqlite(db_path: str | Path) -> list[NormalisedRecord]:
    """Every normalised record in a crawler database."""
    with sqlite3.connect(str(db_path)) as conn:
        return load_normalised(conn)


def publish(database_url: str, records: list[NormalisedRecord]) -> int:
    """Create the table if needed, then upsert every record. Returns the count."""
    with psycopg.connect(database_url) as conn:
        init_schema(conn)
        written = upsert_records(conn, records)
        conn.commit()
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish opportunities to Postgres")
    parser.add_argument(
        "--db-path",
        default="funding_crawler.db",
        help="Normalised crawler SQLite database.",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("FMF_DATABASE_URL", ""),
        help="Defaults to FMF_DATABASE_URL.",
    )
    args = parser.parse_args(argv)

    if not args.database_url:
        parser.error("no database URL: pass --database-url or set FMF_DATABASE_URL")

    records = records_from_sqlite(args.db_path)
    written = publish(args.database_url, records)
    print(f"published {written} opportunities from {args.db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
