"""
Periodic re-crawl scheduling.

Two responsibilities:
  1. Refresh individual opportunities once their stored data goes stale
     (re-fetch + re-extract the same URL).
  2. Periodically re-run full discovery for known search profiles, so new
     funding pages that weren't found before get picked up.

For a class project this simple loop is enough; in a real deployment
you'd more likely run this via a proper scheduler (cron, Celery beat,
etc.) rather than a long-lived Python process.
"""

import time

from backend.crawler.config import SCHEDULER_POLL_INTERVAL_SECONDS, STALE_AFTER_DAYS
from backend.crawler.extract import extract_fields
from backend.crawler.robot_check import is_allowed
from backend.crawler.storage import get_stale_urls, mark_fetch_failed, save_opportunity


def refresh_stale_opportunities() -> None:
    """Re-fetch and re-extract any opportunity whose data has gone stale."""
    from backend.crawler.crawler import fetch_page  # local import avoids a circular import

    stale_urls = get_stale_urls(STALE_AFTER_DAYS)
    print(f"[scheduler] {len(stale_urls)} stale URLs to refresh")

    for url in stale_urls:
        if not is_allowed(url):
            continue
        html = fetch_page(url)
        if html is None:
            mark_fetch_failed(url)
            continue
        fields = extract_fields(html)
        save_opportunity(url, fields, source_query="refresh")


def run_scheduler_loop(search_profile: dict) -> None:
    """
    Run forever: periodically refresh stale opportunities and re-run
    discovery for the given search profile.

    `search_profile` is the same kwargs dict accepted by
    `crawler.run_crawl` (field_of_research, type_of_activity, etc.).
    """
    from backend.crawler.crawler import run_crawl  # local import avoids a circular import

    while True:
        print(f"[scheduler] sleeping {SCHEDULER_POLL_INTERVAL_SECONDS}s before next cycle")
        time.sleep(SCHEDULER_POLL_INTERVAL_SECONDS)

        print("[scheduler] refreshing stale opportunities")
        refresh_stale_opportunities()

        print("[scheduler] re-running discovery for known profile")
        run_crawl(**search_profile)
