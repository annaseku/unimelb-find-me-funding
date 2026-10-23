"""The crawl loop fetches only what robots.txt allows and records what happened to each URL."""

from types import SimpleNamespace

import pytest
import requests

from backend.crawler import crawler

URL = "https://funder.example/grants/reef"
PAGE = "<html><head><title>Reef Grant</title></head><body><main>Apply now.</main></body></html>"


@pytest.fixture
def calls(monkeypatch):
    """Replace the crawler's side effects with recorders."""
    log = {"fetched": [], "saved": [], "failed": [], "slept": []}
    monkeypatch.setattr(crawler, "is_allowed", lambda url: True)
    monkeypatch.setattr(crawler, "fetch_page", lambda url: log["fetched"].append(url) or PAGE)
    monkeypatch.setattr(
        crawler, "save_opportunity", lambda url, fields, q: log["saved"].append((url, fields, q))
    )
    monkeypatch.setattr(crawler, "mark_fetch_failed", lambda url: log["failed"].append(url))
    monkeypatch.setattr(crawler.time, "sleep", lambda s: log["slept"].append(s))
    return log


def test_a_url_robots_txt_disallows_is_never_fetched(monkeypatch, calls):
    monkeypatch.setattr(crawler, "is_allowed", lambda url: False)
    crawler.crawl_url(URL, "reef research grant")
    assert calls["fetched"] == [] and calls["saved"] == []


def test_a_failed_fetch_is_recorded_and_nothing_is_saved(monkeypatch, calls):
    monkeypatch.setattr(crawler, "fetch_page", lambda url: None)
    crawler.crawl_url(URL, "reef research grant")
    assert calls["failed"] == [URL] and calls["saved"] == []


def test_a_fetched_page_is_saved_with_its_query_then_the_crawler_pauses(calls):
    crawler.crawl_url(URL, "reef research grant")
    [(url, fields, query)] = calls["saved"]
    assert (url, fields["title"], query) == (URL, "Reef Grant", "reef research grant")
    assert calls["slept"] == [crawler.REQUEST_DELAY_SECONDS]


def test_fetch_page_returns_the_html_with_our_user_agent(monkeypatch):
    seen = {}

    def fake_get(url, headers, timeout):
        seen["headers"] = headers
        return SimpleNamespace(text=PAGE, raise_for_status=lambda: None)

    monkeypatch.setattr(crawler.requests, "get", fake_get)
    assert crawler.fetch_page(URL) == PAGE
    assert seen["headers"] == crawler.HEADERS


def test_fetch_page_returns_none_when_the_request_fails(monkeypatch):
    def fake_get(url, headers, timeout):
        raise requests.Timeout("too slow")

    monkeypatch.setattr(crawler.requests, "get", fake_get)
    assert crawler.fetch_page(URL) is None


def test_run_crawl_crawls_every_discovered_url_with_the_query_that_found_it(monkeypatch):
    crawled = []
    monkeypatch.setattr(crawler, "init_db", lambda: None)
    monkeypatch.setattr(crawler, "generate_seed_queries", lambda **profile: ["q1", "q2"])
    monkeypatch.setattr(
        crawler,
        "discover_candidate_urls",
        lambda queries: {"https://a.example": "q1", "https://b.example": "q2"},
    )
    monkeypatch.setattr(crawler, "crawl_url", lambda url, q: crawled.append((url, q)))

    crawler.run_crawl(field_of_research="marine biology")

    assert crawled == [("https://a.example", "q1"), ("https://b.example", "q2")]
