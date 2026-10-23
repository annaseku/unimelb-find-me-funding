"""Discovery turns search queries into a de-duplicated set of candidate pages."""

import pytest

from backend.crawler import discover_url


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    monkeypatch.setattr(discover_url.time, "sleep", lambda s: None)


def test_each_url_keeps_the_first_query_that_found_it(monkeypatch):
    results = {"q1": ["https://a.example", "https://b.example"], "q2": ["https://b.example"]}
    monkeypatch.setattr(discover_url, "search_google", lambda q: results[q])

    assert discover_url.discover_candidate_urls(["q1", "q2"]) == {
        "https://a.example": "q1",
        "https://b.example": "q1",
    }


def test_one_failed_search_does_not_stop_the_others(monkeypatch):
    def search(query):
        if query == "broken":
            raise RuntimeError("quota exceeded")
        return ["https://a.example"]

    monkeypatch.setattr(discover_url, "search_google", search)

    assert discover_url.discover_candidate_urls(["broken", "ok"]) == {"https://a.example": "ok"}


def test_searching_without_an_api_key_says_how_to_get_one(monkeypatch):
    monkeypatch.setattr(discover_url, "SERPAPI_API_KEY", None)
    with pytest.raises(RuntimeError, match="SERPAPI_API_KEY"):
        discover_url.search_google("reef research grant")
