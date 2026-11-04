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
# No deadline but a published future opening date.
UNKNOWN_SCORE = 0.5
# No deadline and no future opening date: the client called these "not really
# useful" next to open or future-dated schemes (feedback form 26/10, KAN-83).
# A score, not a hard tier, so a rolling scheme with a strong match still ranks.
NO_ROUND_SCORE = 0.0


def days_remaining(opportunity: Opportunity, today: date) -> int | None:
    if opportunity.deadline is None:
        return None
    return (opportunity.deadline - today).days


def score_deadline(opportunity: Opportunity, today: date) -> CriterionResult:
    days = days_remaining(opportunity, today)
    opens_later = opportunity.opens_at is not None and opportunity.opens_at > today
    reasons: list[str] = []
    if opens_later:
        reasons.append(f"Opens on {opportunity.opens_at.isoformat()}.")

    if days is None:
        reasons.insert(0, "No deadline stated.")
        if not opens_later:
            reasons.append("No current or future round published, so it ranks lower.")
            return CriterionResult(
                score=NO_ROUND_SCORE, label=DeadlineBand.UNKNOWN, reasons=reasons
            )
        return CriterionResult(score=UNKNOWN_SCORE, label=DeadlineBand.UNKNOWN, reasons=reasons)
    if days < 0:
        reasons.insert(0, f"Closed on {opportunity.deadline.isoformat()}.")
        return CriterionResult(score=CLOSED_SCORE, label=DeadlineBand.CLOSED, reasons=reasons)
    for lowest_days, band, score in BANDS:
        if days >= lowest_days:
            reasons.insert(0, f"Closes in {days} days ({opportunity.deadline.isoformat()}).")
            return CriterionResult(score=score, label=band, reasons=reasons)
    raise AssertionError("unreachable: every non-negative day count lands in a band")
