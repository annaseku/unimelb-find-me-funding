"""Deterministic eligibility classification (decisions 3 and 4).

Every restriction the funder states is checked against the researcher's
inputs and yields pass, fail or unknown. The four-state outcome means an
opportunity with one unverifiable requirement is still shown, as the client
asked. Nothing here calls an LLM; the funder's eligibility prose is kept on
the opportunity for a future LLM pass on the ambiguous cases.
"""

from __future__ import annotations

from enum import Enum

from backend.ranking.models import (
    CriterionResult,
    EligibilityState,
    FundingType,
    Opportunity,
    SearchRequest,
)

ELIGIBILITY_SCORES: dict[EligibilityState, float] = {
    EligibilityState.ELIGIBLE: 1.0,
    EligibilityState.POTENTIALLY_ELIGIBLE: 0.7,
    EligibilityState.UNKNOWN: 0.5,
    EligibilityState.LIKELY_INELIGIBLE: 0.1,
}


class Check(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"   # the funder restricts this, the researcher said nothing


def _join(values) -> str:
    return ", ".join(str(v) for v in values)


def _check_membership(label: str, allowed: list, supplied: list) -> tuple[Check, str]:
    """Shared rule for citizenship, employer type and career stage.

    `allowed` is non-empty (the caller only calls this when the funder
    restricts the field). `supplied` is whatever the researcher selected.
    """
    if not supplied:
        return Check.UNKNOWN, f"{label} is restricted to {_join(allowed)}; you did not say."
    matches = [s for s in supplied if s in allowed]
    if matches:
        return Check.PASS, f"{label} accepted: open to {_join(allowed)}; you selected {_join(matches)}."
    return Check.FAIL, f"{label} restricted to {_join(allowed)}; you selected {_join(supplied)}."


def _check_funding_type(offered: list[FundingType], wanted: list[FundingType]) -> tuple[Check, str]:
    # "all" and "any" mean the researcher will take whatever is offered.
    if FundingType.ALL in wanted or FundingType.ANY in wanted:
        return Check.PASS, f"Funding type: offers {_join(offered)}, which suits any preference."
    overlap = [w for w in wanted if w in offered]
    if overlap:
        return Check.PASS, f"Funding type: offers {_join(overlap)}, which you asked for."
    return Check.FAIL, f"Funding type: offers {_join(offered)} but you asked for {_join(wanted)}."


def score_eligibility(opportunity: Opportunity, request: SearchRequest) -> CriterionResult:
    checks: list[Check] = []
    reasons: list[str] = []

    if opportunity.citizenships_allowed:
        outcome, reason = _check_membership(
            "Citizenship", opportunity.citizenships_allowed, request.citizenships
        )
        checks.append(outcome)
        reasons.append(reason)

    if opportunity.employer_types_allowed:
        supplied = [request.employer_type] if request.employer_type else []
        outcome, reason = _check_membership(
            "Employer type", opportunity.employer_types_allowed, supplied
        )
        checks.append(outcome)
        reasons.append(reason)

    if opportunity.career_stages_allowed:
        supplied = [request.career_stage] if request.career_stage else []
        outcome, reason = _check_membership(
            "Career stage", opportunity.career_stages_allowed, supplied
        )
        checks.append(outcome)
        reasons.append(reason)

    # Funding type is only a restriction if the researcher expressed a need.
    if opportunity.funding_types_offered and request.funding_types:
        outcome, reason = _check_funding_type(
            opportunity.funding_types_offered, request.funding_types
        )
        checks.append(outcome)
        reasons.append(reason)

    state = _state_from_checks(checks)
    if not reasons:
        reasons.append("The funder states no restrictions we can check.")
    elif state == EligibilityState.UNKNOWN:
        reasons.append("Restrictions exist but your inputs did not cover them.")
    return CriterionResult(score=ELIGIBILITY_SCORES[state], label=state, reasons=reasons)


def _state_from_checks(checks: list[Check]) -> EligibilityState:
    # Order matters: one hard contradiction outranks any number of passes.
    if Check.FAIL in checks:
        return EligibilityState.LIKELY_INELIGIBLE
    passes = checks.count(Check.PASS)
    unknowns = checks.count(Check.UNKNOWN)
    if passes == 0 and unknowns == 0:
        return EligibilityState.POTENTIALLY_ELIGIBLE   # nothing checkable was stated
    if passes == 0:
        return EligibilityState.UNKNOWN
    if unknowns == 0:
        return EligibilityState.ELIGIBLE
    return EligibilityState.POTENTIALLY_ELIGIBLE
