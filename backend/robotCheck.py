"""
robots.txt compliance checking, with per-domain caching so we don't
re-fetch the same robots.txt file on every request.
"""

import urllib.robotparser
from urllib.parse import urlparse

# Cache of domain -> RobotFileParser, so each domain's robots.txt is only
# fetched once per process run.
_robots_cache: dict = {}


def _get_parser(url: str) -> urllib.robotparser.RobotFileParser:
    """Return a (possibly cached) RobotFileParser for the given URL's domain."""
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"

    if domain not in _robots_cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{domain}/robots.txt")
        try:
            rp.read()
        except Exception:
            # If robots.txt can't be fetched/parsed, default to permissive
            # (matches how most crawlers behave when robots.txt is missing).
            pass
        _robots_cache[domain] = rp

    return _robots_cache[domain]


def is_allowed(url: str, user_agent: str = "*") -> bool:
    """
    Check whether crawling `url` is permitted by that site's robots.txt.

    Fails open (returns True) if robots.txt can't be read at all, since a
    missing/unreachable robots.txt conventionally means "no restrictions".
    """
    try:
        parser = _get_parser(url)
        return parser.can_fetch(user_agent, url)
    except Exception:
        return True