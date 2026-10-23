"""
Structured field extraction: pulls title, deadline, funding amount, and
an eligibility text snippet out of raw page content.

These are deliberately kept as *raw extracted signals* here, not final
classifications -- e.g. we extract a deadline date if we can parse one,
and a funding-amount figure if we can find one, but banding those into
the client's ranking categories ("<15 days", "$1-2M" etc.) is the
matching/ranking engine's job, not the crawler's.
"""

import re
from datetime import datetime

from bs4 import BeautifulSoup

try:
    from dateutil import parser as dateutil_parser

    _HAVE_DATEUTIL = True
except ImportError:
    _HAVE_DATEUTIL = False

# --- Regex patterns ----------------------------------------------------------

# Looks for a labelled deadline/closing-date phrase followed by a date-like
# string. Intentionally broad -- false positives get filtered by the date
# parse step below.
_DEADLINE_LABEL_RE = re.compile(
    r"(deadline|closing date|closes on|apply by|applications close)\s*[:\-]?\s*"
    r"([A-Za-z0-9,\s/\-]{6,40})",
    re.IGNORECASE,
)

# Matches dollar figures like "$500,000", "$1.2 million", "AUD 2,000,000"
_AMOUNT_RE = re.compile(
    r"(AUD|A\$|\$)\s?([\d,]+(?:\.\d+)?)\s?(million|m|k)?",
    re.IGNORECASE,
)

# How much surrounding context to keep around an "eligib..." mention.
_ELIGIBILITY_CONTEXT_CHARS = 300


def extract_title_and_text(html: str):
    """Extract page title and cleaned, whitespace-collapsed body text."""
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
    for tag in soup.select('[role="navigation"], [role="banner"], [role="contentinfo"]'):
        tag.decompose()

    # Menus and footers otherwise lead the text and end up as the summary.
    body = soup.find("main") or soup.find(attrs={"role": "main"}) or soup.find("article") or soup
    text = " ".join(body.get_text(separator=" ").split())
    return title, text


def extract_deadline(text: str):
    """
    Look for a deadline/closing-date phrase in the page text.

    Returns (raw_matched_text, parsed_iso_date). Either or both may be
    None if nothing is found or the matched text isn't a parseable date.
    """
    match = _DEADLINE_LABEL_RE.search(text)
    if not match:
        return None, None

    raw = match.group(2).strip()

    parsed_iso = None
    if _HAVE_DATEUTIL:
        try:
            parsed_date = dateutil_parser.parse(raw, fuzzy=True, default=datetime(1900, 1, 1))
            # Reject obviously-wrong parses (e.g. dateutil grabbing a
            # stray number as a year) by requiring a "sane" year range.
            if 2020 <= parsed_date.year <= 2100:
                parsed_iso = parsed_date.date().isoformat()
        except (ValueError, OverflowError):
            pass

    return raw, parsed_iso


def extract_funding_amount(text: str):
    """
    Look for a dollar figure in the page text and return the raw matched
    string (e.g. "$2,000,000", "AUD 500k"). Banding into the client's
    value ranges happens in the ranking engine, not here.
    """
    match = _AMOUNT_RE.search(text)
    if not match:
        return None
    return match.group(0).strip()


def extract_eligibility_snippet(text: str):
    """
    Find the first mention of "eligib..." in the page text and return a
    window of surrounding context. This raw snippet is what the ranking
    engine will later read (with an LLM or rules) to classify eligibility
    as likely/unknown/not-eligible against a specific user's profile.
    """
    match = re.search(r"eligib\w*", text, re.IGNORECASE)
    if not match:
        return None

    start = max(0, match.start() - 50)
    end = min(len(text), match.start() + _ELIGIBILITY_CONTEXT_CHARS)
    return text[start:end].strip()


def extract_fields(html: str) -> dict:
    """Run all extraction steps and return a single dict of results."""
    title, text = extract_title_and_text(html)
    deadline_raw, deadline_parsed = extract_deadline(text)

    return {
        "title": title,
        "raw_text": text,
        "deadline_raw": deadline_raw,
        "deadline_parsed": deadline_parsed,
        "funding_amount_raw": extract_funding_amount(text),
        "eligibility_snippet": extract_eligibility_snippet(text),
    }
