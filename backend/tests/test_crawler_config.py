import re

from backend.crawler.config import HEADERS


def test_user_agent_names_the_crawler_and_links_the_project():
    ua = HEADERS["User-Agent"]
    assert ua.startswith("FindMeFundingCrawler/")
    assert "+https://github.com/annaseku/unimelb-find-me-funding" in ua


def test_user_agent_publishes_no_email_address():
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", HEADERS["User-Agent"])
