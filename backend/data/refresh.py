"""Crawl a rotating research-area slice, normalise it and publish to Postgres.

Run from the repository root: python -m backend.data.refresh [--all | --refetch] [--dry-run].
The crawler always writes config.DB_PATH relative to the current directory;
--db-path selects the database to normalise and publish, not the crawler output.
Refetch requires those paths to match so failed pages cannot publish cached records.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import psycopg
from pydantic import BaseModel

from backend.crawler.config import DB_PATH
from backend.crawler.queryBuilder import generate_seed_queries
from backend.data.postgres_repository import read_published_urls
from backend.data.publish import latest_run_from_sqlite, publish, records_from_sqlite
from backend.normaliser.llm import extractor_from_env
from backend.normaliser.pipeline import NORMALISED_TABLE, PipelineStats, normalise_database

SEED_FILE = Path(__file__).with_name("seed_profiles.json")
# A serial refetch of 668 pages took about 1.5 hours (KAN-71).
FETCH_WORKERS = 8
LLM_WORKERS = 8


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


def refetch(urls: list[str]) -> tuple[int, int]:
    """Re-fetch published pages into config.DB_PATH; return fetched and failed counts."""
    from backend.crawler.crawler import crawl_url, init_db

    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        # The crawler only marks failures on existing rows. Pending rows also
        # keep robots.txt rejections from reusing a previous successful fetch.
        conn.executemany(
            """INSERT INTO opportunities (url, fetch_failed) VALUES (?, 1)
            ON CONFLICT(url) DO UPDATE SET fetch_failed = 1""",
            ((url,) for url in urls),
        )
        if conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (NORMALISED_TABLE,)
        ).fetchone():
            # Re-run current rules even if the page is unchanged, and never
            # republish a failed URL's cached normalised record.
            conn.executemany(
                f"DELETE FROM {NORMALISED_TABLE} WHERE url = ?", ((url,) for url in urls)
            )

    # One site's pages stay sequential, keeping the crawler's per-request
    # delay towards each host; different sites are fetched in parallel.
    by_host: dict[str, list[str]] = defaultdict(list)
    for url in urls:
        by_host[urlsplit(url).netloc.lower()].append(url)

    def fetch_host(host_urls: list[str]) -> None:
        for url in host_urls:
            crawl_url(url, source_query="refetch")

    with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as pool:
        list(pool.map(fetch_host, by_host.values()))

    with sqlite3.connect(DB_PATH) as conn:
        states = dict(conn.execute("SELECT url, fetch_failed FROM opportunities"))
    return sum(states[url] == 0 for url in urls), sum(states[url] != 0 for url in urls)


def normalise(db_path: str | Path, today: date, use_llm: bool) -> PipelineStats:
    extractor = extractor_from_env() if use_llm else None
    return normalise_database(db_path, today, extractor=extractor, llm_workers=LLM_WORKERS)


def publish_to_postgres(db_path: str | Path, database_url: str) -> int:
    return publish(database_url, records_from_sqlite(db_path), latest_run_from_sqlite(db_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl, normalise and publish funding opportunities from the repository root."
    )
    parser.add_argument("--all", action="store_true", help="Crawl every seed research area.")
    parser.add_argument(
        "--refetch",
        action="store_true",
        help="Re-fetch every published URL through the current extractor without SerpApi searches.",
    )
    parser.add_argument("--per-run", type=int, default=10, help="Profiles per run (default: 10).")
    parser.add_argument("--week", type=int, help="Rotation slot (default: current ISO week).")
    parser.add_argument(
        "--db-path",
        default=DB_PATH,
        help="Database to normalise and publish; must match config.DB_PATH for --refetch.",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("FMF_DATABASE_URL", ""),
        help="Defaults to FMF_DATABASE_URL.",
    )
    parser.add_argument("--no-llm", action="store_true", help="Skip the LLM extractor.")
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Crawl and normalise only, leaving the result in the local SQLite database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print profiles and SerpApi search count, or the published URL count with --refetch.",
    )
    args = parser.parse_args(argv)
    if args.per_run <= 0:
        parser.error("--per-run must be positive")
    if args.refetch and (args.all or args.week is not None):
        parser.error("--refetch cannot be combined with --all or --week")

    selected = []
    if args.refetch:
        if not args.database_url.strip():
            print("no database URL: pass --database-url or set FMF_DATABASE_URL", file=sys.stderr)
            return 2
        if not args.dry_run and Path(args.db_path).resolve() != Path(DB_PATH).resolve():
            parser.error(f"--refetch requires --db-path to match crawler output: {DB_PATH}")
        try:
            urls = read_published_urls(args.database_url)
        except psycopg.Error as exc:
            print(f"could not read published URLs: {exc}", file=sys.stderr)
            return 2
        print(f"urls: {len(urls)}")
        if args.dry_run:
            return 0
        fetched, failed = refetch(urls)
        print(f"fetched: {fetched}")
        print(f"fetch failed: {failed}")
    else:
        profiles = load_seed_profiles()
        week = args.week if args.week is not None else date.today().isocalendar().week
        selected = profiles if args.all else select_profiles(profiles, week, args.per_run)
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
    if not args.refetch:
        print(f"profiles crawled: {stats.crawled}")
    print(f"normalised: {normalised.normalised}")
    print(
        f"llm calls: {normalised.llm_calls}, failures: {normalised.llm_failures}, "
        f"rate-limit waits: {normalised.rate_limit_waits}, "
        f"stopped: {normalised.llm_stop_reason or 'no'}"
    )
    if args.skip_publish:
        print(f"not published: serve with FMF_DATA_SOURCE=sqlite FMF_DB_PATH={args.db_path}")
    else:
        print(f"published: {stats.published}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
