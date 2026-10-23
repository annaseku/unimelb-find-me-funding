"""
Entry point for running the crawler from the repository root.

Usage:
    python3 main.py                 # run once, using the example profile below
    python3 main.py --schedule      # run once, then keep re-crawling on a loop
"""

import argparse
import logging

from backend.crawler.crawler import run_crawl
from backend.crawler.scheduler import run_scheduler_loop

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Funding opportunity crawler")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="keep re-crawling on a loop after the first run",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # Example profile for a manual run; the weekly crawl uses backend/data/refresh.py.
    example_profile = {
        "field_of_research": "marine biology",
        "type_of_activity": "experimental research",
        "career_stage": "postdoc_2_5",
        "funding_type": "equipment",
        "free_text_description": "coral reef resilience to ocean acidification",
    }

    run_crawl(**example_profile)

    if args.schedule:
        run_scheduler_loop(example_profile)
