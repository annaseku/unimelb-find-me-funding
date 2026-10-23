"""Refreshing goes back only to pages whose stored data has gone stale."""

from backend.crawler import scheduler


def test_refresh_recrawls_only_the_stale_urls(monkeypatch):
    asked = {}
    crawled = []

    def fake_stale(days):
        asked["days"] = days
        return ["https://a.example", "https://b.example"]

    monkeypatch.setattr(scheduler, "get_stale_urls", fake_stale)
    monkeypatch.setattr(scheduler, "crawl_url", lambda url, source_query: crawled.append(url))

    scheduler.refresh_stale_opportunities()

    assert asked["days"] == scheduler.STALE_AFTER_DAYS
    assert crawled == ["https://a.example", "https://b.example"]
