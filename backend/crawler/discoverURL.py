"""
Discovery: turns search queries into candidate URLs.

Currently backed by DuckDuckGo's HTML search endpoint (no API key
required). Swap `search_duckduckgo` for a real search API (Bing/Google/
SerpAPI) later without touching the rest of the pipeline -- callers only
depend on `discover_candidate_urls`.
"""

import time

import requests
from bs4 import BeautifulSoup

from backend.crawler.config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY_SECONDS, MAX_RESULTS_PER_QUERY


def search_duckduckgo(query: str, max_results: int = MAX_RESULTS_PER_QUERY) -> list:
    """
    Run a query against DuckDuckGo's HTML-only search endpoint and return
    a list of result URLs.

    Not intended for high-volume/production use -- it's an unofficial
    endpoint and may break if DuckDuckGo changes their markup. Swap for a
    real search API when one is available.
    """
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    return [
        link.get("href")
        for link in soup.select("a.result__a")[:max_results]
        if link.get("href")
    ]


def discover_candidate_urls(seed_queries: list) -> dict:
    """
    Run discovery across all seed queries.

    Returns a dict of {url: source_query} rather than a plain set, so
    downstream storage can record which query surfaced each result --
    useful for debugging discovery quality later.
    """
    candidates = {}

    for query in seed_queries:
        try:
            for url in search_duckduckgo(query):
                # If a URL comes up under multiple queries, keep the first
                # query that found it.
                candidates.setdefault(url, query)
        except requests.RequestException as e:
            print(f"[discover] search failed for query {query!r}: {e}")
        time.sleep(REQUEST_DELAY_SECONDS)

    return candidates