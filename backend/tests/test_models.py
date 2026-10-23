"""The models are the contract between crawler, ranker and frontend, so the
vocabulary is tested explicitly."""

import pytest
from pydantic import ValidationError

from backend.crawler.query_builder import CAREER_STAGE_TERMS, FUNDING_TYPE_TERMS
from backend.ranking.models import (
    CareerStage,
    FundingType,
    Opportunity,
    SearchRequest,
)


def test_career_stage_values_match_the_crawler_query_builder():
    assert {s.value for s in CareerStage} == set(CAREER_STAGE_TERMS)


def test_funding_type_values_match_the_crawler_query_builder():
    assert {f.value for f in FundingType} == set(FUNDING_TYPE_TERMS)


def test_empty_search_request_is_valid_and_defaults_to_ten_results():
    request = SearchRequest()
    assert request.limit == 10
    assert request.offset == 0
    assert request.hide_ineligible is False
    assert request.include_closed is False


@pytest.mark.parametrize("limit", [0, 101])
def test_limit_outside_one_to_one_hundred_is_rejected(limit):
    with pytest.raises(ValidationError):
        SearchRequest(limit=limit)


def test_opportunity_lists_default_to_empty_meaning_unrestricted():
    opportunity = Opportunity(id="x", title="X", funder="F", url="https://example.org", summary="s")
    assert opportunity.citizenships_allowed == []
    assert opportunity.amount_aud is None
    assert opportunity.deadline is None
    assert opportunity.status == "active"
