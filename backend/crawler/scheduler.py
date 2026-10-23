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

import logging
import time

from backend.crawler.config import SCHEDULER_POLL_INTERVAL_SECONDS, STALE_AFTER_DAYS
from backend.crawler.crawler import crawl_url, run_crawl
from backend.crawler.storage import get_stale_urls

logger = logging.getLogger(__name__)


def refresh_stale_opportunities() -> None:
    """Re-fetch and re-extract any opportunity whose data has gone stale."""
    stale_urls = get_stale_urls(STALE_AFTER_DAYS)
    logger.info("%d stale URLs to refresh", len(stale_urls))

    for url in stale_urls:
        crawl_url(url, source_query="refresh")


def run_scheduler_loop(search_profile: dict[str, str]) -> None:
    """
    Run forever: periodically refresh stale opportunities and re-run
    discovery for the given search profile.

    `search_profile` is the same kwargs dict accepted by
    `crawler.run_crawl` (field_of_research, type_of_activity, etc.).
    """
    while True:
        logger.info("sleeping %ds before next cycle", SCHEDULER_POLL_INTERVAL_SECONDS)
        time.sleep(SCHEDULER_POLL_INTERVAL_SECONDS)

        logger.info("refreshing stale opportunities")
        refresh_stale_opportunities()

        logger.info("re-running discovery for known profile")
        run_crawl(**search_profile)
