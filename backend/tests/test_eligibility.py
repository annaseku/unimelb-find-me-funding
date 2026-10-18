"""Eligibility is the client's top priority and has four states (decision 4).
Each test names the rule it proves."""

import pytest

from backend.ranking.eligibility import ELIGIBILITY_SCORES, score_eligibility
from backend.ranking.models import (
    CareerStage,
    EligibilityState,
    EmployerType,
    FundingType,
    Opportunity,
    SearchRequest,
)


def make_opportunity(**overrides) -> Opportunity:
    base = dict(id="o1", title="T", funder="F", url="https://example.org", summary="s")
    return Opportunity(**{**base, **overrides})


def test_no_restrictions_stated_is_potentially_eligible():
    result = score_eligibility(make_opportunity(), SearchRequest())
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE
    assert result.score == ELIGIBILITY_SCORES[EligibilityState.POTENTIALLY_ELIGIBLE]
    assert any("no restrictions" in r.lower() for r in result.reasons)


def test_restriction_stated_but_nothing_supplied_is_unknown():
    opportunity = make_opportunity(citizenships_allowed=["AU"])
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.UNKNOWN


def test_citizenship_mismatch_is_likely_ineligible_and_still_scored():
    opportunity = make_opportunity(citizenships_allowed=["AU", "NZ"])
    result = score_eligibility(opportunity, SearchRequest(citizenships=["GB"]))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE
    assert result.score > 0, "decision 4: de-ranked, never dropped by the scorer"
    assert any("AU" in r and "GB" in r for r in result.reasons)


def test_one_of_several_citizenships_matching_passes():
    opportunity = make_opportunity(citizenships_allowed=["AU"], countries=["AU"])
    result = score_eligibility(opportunity, SearchRequest(citizenships=["GB", "AU"]))
    assert result.label == EligibilityState.ELIGIBLE


def test_all_stated_restrictions_passing_is_eligible_with_score_one():
    opportunity = make_opportunity(
        countries=["AU"],
        citizenships_allowed=["AU"],
        employer_types_allowed=[EmployerType.UNIVERSITY],
        career_stages_allowed=[CareerStage.POSTDOC_2_5],
        funding_types_offered=[FundingType.SALARY],
    )
    request = SearchRequest(
        citizenships=["AU"],
        employer_type=EmployerType.UNIVERSITY,
        career_stage=CareerStage.POSTDOC_2_5,
        funding_types=[FundingType.SALARY],
    )
    result = score_eligibility(opportunity, request)
    assert result.label == EligibilityState.ELIGIBLE
    assert result.score == 1.0
    assert len(result.reasons) == 5  # location plus the four stated restrictions


def test_mixed_pass_and_unknown_is_potentially_eligible():
    opportunity = make_opportunity(
        citizenships_allowed=["AU"], career_stages_allowed=[CareerStage.UNDERGRADUATE]
    )
    result = score_eligibility(opportunity, SearchRequest(citizenships=["AU"]))
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE


def test_employer_type_mismatch_fails():
    opportunity = make_opportunity(employer_types_allowed=[EmployerType.INDUSTRY])
    result = score_eligibility(opportunity, SearchRequest(employer_type=EmployerType.UNIVERSITY))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE


def test_career_stage_mismatch_fails():
    opportunity = make_opportunity(career_stages_allowed=[CareerStage.POSTDOC_0_2])
    result = score_eligibility(
        opportunity, SearchRequest(career_stage=CareerStage.GRADUATE_STUDENT)
    )
    assert result.label == EligibilityState.LIKELY_INELIGIBLE


@pytest.mark.parametrize("wanted", [FundingType.ALL, FundingType.ANY])
def test_all_or_any_funding_type_never_contradicts(wanted):
    opportunity = make_opportunity(funding_types_offered=[FundingType.EQUIPMENT], countries=["AU"])
    result = score_eligibility(opportunity, SearchRequest(funding_types=[wanted]))
    assert result.label == EligibilityState.ELIGIBLE


