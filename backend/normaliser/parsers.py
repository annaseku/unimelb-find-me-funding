"""Deterministic parsers for the crisp fields: amount, deadline, status, id,
funder, summary and keywords. No network calls, no LLM."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from urllib.parse import urlparse

from backend.crawler.dates import parse_date_text
from backend.ranking.models import OpportunityStatus

RATES_TO_AUD: dict[str, float] = {
    "AUD": 1.0,
    "USD": 1.5,
    "EUR": 1.65,
    "GBP": 1.9,
    "NZD": 0.93,
    "CAD": 1.1,
}

MIN_AMOUNT_AUD = 1_000

_MULTIPLIERS: dict[str, float] = {
    "million": 1_000_000,
    "mn": 1_000_000,
    "m": 1_000_000,
    "billion": 1_000_000_000,
    "bn": 1_000_000_000,
    "b": 1_000_000_000,
    "thousand": 1_000,
    "k": 1_000,
}

# Order matters: check the more specific symbols/codes before the bare "$",
# which is the fallback (assumed AUD).
_CURRENCY_MARKERS: list[tuple[str, str]] = [
    (r"€|\bEUR\b", "EUR"),
    (r"£|\bGBP\b", "GBP"),
    (r"US\$|\bUSD\b", "USD"),
    (r"NZ\$|\bNZD\b", "NZD"),
    (r"CA\$|\bCAD\b", "CAD"),
    (r"A\$|\bAUD\b", "AUD"),
    (r"\$", "AUD"),
]

_NUMBER_RE = r"(?P<number>\d[\d,]*(?:\.\d+)?)"
# The trailing \b stops the "m" of "may" or the "b" of "budget" reading as a multiplier.
_MULTIPLIER_RE = r"(?:\s*(?P<multiplier>million|billion|thousand|mn|bn|k|b|m)\b)?"

_STOP_WORDS = frozenset(
    {
        "with",
        "from",
        "that",
        "this",
        "grant",
        "grants",
        "funding",
        "program",
        "programme",
        "scheme",
        "award",
        "awards",
        "research",
    }
)


def _find_amount(pattern: str, text: str) -> re.Match[str] | None:
    return re.search(pattern, text, flags=re.IGNORECASE)


def parse_amount_aud(raw: str | None) -> tuple[int | None, str]:
    """Return (amount in whole AUD, note). The note explains the conversion,
    or why no amount was returned. Only the first money figure in the string
    is used, so trailing numbers (e.g. a grant's duration in years) are
    ignored."""
    if not raw:
        return None, "no amount found"

    for currency_pattern, currency in _CURRENCY_MARKERS:
        # Non-capturing group around the alternation: without it, "|" splits
        # the whole pattern in two and the shorter branch (e.g. bare "A$")
        # matches first, leaving the number group unmatched.
        pattern = f"(?:{currency_pattern})" + r"\s*" + _NUMBER_RE + _MULTIPLIER_RE
        match = _find_amount(pattern, raw)
        if not match:
            continue

        number_text = match.group("number").replace(",", "")
        multiplier_text = match.group("multiplier")
        try:
            number = float(number_text)
        except ValueError:
            continue
        if multiplier_text:
            number *= _MULTIPLIERS[multiplier_text.lower()]

        rate = RATES_TO_AUD[currency]
        amount_aud = round(number * rate)

        if amount_aud < MIN_AMOUNT_AUD:
            return None, "figure below $1,000 ignored"

        if currency == "AUD":
            bare_dollar = re.match(r"\$", match.group(0)) is not None
            note = "currency not stated, assumed AUD" if bare_dollar else "stated in AUD"
        else:
            stated = f"{number_text}{(' ' + multiplier_text) if multiplier_text else ''}"
            note = f"converted from {currency} {stated} at {rate} AUD per {currency}"
        return amount_aud, note

    return None, "no amount found"


def parse_deadline(deadline_parsed: str | None, deadline_raw: str | None) -> date | None:
    """An ISO `deadline_parsed` wins outright. Otherwise fall back to a fuzzy
    parse of `deadline_raw`, accepting only plausible years."""
    if deadline_parsed:
        try:
            iso_date = date.fromisoformat(deadline_parsed)
        except ValueError:
            iso_date = None
        if iso_date is not None and 2020 <= iso_date.year <= 2100:
            return iso_date

    if deadline_raw:
        return parse_date_text(deadline_raw)

    return None


def derive_status(deadline: date | None, today: date) -> OpportunityStatus:
    if deadline is not None and deadline < today:
        return OpportunityStatus.CLOSED
    return OpportunityStatus.ACTIVE


def _host_without_www(url: str) -> str:
    host = urlparse(url).netloc
    return host[4:] if host.startswith("www.") else host


def make_id(url: str) -> str:
    """A deterministic, human-scannable id: the host as a slug plus 8 hex
    characters of the URL's SHA-256, so two different URLs on the same host
    never collide."""
    host = _host_without_www(url)
    slug = re.sub(r"[^a-z0-9]+", "-", host.lower()).strip("-")
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}"


def funder_from_url(url: str) -> str:
    return _host_without_www(url)


_SENTENCE_END_RE = re.compile(r"[.?!]\s")
_TOKEN_RE = re.compile(r"\S+")
MIN_PROSE_WORDS = 6
MIN_LOWERCASE_SHARE = 0.5
# Capitalised words that open a sentence rather than label a menu item.
_SENTENCE_OPENERS = frozenset(
    "The A An Our This These We Its Their Each All In For To Applications Funding".split()
)
_MENU_BOUNDARIES = frozenset("/ < | Share Twitter Facebook LinkedIn Email".split())
_MAX_NAME_WORDS = 8
# Site-wide notices that read as prose but say nothing about the opportunity.
_BOILERPLATE_RE = re.compile(
    r"\.gov|official website|government websites|https://|browser does not support"
    r"|sensitive information|site is secure|cookies|javascript|copyright|privacy policy"
    r"|verifying|please wait|subscribe",
    re.IGNORECASE,
)


def _is_menu_token(token: str) -> bool:
    return not token[0].islower()


def _is_name_token(token: str) -> bool:
    return token not in _MENU_BOUNDARIES and token.lstrip("(")[:1].isupper()


def _name_start(words: list[str], start: int) -> int:
    """Keep a proper name that opens the prose ("The FHRI Fund releases",
    "Biological Technologies (BT) Miromatrix Medical Inc's unique ...").
    Walk back over the capitalised run ending at `start`, but only keep it
    when a sentence opener or a parenthesised acronym marks it as a name:
    a bare run of capitalised words is just as likely a menu."""
    if start + 1 >= len(words) or not words[start + 1][0].islower():
        return start
    first = start
    while first > 0 and start - first < _MAX_NAME_WORDS and _is_name_token(words[first - 1]):
        first -= 1
    for i in range(start, first - 1, -1):
        if words[i] in _SENTENCE_OPENERS:
            return i
    if any(word.startswith("(") for word in words[first : start + 1]):
        return first
    return start


def _prose_start(text: str) -> int | None:
    """Skip capitalised menu runs, retaining short names that introduce prose."""
    sentence_start = 0
    ends = [m.end() for m in _SENTENCE_END_RE.finditer(text)] + [len(text)]
    for end in ends:
        tokens = list(_TOKEN_RE.finditer(text, sentence_start, end))
        start = 0
        for i in range(2, len(tokens)):
            if all(_is_menu_token(t.group()) for t in tokens[i - 2 : i + 1]):
                start = i
        if start and tokens[start - 1].group() in _SENTENCE_OPENERS:
            start -= 1
        words = [t.group() for t in tokens]
        for candidate in (_name_start(words, start), start):
            remaining = words[candidate:]
            lowercase = sum(1 for w in remaining if w[0].islower())
            is_prose = (
                len(remaining) >= MIN_PROSE_WORDS
                and lowercase / len(remaining) >= MIN_LOWERCASE_SHARE
            )
            if is_prose and not _BOILERPLATE_RE.search(" ".join(remaining)):
                return tokens[candidate].start()
        sentence_start = end
    return None


def summarise(raw_text: str | None, title: str | None, max_chars: int = 400) -> str:
    if not raw_text:
        return ""

    text = raw_text.strip()
    if title and text.lower().startswith(title.strip().lower()):
        text = text[len(title.strip()) :]
        # Drop the separator left dangling after the title (". ", " - ", etc.)
        text = re.sub(r"^[\s.,;:!\-–—]+", "", text)

    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    start = _prose_start(text)
    if start:
        text = text[start:]

    if len(text) <= max_chars:
        return text

    window = text[:max_chars]
    last_end = None
    for match in _SENTENCE_END_RE.finditer(window):
        last_end = match.end()
    if last_end:
        return window[:last_end].strip()

    return window.rstrip() + "…"


def keywords_from(title: str | None, limit: int = 8) -> list[str]:
    if not title:
        return []

    words = re.findall(r"[a-zA-Z]+", title.lower())
    keywords: list[str] = []
    for word in words:
        if len(word) < 4 or word in _STOP_WORDS or word in keywords:
            continue
        keywords.append(word)
        if len(keywords) >= limit:
            break
    return keywords
