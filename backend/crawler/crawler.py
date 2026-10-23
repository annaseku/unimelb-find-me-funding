"""
Orchestration: ties query building, discovery, robots.txt checking,
fetching, extraction, and storage together into a single crawl run.

Run it from the repository root with `python3 main.py`; the weekly crawl
calls `run_crawl` from `backend/data/refresh.py`.
"""

import logging
import time

import requests

from backend.crawler.config import HEADERS, REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT
from backend.crawler.discover_url import discover_candidate_urls
from backend.crawler.extract import extract_fields
from backend.crawler.query_builder import generate_seed_queries
from backend.crawler.robot_check import is_allowed
from backend.crawler.storage import init_db, mark_fetch_failed, save_opportunity

logger = logging.getLogger(__name__)


def fetch_page(url: str) -> str | None:
    """Fetch raw HTML for a URL, returning None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        logger.warning("fetch failed for %s: %s", url, e)
        return None


def crawl_url(url: str, source_query: str) -> None:
    """Fetch, extract, and store a single URL -- if robots.txt allows it."""
    if not is_allowed(url):
        logger.info("skipping (robots.txt disallows): %s", url)
        return

    html = fetch_page(url)
    if html is None:
        mark_fetch_failed(url)
        return

    fields = extract_fields(html)
    save_opportunity(url, fields, source_query)
    logger.info("saved: %r (%s)", fields["title"][:60], url)

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
    logger.info("seed queries: %s", queries)

    candidates = discover_candidate_urls(queries)
    logger.info("discovered %d candidate URLs", len(candidates))

    for url, source_query in candidates.items():
        crawl_url(url, source_query)
