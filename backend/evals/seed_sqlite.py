"""Seed a local SQLite fixture from the evals corpus.

Usage: python -m backend.evals.seed_sqlite <db-path>
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Iterable
from pathlib import Path

from backend.evals.corpus import corpus_records
from backend.normaliser.models import NormalisedRecord
from backend.normaliser.pipeline import write_records


def seed(db_path: str | Path, records: Iterable[NormalisedRecord] | None = None) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        return write_records(conn, corpus_records() if records is None else records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed a SQLite fixture from the evals corpus")
    parser.add_argument("db_path", help="SQLite database to create or update.")
    args = parser.parse_args(argv)
    written = seed(args.db_path)
    print(f"seeded {written} opportunities into {args.db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
