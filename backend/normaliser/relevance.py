"""Decides whether a crawled page is a funding opportunity at all, before it is
normalised and published. Search results for "<field> funding opportunity"
also return dictionary entries, encyclopedia articles, videos, journal home
pages and bot-check screens; none of those belong in the results.

Two layers. `page_reject_reason` looks only at the URL and title and rejects
only what is certain from those alone (a blocked site, a bot-check page), so
the publisher can apply it to records already in Postgres, which keep no page
text. `reject_reason` adds the checks that need the text. The LLM extractor's
own verdict is applied separately, in the pipeline."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from backend.normaliser.models import CrawledRow

# Sites that never host a funding opportunity of their own. A subdomain of an
# entry is blocked too, so youtube.com also covers m.youtube.com.
BLOCKED_DOMAINS: frozenset[str] = frozenset(
    {
        # Dictionaries and encyclopedias
        "wikipedia.org",
        "wiktionary.org",
        "britannica.com",
        "merriam-webster.com",
        "dictionary.cambridge.org",
        "dictionary.com",
        "collinsdictionary.com",
        # Video, social and Q&A
        "youtube.com",
        "youtu.be",
        "reddit.com",
        "quora.com",
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "x.com",
        "twitter.com",
        "tiktok.com",
        "pinterest.com",
        # App stores, podcasts and developer documentation. Listed by
        # subdomain: aws.amazon.com and research.google run research programmes.
        "apps.apple.com",
        "podcasts.apple.com",
        "developer.apple.com",
        "play.google.com",
        "dev.mysql.com",
        "postgresql.org",
        # Journals and paper indexes
        "sciencedirect.com",
        "springer.com",
        "onlinelibrary.wiley.com",
        "tandfonline.com",
        "mdpi.com",
        "researchgate.net",
        "jstor.org",
        "arxiv.org",
        "pmc.ncbi.nlm.nih.gov",
        "pubmed.ncbi.nlm.nih.gov",
    }
)

# Interstitials served instead of the page: bot checks, logins, errors.
_BLOCK_PAGE_TITLE_RE = re.compile(
    r"one moment, please|just a moment|access denied|attention required|"
    r"are you a (robot|human)|verify you are human|security check|captcha|"
    r"page not found|^\s*404\b",
    re.IGNORECASE,
)

# Most funding pages name what they offer in the title or the address. "fund"
# but not "fundamentals"; no trailing word boundary, so "GrantOpportunities"
# and "funding-schemes" in a path still count. A page without one ("MRFF
# Indigenous Health Research", "Reef Trust Partnership") needs stronger text.
_FUNDING_TERM_RE = re.compile(
    r"grant|fund(?!ament)|fellow|scholar|award|bursar|prize|stipend", re.IGNORECASE
)

# Things a page you can apply to says. A page needs at least
# MIN_APPLICATION_SIGNALS of these groups, not one term repeated.
_APPLICATION_SIGNALS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bappl(y|ying|ications?|icants?)\b", re.IGNORECASE),
    re.compile(r"\bdeadlines?\b|\bclos(e|es|ing)\b", re.IGNORECASE),
    re.compile(r"\beligib", re.IGNORECASE),
    re.compile(r"(\$|£|€|\b(AUD|USD|EUR|GBP)\s?)\d", re.IGNORECASE),
)

MIN_TEXT_CHARS = 200
MIN_APPLICATION_SIGNALS = 2
MIN_APPLICATION_SIGNALS_WITHOUT_FUNDING_TITLE = 3


def _host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host.removeprefix("www.")


def is_blocked_domain(url: str) -> bool:
    host = _host(url)
    return any(host == domain or host.endswith(f".{domain}") for domain in BLOCKED_DOMAINS)


def page_reject_reason(url: str, title: str | None) -> str | None:
    """Why the URL and title alone rule a page out, or None if they don't."""
    if is_blocked_domain(url):
        return f"blocked site: {_host(url)}"
    if title and _BLOCK_PAGE_TITLE_RE.search(title):
        return f"block page: {title.strip()[:60]}"
    return None


def reject_reason(row: CrawledRow) -> str | None:
    """Why a crawled page is not a funding opportunity, or None if it may be."""
    reason = page_reject_reason(row.url, row.title)
    if reason:
        return reason
    text = row.raw_text or ""
    if len(text) < MIN_TEXT_CHARS:
        return f"too little text ({len(text)} characters)"
    signals = sum(1 for pattern in _APPLICATION_SIGNALS if pattern.search(text))
    if signals < MIN_APPLICATION_SIGNALS:
        return "no application details (apply, deadline, eligibility or amount)"
    if not _FUNDING_TERM_RE.search(f"{row.title or ''} {row.url}"):
        if not _FUNDING_TERM_RE.search(text):
            return "no funding term in title, URL or text"
        if signals < MIN_APPLICATION_SIGNALS_WITHOUT_FUNDING_TITLE:
            return "no funding term in title or URL, and too few application details"
    return None
