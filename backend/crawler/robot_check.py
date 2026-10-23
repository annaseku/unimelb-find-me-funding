"""
robots.txt compliance checking, with per-domain caching so we don't
re-fetch the same robots.txt file on every request.

Follows RFC 9309: a robots.txt that does not exist (4xx) means no
restrictions, but one that cannot be reached (5xx or a network error)
means do not crawl the site at all.
"""

import logging
import urllib.robotparser
from urllib.parse import urlparse

import requests

from backend.crawler.config import HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

# Cache of domain -> RobotFileParser, so each domain's robots.txt is only
# fetched once per process run.
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


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
        except requests.RequestException as e:
            logger.warning("robots.txt unreachable for %s, not crawling it: %s", domain, e)
            rp.disallow_all = True
        else:
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            elif 400 <= resp.status_code < 500:
                rp.allow_all = True
            else:
                logger.warning(
                    "robots.txt for %s returned %s, not crawling it", domain, resp.status_code
                )
                rp.disallow_all = True

        _robots_cache[domain] = rp

    return _robots_cache[domain]


def is_allowed(url: str, user_agent: str = HEADERS["User-Agent"]) -> bool:
    """Check whether our crawler may fetch `url` under that site's robots.txt."""
    return _get_parser(url).can_fetch(user_agent, url)
