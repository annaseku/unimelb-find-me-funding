"""Configurable weights for combining the four scores (decision 5).

The defaults are placeholders that put eligibility first because the client
called it the top priority. The relative weighting is still an open team
decision; see docs/ranking-discussion-points.md.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Weights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eligibility: float = Field(ge=0.0)
    research_match: float = Field(ge=0.0)
    funding_value: float = Field(ge=0.0)
    deadline: float = Field(ge=0.0)

    @model_validator(mode="after")
    def _at_least_one_non_zero(self) -> Weights:
        # An all-zero set would divide by zero when normalising.
        if self.total() == 0:
            raise ValueError("at least one weight must be greater than zero")
        return self

    def total(self) -> float:
        return self.eligibility + self.research_match + self.funding_value + self.deadline

    def as_dict(self) -> dict[str, float]:
        return self.model_dump()


DEFAULT_WEIGHTS = Weights(
    eligibility=0.4,
    research_match=0.3,
    funding_value=0.15,
    deadline=0.15,
)


def resolve_weights(override: dict[str, float] | Weights | None) -> Weights:
    """Merge a partial override from the request onto the defaults."""
    if override is None:
        return DEFAULT_WEIGHTS
    if isinstance(override, Weights):
        return override
    return Weights(**{**DEFAULT_WEIGHTS.as_dict(), **override})
