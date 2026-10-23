"""The robots.txt gate (KAN-49): our crawler fetches only what each site allows it to."""

from types import SimpleNamespace

import pytest
import requests

from backend.crawler import robot_check
from backend.crawler.config import HEADERS


@pytest.fixture(autouse=True)
def empty_cache():
    robot_check._robots_cache.clear()
    yield
    robot_check._robots_cache.clear()


def serve(monkeypatch, status=200, text="", error=None):
    calls = []

    def fake_get(url, headers, timeout):
        calls.append((url, headers))
        if error:
            raise error
        return SimpleNamespace(status_code=status, text=text)

    monkeypatch.setattr(robot_check.requests, "get", fake_get)
    return calls


def test_a_path_disallowed_for_every_crawler_is_not_fetched(monkeypatch):
    serve(monkeypatch, text="User-agent: *\nDisallow: /private/\n")
    assert not robot_check.is_allowed("https://funder.example/private/grant")
    assert robot_check.is_allowed("https://funder.example/grants/reef")


def test_rules_aimed_at_our_crawler_override_the_wildcard(monkeypatch):
    serve(
        monkeypatch,
        text="User-agent: FindMeFundingCrawler\nDisallow: /\n\nUser-agent: *\nAllow: /\n",
    )
    assert not robot_check.is_allowed("https://funder.example/grants/reef")


def test_robots_txt_is_requested_with_our_user_agent(monkeypatch):
    calls = serve(monkeypatch, text="")
    robot_check.is_allowed("https://funder.example/grants/reef")
    assert calls == [("https://funder.example/robots.txt", HEADERS)]


def test_a_missing_robots_txt_allows_crawling(monkeypatch):
    serve(monkeypatch, status=404)
    assert robot_check.is_allowed("https://funder.example/grants/reef")


@pytest.mark.parametrize("status", [500, 503])
def test_a_server_error_on_robots_txt_blocks_the_site(monkeypatch, status):
    serve(monkeypatch, status=status)
    assert not robot_check.is_allowed("https://funder.example/grants/reef")


def test_an_unreachable_robots_txt_blocks_the_site(monkeypatch):
    serve(monkeypatch, error=requests.ConnectionError("no route to host"))
    assert not robot_check.is_allowed("https://funder.example/grants/reef")


def test_robots_txt_is_fetched_once_per_site(monkeypatch):
    calls = serve(monkeypatch, text="User-agent: *\nDisallow: /private/\n")
    robot_check.is_allowed("https://funder.example/a")
    robot_check.is_allowed("https://funder.example/b")
    robot_check.is_allowed("https://other.example/a")
    assert [url for url, _ in calls] == [
        "https://funder.example/robots.txt",
        "https://other.example/robots.txt",
    ]
