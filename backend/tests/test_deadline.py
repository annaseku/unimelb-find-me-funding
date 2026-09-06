"""More lead time scores higher (team decision, flagged for the client)."""

from datetime import timedelta

import pytest

from backend.ranking.deadline import days_remaining, score_deadline
from backend.ranking.models import DeadlineBand, Opportunity
from backend.tests.conftest import TODAY


def make_opportunity(days=None, opens_in=None) -> Opportunity:
    return Opportunity(
        id="o1",
        title="T",
        funder="F",
        url="https://example.org",
        summary="s",
        deadline=None if days is None else TODAY + timedelta(days=days),
        opens_at=None if opens_in is None else TODAY + timedelta(days=opens_in),
    )


@pytest.mark.parametrize(
    ("days", "band", "score"),
    [
        (200, DeadlineBand.OVER_60_DAYS, 1.0),
        (61, DeadlineBand.OVER_60_DAYS, 1.0),
        (60, DeadlineBand.DAYS_60_TO_30, 0.8),
        (30, DeadlineBand.DAYS_60_TO_30, 0.8),
        (29, DeadlineBand.DAYS_30_TO_15, 0.5),
        (15, DeadlineBand.DAYS_30_TO_15, 0.5),
        (14, DeadlineBand.UNDER_15_DAYS, 0.2),
        (0, DeadlineBand.UNDER_15_DAYS, 0.2),
        (-1, DeadlineBand.CLOSED, 0.0),
        (None, DeadlineBand.UNKNOWN, 0.5),
    ],
)
def test_band_edges(days, band, score):
    result = score_deadline(make_opportunity(days), TODAY)
    assert result.label == band
    assert result.score == score


def test_days_remaining_is_none_without_a_deadline():
    assert days_remaining(make_opportunity(None), TODAY) is None


def test_future_opening_date_is_mentioned():
    result = score_deadline(make_opportunity(days=120, opens_in=30), TODAY)
    assert any("opens on" in r.lower() for r in result.reasons)


def test_reason_mentions_days_remaining():
    assert "45 days" in score_deadline(make_opportunity(45), TODAY).reasons[0]
