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

# Page furniture, not content: menus, headers, footers, cookie banners. Left
# in, the start of the page text is a menu, and the result card's overview
# (the first sentences of the text) reads "Home About Funding News Contact".
_FURNITURE_TAGS = [
    "script", "style", "noscript", "template", "svg", "iframe",
    # Not <form>: ASP.NET pages wrap the whole body in one.
    "nav", "header", "footer", "aside", "button", "select",
]
_FURNITURE_ROLES = {"navigation", "banner", "contentinfo", "search", "menu", "menubar"}
_FURNITURE_CLASS_RE = re.compile(
    r"(^|[-_ ])(nav|navbar|menu|breadcrumbs?|cookies?|skip|site-header|site-footer|"
    r"footer|sidebar|social|share)([-_ ]|$)",
    re.IGNORECASE,
)

# A <main> or <article> shorter than this is probably a teaser, not the page.
_MIN_MAIN_TEXT_CHARS = 200


def _is_furniture(tag) -> bool:
    if tag.attrs is None:
        return False
    if (tag.get("role") or "").lower() in _FURNITURE_ROLES:
        return True
    names = " ".join(tag.get("class") or []) + " " + (tag.get("id") or "")
    return bool(_FURNITURE_CLASS_RE.search(names))


def _collapse(text: str) -> str:
    return " ".join(text.split())


def extract_description(soup) -> str:
    """The page's own summary from <meta name="description"> or Open Graph,
    which funders usually write as a one-line overview of the scheme."""
    for attrs in ({"name": "description"}, {"property": "og:description"}):
        meta = soup.find("meta", attrs=attrs)
        if meta and meta.get("content"):
            return _collapse(meta["content"])
    return ""


def extract_title_and_text(html: str):
    """Extract page title and cleaned, whitespace-collapsed body text, with
    menus, headers and footers removed and the main content preferred."""
    soup = BeautifulSoup(html, "html.parser")
    title, text, _ = _extract(soup)
    return title, text


def _extract(soup):
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    description = extract_description(soup)

    for tag in soup(_FURNITURE_TAGS):
        tag.decompose()
    for tag in soup.find_all(_is_furniture):
        tag.decompose()

    body = soup.body or soup
    for candidate in (soup.find("main"), soup.find(attrs={"role": "main"}), soup.find("article")):
        if candidate and len(candidate.get_text(" ", strip=True)) >= _MIN_MAIN_TEXT_CHARS:
            body = candidate
            break

    text = _collapse(body.get_text(separator=" "))
    return title, text, description


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
    title, text, description = _extract(BeautifulSoup(html, "html.parser"))
    deadline_raw, deadline_parsed = extract_deadline(text)

    return {
        "title": title,
        "description": description,
        "raw_text": text,
        "deadline_raw": deadline_raw,
        "deadline_parsed": deadline_parsed,
        "funding_amount_raw": extract_funding_amount(text),
        "eligibility_snippet": extract_eligibility_snippet(text),
    }