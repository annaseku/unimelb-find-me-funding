"""Pages that are never one open funding opportunity, decided from the URL.

Discovery indexes whatever search returns, and the LLM funding gate (KAN-78)
only rejects pages that are not about funding at all. These hosts are about
funding but never list one open scheme (KAN-84). Checked at read time, like
the not_funding status (decision 9), so the rule covers rows already
published without a re-crawl, and direct lookup by id still works.

Only clear cases belong here. A scheme's own home page is not one: about half
the live root-URL results are a single scheme's site.
"""

from __future__ import annotations

from urllib.parse import urlparse

from backend.ranking.models import Opportunity, OpportunityStatus

AWARDED_GRANTS_HOST = "dataportal.arc.gov.au"
# Springshare LibGuides and similar library research guides: lists of funders.
GUIDE_HOST_PREFIXES = ("libguides.", "guides.", "researchguides.", "lawguides.")
GUIDE_HOST_SUFFIX = ".libguides.com"


def excluded_page_reason(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower()
    if host == AWARDED_GRANTS_HOST:
        return "ARC Grants Data Portal record of a grant already awarded"
    if host.startswith(GUIDE_HOST_PREFIXES) or host.endswith(GUIDE_HOST_SUFFIX):
        return "library research guide listing funders"
    return None


def is_funding_record(opportunity: Opportunity) -> bool:
    """True for a funding record, open or closed; false for anything never searchable."""
    return (
        opportunity.status != OpportunityStatus.NOT_FUNDING
        and excluded_page_reason(opportunity.url) is None
    )
