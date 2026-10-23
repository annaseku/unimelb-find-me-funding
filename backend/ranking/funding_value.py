"""Funding value banding (client criterion 3).

Bands are the ones in the root README's ranking table. Most single-project
grants fall in the bottom band, which the team has flagged for the client;
change the edges in BANDS if that decision changes.
"""

from __future__ import annotations

from backend.ranking.models import CriterionResult, FundingBand, Opportunity

# (lower edge inclusive, band, score), checked from the top down.
BANDS: list[tuple[int, FundingBand, float]] = [
    (5_000_000, FundingBand.OVER_5M, 1.0),
    (2_000_000, FundingBand.FROM_2M_TO_5M, 0.75),
    (1_000_000, FundingBand.FROM_1M_TO_2M, 0.5),
    (0, FundingBand.UNDER_1M, 0.25),
]
UNKNOWN_SCORE = 0.5

_LABELS = {
    FundingBand.OVER_5M: "$5M or more",
    FundingBand.FROM_2M_TO_5M: "$2M to $5M",
    FundingBand.FROM_1M_TO_2M: "$1M to $2M",
    FundingBand.UNDER_1M: "under $1M",
}


def score_funding_value(opportunity: Opportunity) -> CriterionResult:
    amount = opportunity.amount_aud
    if amount is None:
        # Decision 4 applies to amounts too: unknown sits mid-range, not at zero.
        return CriterionResult(
            score=UNKNOWN_SCORE, label=FundingBand.UNKNOWN, reasons=["Funding amount not stated."]
        )
    for lower_edge, band, score in BANDS:
        if amount >= lower_edge:
            note = f" ({opportunity.amount_note})" if opportunity.amount_note else ""
            return CriterionResult(
                score=score,
                label=band,
                reasons=[f"Up to ${amount:,} AUD{note}, in the {_LABELS[band]} band."],
            )
    raise ValueError(f"negative funding amount on {opportunity.id}")
