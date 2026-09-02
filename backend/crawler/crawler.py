"""
Orchestration: ties query building, discovery, robots.txt checking,
fetching, extraction, and storage together into a single crawl run.

Usage:
    python crawler.py                 # run once, using the example profile below
    python crawler.py --schedule      # run once, then keep re-crawling on a loop
"""

import argparse
import time

import requests

from backend.crawler.config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY_SECONDS
from backend.crawler.queryBuilder import generate_seed_queries
from backend.crawler.discoverURL import discover_candidate_urls
from backend.crawler.robotCheck import is_allowed
from backend.crawler.extract import extract_fields
from backend.crawler.storage import init_db, save_opportunity, mark_fetch_failed


def fetch_page(url: str):
    """Fetch raw HTML for a URL, returning None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"[fetch] failed for {url}: {e}")
        return None


def crawl_url(url: str, source_query: str) -> None:
    """Fetch, extract, and store a single URL -- if robots.txt allows it."""
    if not is_allowed(url):
        print(f"[crawl] skipping (robots.txt disallows): {url}")
        return

    html = fetch_page(url)
    if html is None:
        mark_fetch_failed(url)
        return

    fields = extract_fields(html)
    save_opportunity(url, fields, source_query)
    print(f"[crawl] saved: {fields['title'][:60]!r} ({url})")

    time.sleep(REQUEST_DELAY_SECONDS)


def run_crawl(
    field_of_research: str,
    type_of_activity: str = "",
    career_stage: str = "",
    funding_type: str = "",
    free_text_description: str = "",
) -> None:
    """
    End-to-end crawl for one search profile: build queries -> discover
    URLs -> respect robots.txt -> fetch -> extract -> store.
    """
    init_db()

    queries = generate_seed_queries(
        field_of_research=field_of_research,
        type_of_activity=type_of_activity,
        career_stage=career_stage,
        funding_type=funding_type,
        free_text_description=free_text_description,
    )
    print(f"[run_crawl] seed queries: {queries}")

    candidates = discover_candidate_urls(queries)
    print(f"[run_crawl] discovered {len(candidates)} candidate URLs")

    for url, source_query in candidates.items():
        crawl_url(url, source_query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Funding opportunity crawler")
    parser.add_argument(
        "--schedule", action="store_true",
        help="keep re-crawling on a loop after the first run",
    )
    args = parser.parse_args()

    # Example manual profile -- replace with real user input once the API layer exists
    example_profile = {
        "field_of_research": "marine biology",
        "type_of_activity": "experimental research",
        "career_stage": "postdoc_2_5",
        "funding_type": "equipment",
        "free_text_description": "coral reef resilience to ocean acidification",
    }

    run_crawl(**example_profile)

    if args.schedule:
        from backend.crawler.scheduler import run_scheduler_loop
        run_scheduler_loop(example_profile)