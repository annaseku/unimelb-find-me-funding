"""Crawl a rotating research-area slice, normalise it and publish to Postgres.

Run from the repository root: python -m backend.data.refresh [--all] [--dry-run].
The crawler always writes config.DB_PATH relative to the current directory;
--db-path selects the database to normalise and publish, not the crawler output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from pydantic import BaseModel

from backend.crawler.config import DB_PATH
from backend.crawler.queryBuilder import generate_seed_queries
from backend.data.publish import publish, records_from_sqlite
from backend.normaliser.llm import extractor_from_env
from backend.normaliser.pipeline import PipelineStats, normalise_database

SEED_FILE = Path(__file__).with_name("seed_profiles.json")


class SeedProfile(BaseModel):
    for_division: str
    field_of_research: str


@dataclass
class RefreshStats:
    profiles: list[str]
    crawled: int
    normalised: PipelineStats | None
    published: int


def load_seed_profiles(path: Path = SEED_FILE) -> list[SeedProfile]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [SeedProfile.model_validate(profile) for profile in payload["profiles"]]


def select_profiles(profiles: list[SeedProfile], week: int, per_run: int) -> list[SeedProfile]:
    if per_run <= 0:
        raise ValueError("per_run must be positive")
    if per_run >= len(profiles):
        return profiles[:]
    start = (week * per_run) % len(profiles)
    return [profiles[(start + offset) % len(profiles)] for offset in range(per_run)]


def crawl(profiles: list[SeedProfile]) -> None:
    # Discovery reads its API key on import; keep it out of dry-runs and tests.
    from backend.crawler.crawler import run_crawl

    for profile in profiles:
        run_crawl(field_of_research=profile.field_of_research)


def normalise(db_path: str | Path, today: date, use_llm: bool) -> PipelineStats:
    extractor = extractor_from_env() if use_llm else None
    return normalise_database(db_path, today, extractor=extractor)


def publish_to_postgres(db_path: str | Path, database_url: str) -> int:
    return publish(database_url, records_from_sqlite(db_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl, normalise and publish funding opportunities from the repository root."
    )
    parser.add_argument("--all", action="store_true", help="Crawl every seed research area.")
    parser.add_argument("--per-run", type=int, default=10, help="Profiles per run (default: 10).")
    parser.add_argument("--week", type=int, default=date.today().isocalendar().week)
    parser.add_argument(
        "--db-path",
        default=DB_PATH,
        help="Database to normalise and publish; crawler output always uses config.DB_PATH.",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("FMF_DATABASE_URL", ""),
        help="Defaults to FMF_DATABASE_URL.",
    )
    parser.add_argument("--no-llm", action="store_true", help="Skip the Gemini extractor.")
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Crawl and normalise only, leaving the result in the local SQLite database.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print profiles and SerpApi search count only."
    )
    args = parser.parse_args(argv)
    if args.per_run <= 0:
        parser.error("--per-run must be positive")

    profiles = load_seed_profiles()
    selected = profiles if args.all else select_profiles(profiles, args.week, args.per_run)
    if args.dry_run:
        for profile in selected:
            print(f"{profile.for_division}: {profile.field_of_research}")
        searches = sum(
            len(generate_seed_queries(field_of_research=p.field_of_research)) for p in selected
        )
        print(f"SerpApi searches: {searches}")
        return 0

    if not os.environ.get("SERPAPI_API_KEY", "").strip():
        print("no SerpApi key: set SERPAPI_API_KEY before crawling", file=sys.stderr)
        return 2
    if not args.skip_publish and not args.database_url.strip():
        print("no database URL: pass --database-url or set FMF_DATABASE_URL", file=sys.stderr)
        return 2

    crawl(selected)
    normalised = normalise(args.db_path, date.today(), use_llm=not args.no_llm)
    published = 0 if args.skip_publish else publish_to_postgres(args.db_path, args.database_url)
    stats = RefreshStats(
        profiles=[p.field_of_research for p in selected],
        crawled=len(selected),
        normalised=normalised,
        published=published,
    )
    print(f"profiles crawled: {stats.crawled}")
    print(f"normalised: {normalised.normalised}")
    if args.skip_publish:
        print(f"not published: serve with FMF_DATA_SOURCE=sqlite FMF_DB_PATH={args.db_path}")
    else:
        print(f"published: {stats.published}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
