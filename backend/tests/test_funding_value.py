"""Funding bands follow the backend README proposal; edges are tested exactly."""

import pytest

from backend.ranking.funding_value import score_funding_value
from backend.ranking.models import FundingBand, Opportunity


def make_opportunity(amount) -> Opportunity:
    return Opportunity(
        id="o1", title="T", funder="F", url="https://example.org", summary="s", amount_aud=amount
    )


@pytest.mark.parametrize(
    ("amount", "band", "score"),
    [
        (1, FundingBand.UNDER_1M, 0.25),
        (999_999, FundingBand.UNDER_1M, 0.25),
        (1_000_000, FundingBand.FROM_1M_TO_2M, 0.5),
        (1_999_999, FundingBand.FROM_1M_TO_2M, 0.5),
        (2_000_000, FundingBand.FROM_2M_TO_5M, 0.75),
        (4_999_999, FundingBand.FROM_2M_TO_5M, 0.75),
        (5_000_000, FundingBand.OVER_5M, 1.0),
        (None, FundingBand.UNKNOWN, 0.5),
    ],
)
def test_band_edges(amount, band, score):
    result = score_funding_value(make_opportunity(amount))
    assert result.label == band
    assert result.score == score


def test_reason_states_the_amount():
    assert "$1,500,000" in score_funding_value(make_opportunity(1_500_000)).reasons[0]


def test_reason_for_unknown_amount():
    assert "not stated" in score_funding_value(make_opportunity(None)).reasons[0].lower()
