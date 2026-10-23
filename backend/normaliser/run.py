"""Command-line entry point for the normaliser pipeline.

Usage, from the repository root:

    python -m backend.normaliser.run [--db PATH] [--today YYYY-MM-DD] [--no-llm] [--force]
"""

from __future__ import annotations

import argparse
import logging
from datetime import date

from backend.crawler.config import DB_PATH
from backend.normaliser.llm import extractor_from_env
from backend.normaliser.pipeline import normalise_database


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Normalise crawled rows into structured funding opportunities."
    )
    parser.add_argument("--db", default=DB_PATH, help="Path to the crawler's SQLite database.")
    parser.add_argument(
        "--today",
        type=_parse_date,
        default=date.today(),
        help="Reference date for deadline status, YYYY-MM-DD (default: today).",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip the LLM extractor even if OPENROUTER_API_KEY is set.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-normalise every row, even ones whose content hasn't changed.",
    )
    args = parser.parse_args()

    extractor = None if args.no_llm else extractor_from_env()

    stats = normalise_database(args.db, args.today, extractor=extractor, force=args.force)

    # run.py is a CLI script: print is the deliberate exception to the
    # project-wide "log, don't print" rule.
    print(f"rows read: {stats.rows_read}")
    print(f"normalised: {stats.normalised}")
    print(f"skipped unchanged: {stats.skipped_unchanged}")
    print(f"llm calls: {stats.llm_calls}")
    print(f"llm failures: {stats.llm_failures}")
    print(f"API data source: FMF_DATA_SOURCE=sqlite FMF_DB_PATH={args.db}")


if __name__ == "__main__":
    main()
