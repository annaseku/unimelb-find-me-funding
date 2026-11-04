"""Seed a local SQLite fixture from the evals corpus.

Usage: python -m backend.evals.seed_sqlite [--repeat N] <db-path>
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Iterable
from contextlib import closing
from pathlib import Path

from backend.evals.corpus import corpus_records
from backend.normaliser.models import NormalisedRecord
from backend.normaliser.pipeline import write_records


def _expanded_records(
    records: Iterable[NormalisedRecord],
    multiplier: int,
) -> list[NormalisedRecord]:
    """Duplicate the seeded corpus so a local UI can exercise multi-page pagination."""
    if multiplier < 1:
        raise ValueError("repeat must be at least 1")
    base = list(records)
    expanded: list[NormalisedRecord] = []
    for repeat in range(multiplier):
        for record in base:
            clone = record.model_copy(deep=True)
            if repeat == 0:
                expanded.append(clone)
                continue
            opportunity = clone.opportunity
            opportunity.id = f"{opportunity.id}-demo-{repeat}"
            opportunity.title = f"{opportunity.title} (Demo {repeat})"
            opportunity.url = f"{opportunity.url}?demo={repeat}"
            if opportunity.source_urls:
                opportunity.source_urls = [
                    f"{source}?demo={repeat}" for source in opportunity.source_urls
                ]
            if opportunity.summary:
                opportunity.summary = f"{opportunity.summary} Demo round {repeat}."
            clone.content_hash = f"{clone.content_hash}-{repeat}"
            expanded.append(clone)
    return expanded


def seed(
    db_path: str | Path,
    records: Iterable[NormalisedRecord] | None = None,
    *,
    multiplier: int = 1,
) -> int:
    with closing(sqlite3.connect(str(db_path))) as conn, conn:
        source = corpus_records() if records is None else list(records)
        return write_records(conn, _expanded_records(source, multiplier))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed a SQLite fixture from the evals corpus")
    parser.add_argument("db_path", help="SQLite database to create or update.")
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Duplicate each corpus record this many times to simulate more search results.",
    )
    args = parser.parse_args(argv)
    written = seed(args.db_path, multiplier=args.repeat)
    print(f"seeded {written} opportunities into {args.db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
