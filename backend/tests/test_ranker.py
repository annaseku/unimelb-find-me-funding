"""The combiner is decision 5: four separate scores, configurable weights,
never one opaque number. Closed results are soft-deleted (decision 9)."""

from datetime import timedelta

import pytest

from backend.ranking.models import (
    DeadlineBand,
    EligibilityState,
    Opportunity,
    OpportunityStatus,
    SearchRequest,
)
from backend.ranking.ranker import AUSTRALIAN_BOOST, is_australian, rank, score_opportunity
from backend.ranking.weights import DEFAULT_WEIGHTS, Weights
from backend.tests.conftest import TODAY


def make_opportunity(**overrides) -> Opportunity:
    base = dict(
        id="o1",
        title="Machine learning grant",
        funder="F",
        url="https://example.org",
        summary="Funds machine learning research.",
        amount_aud=100_000,
        deadline=TODAY + timedelta(days=90),
        for_codes=["4611"],
    )
    return Opportunity(**{**base, **overrides})


def test_every_result_carries_four_criteria_with_reasons():
    ranked = score_opportunity(make_opportunity(), SearchRequest(), DEFAULT_WEIGHTS, TODAY)
    for criterion in (
        ranked.eligibility,
        ranked.research_match,
        ranked.funding_value,
        ranked.deadline,
    ):
        assert criterion.reasons
        assert 0.0 <= criterion.score <= 1.0
    assert 0.0 <= ranked.overall <= 1.0


def test_weighting_everything_on_one_criterion_reproduces_that_score():
    weights = Weights(eligibility=0, research_match=0, funding_value=1, deadline=0)
    ranked = score_opportunity(make_opportunity(), SearchRequest(), weights, TODAY)
    assert ranked.overall == pytest.approx(ranked.funding_value.score)


def test_overall_is_the_weighted_average():
    ranked = score_opportunity(
        make_opportunity(), SearchRequest(for_codes=["4611"]), DEFAULT_WEIGHTS, TODAY
    )
    expected = (
        0.4 * ranked.eligibility.score
        + 0.3 * ranked.research_match.score
        + 0.15 * ranked.funding_value.score
        + 0.15 * ranked.deadline.score
    )
    assert ranked.overall == pytest.approx(expected, abs=1e-4)


def test_past_deadline_is_hidden_by_default_and_retrievable():
    opportunities = [
        make_opportunity(id="open"),
        make_opportunity(id="past", deadline=TODAY - timedelta(days=1)),
    ]
    default = rank(opportunities, SearchRequest(), DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in default] == ["open"]
    shown = rank(opportunities, SearchRequest(include_closed=True), DEFAULT_WEIGHTS, TODAY)
    assert {r.opportunity.id for r in shown} == {"open", "past"}
    past = next(r for r in shown if r.opportunity.id == "past")
    assert past.deadline.label == DeadlineBand.CLOSED


def test_closed_status_is_hidden_even_with_a_future_deadline():
    opportunities = [make_opportunity(id="archived", status=OpportunityStatus.CLOSED)]
    assert rank(opportunities, SearchRequest(), DEFAULT_WEIGHTS, TODAY) == []


def test_hide_ineligible_drops_only_likely_ineligible():
    opportunities = [
        make_opportunity(id="fits", citizenships_allowed=["AU"]),
        make_opportunity(id="unknown"),
        make_opportunity(id="wrong", citizenships_allowed=["US"]),
    ]
    request = SearchRequest(citizenships=["AU"], hide_ineligible=True)
    ids = [r.opportunity.id for r in rank(opportunities, request, DEFAULT_WEIGHTS, TODAY)]
    assert "wrong" not in ids
    assert {"fits", "unknown"} <= set(ids)


def test_ineligible_is_shown_and_ranked_last_by_default():
    opportunities = [
        make_opportunity(id="wrong", citizenships_allowed=["US"]),
        make_opportunity(id="fits", citizenships_allowed=["AU"]),
    ]
    results = rank(opportunities, SearchRequest(citizenships=["AU"]), DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in results] == ["fits", "wrong"]
    assert results[-1].eligibility.label == EligibilityState.LIKELY_INELIGIBLE


def test_ineligible_never_outranks_an_eligible_result_even_with_a_better_overall():
    opportunities = [
        make_opportunity(id="rich-but-wrong", citizenships_allowed=["US"], amount_aud=9_000_000),
        make_opportunity(
            id="modest-but-fits", citizenships_allowed=["AU"], amount_aud=1_000, for_codes=["9999"]
        ),
    ]
    request = SearchRequest(citizenships=["AU"], for_codes=["4611"])
    results = rank(opportunities, request, DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in results] == ["modest-but-fits", "rich-but-wrong"]
    # The tier rule decided this, not the weights: the ineligible one scores higher.
    assert results[0].overall < results[1].overall


def test_ties_break_on_eligibility_then_id():
    # Same overall by construction: identical except eligibility state and id.
    weights = Weights(eligibility=0, research_match=1, funding_value=0, deadline=0)
    opportunities = [
        make_opportunity(id="b"),
        make_opportunity(id="a"),
        make_opportunity(id="c", citizenships_allowed=["AU"]),
    ]
    results = rank(opportunities, SearchRequest(citizenships=["AU"]), weights, TODAY)
    assert [r.opportunity.id for r in results] == ["c", "a", "b"]


def test_best_first():
    opportunities = [
        make_opportunity(id="weak", for_codes=["9999"], amount_aud=1_000),
        make_opportunity(id="strong", amount_aud=6_000_000),
    ]
    results = rank(opportunities, SearchRequest(for_codes=["4611"]), DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in results] == ["strong", "weak"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"url": "https://www.arc.gov.au/funding"},
        {"countries": ["AU"]},
        {"citizenships_allowed": ["AU", "NZ"]},
        {"title": "Australian Postgraduate Award"},
        {"funder": "Australian Research Council"},
        {"eligibility_text": "Applicants must work in Australia."},
    ],
)
def test_australian_signals(overrides):
    assert is_australian(make_opportunity(**overrides))


def test_an_international_scheme_is_not_australian():
    assert not is_australian(make_opportunity(url="https://www.nsf.gov/funding"))
    # "Austral" alone (Austral Islands, australopithecus) is not Australia.
    assert not is_australian(make_opportunity(title="Austral ecology grant"))


def test_an_australian_scheme_outranks_a_slightly_better_international_one():
    international = make_opportunity(id="us", amount_aud=150_000)
    australian = make_opportunity(id="au", url="https://www.arc.gov.au/funding")
    request = SearchRequest(for_codes=["4611"])
    gap = (
        score_opportunity(international, request, DEFAULT_WEIGHTS, TODAY).overall
        - score_opportunity(australian, request, DEFAULT_WEIGHTS, TODAY).overall
    )
    assert 0 <= gap < AUSTRALIAN_BOOST
    ranked = rank([international, australian], request, DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in ranked] == ["au", "us"]


def test_the_boost_never_lifts_an_ineligible_australian_scheme_above_an_eligible_one():
    australian = make_opportunity(
        id="au", url="https://www.arc.gov.au/funding", citizenships_allowed=["AU"]
    )
    international = make_opportunity(id="us")
    request = SearchRequest(citizenships=["GB"])
    ranked = rank([australian, international], request, DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in ranked] == ["us", "au"]
