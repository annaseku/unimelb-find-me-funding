"""Combine the four criterion scores into an ordered result list.

Decision 5: the four scores are computed separately, combined with
configurable weights, and all four travel with the result so the UI can
show why something ranked where it did. Decision 9: closed opportunities are
soft-deleted, so they are filtered here at read time rather than removed
from the data. Paging is the API's job; this module returns the full list.

Australian opportunities rank above international ones within each
eligibility tier: the tool serves University of Melbourne researchers, and
the client asked for results tailored to Australian funding.
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlparse

from backend.ranking.deadline import score_deadline
from backend.ranking.eligibility import score_eligibility
from backend.ranking.funding_value import score_funding_value
from backend.ranking.models import (
    DeadlineBand,
    EligibilityState,
    Opportunity,
    OpportunityStatus,
    RankedOpportunity,
    SearchRequest,
)
from backend.ranking.research_match import score_research_match
from backend.ranking.weights import Weights


def score_opportunity(
    opportunity: Opportunity, request: SearchRequest, weights: Weights, today: date
) -> RankedOpportunity:
    eligibility = score_eligibility(opportunity, request)
    research_match = score_research_match(opportunity, request)
    funding_value = score_funding_value(opportunity)
    deadline = score_deadline(opportunity, today)

    weighted = (
        weights.eligibility * eligibility.score
        + weights.research_match * research_match.score
        + weights.funding_value * funding_value.score
        + weights.deadline * deadline.score
    )
    overall = round(weighted / weights.total(), 4)

    return RankedOpportunity(
        opportunity=opportunity,
        overall=overall,
        eligibility=eligibility,
        research_match=research_match,
        funding_value=funding_value,
        deadline=deadline,
    )


AUSTRALIAN_BOOST = 0.1

_AUSTRALIA_RE = re.compile(r"\bAustralian?s?\b", re.IGNORECASE)


def is_australian(opportunity: Opportunity) -> bool:
    """An Australian funder or a scheme for Australia-based researchers: an
    .au address, AU in the location or citizenship rules, or Australia named
    in the title, funder or eligibility text."""
    host = (urlparse(opportunity.url).hostname or "").lower()
    if host.endswith(".au"):
        return True
    if "AU" in opportunity.countries or "AU" in opportunity.citizenships_allowed:
        return True
    text = f"{opportunity.title} {opportunity.funder} {opportunity.eligibility_text}"
    return bool(_AUSTRALIA_RE.search(text))


def rank(
    opportunities: list[Opportunity], request: SearchRequest, weights: Weights, today: date
) -> list[RankedOpportunity]:
    ranked = [
        score_opportunity(o, request, weights, today)
        for o in opportunities
        if request.include_closed or _is_open(o, today)
    ]

    if request.hide_ineligible:
        # Discussion point 2: shown and de-ranked by default, hidden on request.
        ranked = [r for r in ranked if r.eligibility.label != EligibilityState.LIKELY_INELIGIBLE]

    # Likely-ineligible results always sit below everything else: the client
    # called a great match you cannot apply for "pointless". Within each tier,
    # Australian opportunities come first, then highest overall, equal
    # overalls prefer the more eligible one, then a stable id order so two
    # runs always agree.
    ranked.sort(
        key=lambda r: (
            r.eligibility.label == EligibilityState.LIKELY_INELIGIBLE,
            -(r.overall + (AUSTRALIAN_BOOST if is_australian(r.opportunity) else 0.0)),
            -r.eligibility.score,
            r.opportunity.id,
        )
    )
    return ranked


def _is_open(opportunity: Opportunity, today: date) -> bool:
    if opportunity.status == OpportunityStatus.CLOSED:
        return False
    return score_deadline(opportunity, today).label != DeadlineBand.CLOSED