def test_funding_type_not_offered_fails():
    opportunity = make_opportunity(funding_types_offered=[FundingType.EQUIPMENT])
    result = score_eligibility(opportunity, SearchRequest(funding_types=[FundingType.SALARY]))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE


def test_funding_type_is_skipped_when_the_researcher_lists_none():
    # No requested funding type means no need was expressed, so it is neither
    # a pass nor an unknown; the opportunity has nothing else stated.
    opportunity = make_opportunity(funding_types_offered=[FundingType.EQUIPMENT])
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE


def test_every_result_has_at_least_one_reason():
    for request in (SearchRequest(), SearchRequest(citizenships=["AU"])):
        assert score_eligibility(make_opportunity(citizenships_allowed=["AU"]), request).reasons


def test_career_stage_reason_uses_a_human_label():
    result = score_eligibility(
        make_opportunity(career_stages_allowed=[CareerStage.POSTDOC_0_2]),
        SearchRequest(career_stage=CareerStage.POSTDOC_0_2),
    )
    reason = " ".join(result.reasons)
    assert "0-2 years post-PhD" in reason
    assert "postdoc_0_2" not in reason


def test_employer_type_reason_uses_a_human_label():
    result = score_eligibility(
        make_opportunity(employer_types_allowed=[EmployerType.RESEARCH_INSTITUTE]),
        SearchRequest(employer_type=EmployerType.PHILANTHROPIC),
    )
    reason = " ".join(result.reasons)
    assert "research institute" in reason
    assert "philanthropic organisation" in reason
    assert "research_institute" not in reason


def test_funding_type_reason_uses_a_human_label():
    result = score_eligibility(
        make_opportunity(funding_types_offered=[FundingType.ALL]),
        SearchRequest(funding_types=[FundingType.SALARY]),
    )
    reason = " ".join(result.reasons)
    assert "all kinds" in reason
    assert "salary" in reason


# --- institution location ----------------------------------------------------


def test_stated_country_excluding_the_researchers_is_likely_ineligible():
    opportunity = make_opportunity(countries=["DE", "FR"])
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.LIKELY_INELIGIBLE
    assert any("Australia" in r for r in result.reasons)


def test_australian_funder_domain_passes_for_the_default_australian_institution():
    opportunity = make_opportunity(url="https://www.arc.gov.au/funding")
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.ELIGIBLE


def test_mention_of_australia_passes_on_a_generic_domain():
    opportunity = make_opportunity(summary="Open to early-career Australian researchers.")
    assert score_eligibility(opportunity, SearchRequest()).label == EligibilityState.ELIGIBLE


def test_overseas_funder_domain_is_unknown_not_ineligible():
    # NIH funds some foreign institutions, so a US domain alone is never a fail.
    opportunity = make_opportunity(url="https://grants.nih.gov/r01")
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.UNKNOWN
    assert any("the United States" in r for r in result.reasons)


def test_australian_funder_outranks_us_funder_on_eligibility():
    au = score_eligibility(make_opportunity(url="https://nhmrc.gov.au/x"), SearchRequest())
    us = score_eligibility(make_opportunity(url="https://www.nsf.gov/x"), SearchRequest())
    assert au.score > us.score


def test_institution_country_can_be_overridden():
    opportunity = make_opportunity(url="https://www.ukri.org.uk/x", countries=["GB"])
    request = SearchRequest(institution_country="GB")
    assert score_eligibility(opportunity, request).label == EligibilityState.ELIGIBLE


def test_passing_filters_with_unconfirmed_location_is_never_fully_eligible():
    # A generic-domain funder that states no location: passing career stage
    # alone used to read as 100% eligible for an overseas funder.
    opportunity = make_opportunity(career_stages_allowed=[CareerStage.POSTDOC_2_5])
    result = score_eligibility(opportunity, SearchRequest(career_stage=CareerStage.POSTDOC_2_5))
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE
    assert result.score < 1.0
    assert any("cannot confirm" in r for r in result.reasons)
