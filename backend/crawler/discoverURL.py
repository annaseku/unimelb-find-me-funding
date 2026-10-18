"""
Discovery: turns search queries into candidate URLs.

Uses SerpApi (https://serpapi.com) -- a real, documented search API --
instead of scraping DuckDuckGo's HTML page, which turned out to serve a
bot-detection page instead of real results when hit with a plain
server-side request (confirmed: status 202, response was DuckDuckGo's
homepage shell, not search results).

Requires a SERPAPI_API_KEY environment variable. Get a free key at
https://serpapi.com/manage-api-key, then set it with:
    export SERPAPI_API_KEY=your_key_here
"""

import os
import time

import serpapi

from backend.crawler.config import REQUEST_DELAY_SECONDS, MAX_RESULTS_PER_QUERY

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")


def search_google(query: str, max_results: int = MAX_RESULTS_PER_QUERY) -> list:
    """
    Run a query against Google Search via SerpApi and return a list of
    result URLs.
    """
    if not SERPAPI_API_KEY:
        raise RuntimeError(
            "SERPAPI_API_KEY environment variable is not set. "
            "Get a free key at https://serpapi.com/manage-api-key and "
            "set it with: export SERPAPI_API_KEY=your_key_here"
        )

    client = serpapi.Client(api_key=SERPAPI_API_KEY)
    # Search as google.com.au from Australia: unlocalised searches came back
    # almost entirely American.
    results = client.search(
        q=query,
        engine="google",
        num=max_results,
        google_domain="google.com.au",
        gl="au",
        hl="en",
    )

    organic_results = results.get("organic_results", [])
    return [r["link"] for r in organic_results[:max_results] if "link" in r]


def discover_candidate_urls(seed_queries: list) -> dict:
    """
    Run discovery across all seed queries.

    Returns a dict of {url: source_query}, so downstream storage can
    record which query surfaced each result.
    """
    candidates = {}

    for query in seed_queries:
        try:
            for url in search_google(query):
                candidates.setdefault(url, query)
        except Exception as e:
            print(f"[discover] search failed for query {query!r}: {e}")
        time.sleep(REQUEST_DELAY_SECONDS)

    return candidates