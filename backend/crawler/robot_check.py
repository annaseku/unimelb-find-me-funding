"""
robots.txt compliance checking, with per-domain caching so we don't
re-fetch the same robots.txt file on every request.
"""

import urllib.robotparser
from urllib.parse import urlparse

import requests

from backend.crawler.config import HEADERS, REQUEST_TIMEOUT

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

        # Deliberately NOT using rp.read() here: it fetches robots.txt
        # with urllib's default opener, which sends the User-Agent
        # "Python-urllib/x.y". Many sites block that generic UA and
        # return 403 -- and RobotFileParser specifically treats a 401/403
        # on the robots.txt fetch itself as "disallow everything", not
        # "couldn't check, so allow". That silently blocked every single
        # URL regardless of domain. Fetching with our real headers and
        # feeding the text straight into the parser avoids both problems.
        try:
            resp = requests.get(f"{domain}/robots.txt", headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                # No robots.txt, or it errored -- treat as permissive,
                # which matches how most well-behaved crawlers handle a
                # missing robots.txt.
                rp.parse([])
        except requests.RequestException:
            rp.parse([])

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
