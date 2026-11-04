"""Pages that are never one open opportunity, decided from the URL (KAN-84)."""

import pytest

from backend.ranking.models import Opportunity, OpportunityStatus
from backend.ranking.page_filter import excluded_page_reason, is_funding_record


def make(url: str, status: OpportunityStatus = OpportunityStatus.ACTIVE) -> Opportunity:
    return Opportunity(id="o", title="T", funder="F", url=url, summary="s", status=status)


@pytest.mark.parametrize(
    "url",
    [
        # Grants already awarded, found on the live index 05/11/2026.
        "https://dataportal.arc.gov.au/NCGP/Web/Grant/Grant/FT180100009",
        "https://dataportal.arc.gov.au/RGS/Web/Grants/DE230101382",
        "https://dataportal.arc.gov.au/NCGP/web/grant/grants",
        # Library research guides: lists of funders, never one opportunity.
        "https://libguides.lib.rochester.edu/LING/funding",
        "https://hsls.libguides.com/grants",
        "https://relay.libguides.com/teacher-education/grants",
        "https://guides.lib.umassd.edu/c.php?g=207329&p=1367280",
        "https://guides.library.umass.edu/c.php?g=1413600&p=10473407",
        "https://guides.smu.edu/underwood/funding",
        "https://researchguides.dartmouth.edu/earthsci/scholarships",
        "https://lawguides.mainelaw.maine.edu/External_Funding/grantorganizations",
        "https://LIBGUIDES.colum.edu/funding/writing",
    ],
)
def test_awarded_grant_records_and_library_guides_are_excluded(url):
    assert excluded_page_reason(url) is not None
    assert not is_funding_record(make(url))


@pytest.mark.parametrize(
    "url",
    [
        # Real schemes on the same hosts or with similar paths must stay.
        "https://www.arc.gov.au/funding-research/funding-schemes/discovery-program",
        "https://www.bath.ac.uk/guides/joining-mathematical-sciences-as-an-independent-research-fel",
        "https://scholar.africa/guides/agriculture-scholarships-african-students",
        # A scheme's own home page is not a clear case (KAN-84), so it stays.
        "https://clscholarship.org/",
        "https://www.artswriters.org/",
    ],
)
def test_real_schemes_and_home_pages_are_kept(url):
    assert excluded_page_reason(url) is None
    assert is_funding_record(make(url))


def test_not_funding_status_is_still_excluded():
    assert not is_funding_record(make("https://example.org/grant", OpportunityStatus.NOT_FUNDING))


def test_closed_schemes_still_count_as_funding_records():
    assert is_funding_record(make("https://example.org/grant", OpportunityStatus.CLOSED))
