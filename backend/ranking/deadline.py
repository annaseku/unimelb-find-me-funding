"""Time-to-deadline banding (client criterion 4).

Bands are from the brief. More lead time scores higher because the client
said a deadline six months out is far more useful than one due next week;
the architecture page's phrase "deadline urgency" reads the other way, so
this is on the discussion list. `today` is always passed in so the ranker
never reads the clock and tests stay deterministic.
"""

from __future__ import annotations

from datetime import date

from backend.ranking.models import CriterionResult, DeadlineBand, Opportunity

# (lowest days remaining inclusive, band, score), checked from the top down.
BANDS: list[tuple[int, DeadlineBand, float]] = [
    (61, DeadlineBand.OVER_60_DAYS, 1.0),
    (30, DeadlineBand.DAYS_60_TO_30, 0.8),
    (15, DeadlineBand.DAYS_30_TO_15, 0.5),
    (0, DeadlineBand.UNDER_15_DAYS, 0.2),
]
CLOSED_SCORE = 0.0
UNKNOWN_SCORE = 0.5


def days_remaining(opportunity: Opportunity, today: date) -> int | None:
    if opportunity.deadline is None:
        return None
    return (opportunity.deadline - today).days


def score_deadline(opportunity: Opportunity, today: date) -> CriterionResult:
    days = days_remaining(opportunity, today)
    reasons: list[str] = []
    if opportunity.opens_at and opportunity.opens_at > today:
        reasons.append(f"Opens on {opportunity.opens_at.isoformat()}.")

    if days is None:
        reasons.insert(0, "No deadline stated.")
        return CriterionResult(score=UNKNOWN_SCORE, label=DeadlineBand.UNKNOWN, reasons=reasons)
    if days < 0:
        reasons.insert(0, f"Closed on {opportunity.deadline.isoformat()}.")
        return CriterionResult(score=CLOSED_SCORE, label=DeadlineBand.CLOSED, reasons=reasons)
    for lowest_days, band, score in BANDS:
        if days >= lowest_days:
            reasons.insert(0, f"Closes in {days} days ({opportunity.deadline.isoformat()}).")
            return CriterionResult(score=score, label=band, reasons=reasons)
    raise AssertionError("unreachable: every non-negative day count lands in a band")
