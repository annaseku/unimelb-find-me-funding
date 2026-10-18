"""Tests for backend.normaliser.relevance: telling funding pages apart from
the dictionary entries, videos, bot-check screens and news pages that real
crawls return alongside them."""

from __future__ import annotations

import pytest

from backend.normaliser.models import CrawledRow
from backend.normaliser.relevance import is_blocked_domain, page_reject_reason, reject_reason
from backend.normaliser.rules import load_fixture_rows

NEWS_URL = "https://www.example-news.org/2026/07/university-announces-new-lab"

FUNDING_TEXT = (
    "The scheme supports early-career researchers with grants of up to $500,000. "
    "Applicants must hold a PhD awarded in the last five years. Eligibility is limited "
    "to researchers employed at an Australian university. Applications close on "
    "1 March 2027 and must be submitted through the research office."
)


def _row(url: str, title: str, text: str = FUNDING_TEXT) -> CrawledRow:
    return CrawledRow(url=url, title=title, raw_text=text)


def test_every_fixture_funding_page_passes_and_the_news_page_is_rejected():
    reasons = {row.url: reject_reason(row) for row in load_fixture_rows()}
    assert reasons.pop(NEWS_URL) is not None
    assert reasons and all(reason is None for reason in reasons.values())


@pytest.mark.parametrize(
    "url",
    [
        "https://en.wikipedia.org/wiki/Funding",
        "https://www.youtube.com/watch?v=9fm-_FKxZ_g",
        "https://m.youtube.com/watch?v=9fm-_FKxZ_g",
        "https://www.merriam-webster.com/dictionary/opportunity",
        "https://dev.mysql.com/doc/en/grant.html",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC3004979/",
    ],
)
def test_blocked_sites_are_rejected_on_the_url_alone(url):
    assert is_blocked_domain(url)
    assert page_reject_reason(url, "Research grant funding") is not None


@pytest.mark.parametrize(
    "url",
    [
        "https://aws.amazon.com/government-education/research-and-technical-computing/cloud-credit-for-research/",
        "https://www.arc.gov.au/funding-research/funding-schemes",
        # A lookalike host is not a subdomain of a blocked one.
        "https://notwikipedia.org/grants",
    ],
)
def test_research_programmes_on_unblocked_hosts_are_not_blocked(url):
    assert not is_blocked_domain(url)


@pytest.mark.parametrize("title", ["One moment, please...", "Just a moment...", "404 Not Found"])
def test_bot_check_and_error_pages_are_rejected(title):
    assert page_reject_reason("https://www.lms.ac.uk/grants/other-sources", title) is not None


def test_a_page_with_almost_no_text_is_rejected():
    reason = reject_reason(
        _row("https://www.grants.gov/search-results-detail/56210", "Lock", "Lock")
    )
    assert reason is not None and "too little text" in reason


def test_a_funding_titled_page_without_application_details_is_rejected():
    text = "Grant Lee Phillips is a singer-songwriter from California. " * 6
    reason = reject_reason(_row("https://www.grantleephillips.com/", "GRANT-LEE PHILLIPS", text))
    assert reason is not None and "no application details" in reason


def test_fundamentals_is_not_a_funding_term():
    text = "Schools apply SEL programs. Eligible schools close the gap on $1,000 costs. " * 4
    url = "https://casel.org/fundamentals-of-sel/what-does-the-research-say/"
    reason = reject_reason(_row(url, "Does SEL Work?", text))
    assert reason == "no funding term in title, URL or text"


def test_a_scheme_named_by_acronym_passes_on_strong_text():
    row = _row(
        "https://www.health.gov.au/our-work/mrff-indigenous-health-research",
        "MRFF Indigenous Health Research 2026",
    )
    assert reject_reason(row) is None


def test_without_a_funding_title_two_application_details_are_not_enough():
    text = "Funding for our members. Applications are open to everyone who is eligible. " * 4
    row = _row("https://opportunity.org/", "Opportunity International", text)
    assert reject_reason(row) is not None
    # The same text under a funding title passes.
    assert reject_reason(_row("https://opportunity.org/grants", "Member grants", text)) is None
