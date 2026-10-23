"""Shared data model for the ranking engine and the search API.

The enum values deliberately match the keys in backend/crawler/query_builder.py
and the frontend drop-downs, so all three sides speak the same vocabulary.
Implements Confluence decision 4 (four eligibility states) and decision 5
(four separate scores reported alongside the overall).
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class EmployerType(StrEnum):
    UNIVERSITY = "university"
    RESEARCH_INSTITUTE = "research_institute"
    INDUSTRY = "industry"
    PHILANTHROPIC = "philanthropic"


class CareerStage(StrEnum):
    UNDERGRADUATE = "undergraduate"
    GRADUATE_STUDENT = "graduate_student"
    POSTDOC_0_2 = "postdoc_0_2"
    POSTDOC_2_5 = "postdoc_2_5"
    POSTDOC_5_10 = "postdoc_5_10"
    POSTDOC_10_PLUS = "postdoc_10_plus"


class FundingType(StrEnum):
    SALARY = "salary"
    CONSUMABLES = "consumables"
    EQUIPMENT = "equipment"
    ALL = "all"  # the researcher wants every kind
    ANY = "any"  # the researcher has no preference


class EligibilityState(StrEnum):
    """Decision 4: four states, never a yes/no."""

    ELIGIBLE = "eligible"
    POTENTIALLY_ELIGIBLE = "potentially_eligible"
    UNKNOWN = "unknown"
    LIKELY_INELIGIBLE = "likely_ineligible"


class MatchLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DeadlineBand(StrEnum):
    """The bands named in the client brief, plus closed and unknown."""

    OVER_60_DAYS = "over_60_days"
    DAYS_60_TO_30 = "days_60_to_30"
    DAYS_30_TO_15 = "days_30_to_15"
    UNDER_15_DAYS = "under_15_days"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class FundingBand(StrEnum):
    UNDER_1M = "under_1m"
    FROM_1M_TO_2M = "from_1m_to_2m"
    FROM_2M_TO_5M = "from_2m_to_5m"
    OVER_5M = "over_5m"
    UNKNOWN = "unknown"


class OpportunityStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"  # soft-deleted, decision 9


class Opportunity(BaseModel):
    """One funding opportunity, already deduplicated across its sources.

    An empty list for any *_allowed or *_offered field means the funder
    states no restriction (or we could not find one), not "nobody".
    """

    id: str
    title: str
    funder: str
    url: str
    source_urls: list[str] = Field(default_factory=list)
    summary: str
    amount_aud: int | None = Field(default=None, description="Maximum available, AUD.")
    amount_note: str = ""
    deadline: date | None = None
    opens_at: date | None = None
    countries: list[str] = Field(
        default_factory=list,
        description="Where the applicant's institution must be based. Informational for now.",
    )
    citizenships_allowed: list[str] = Field(default_factory=list)
    employer_types_allowed: list[EmployerType] = Field(default_factory=list)
    career_stages_allowed: list[CareerStage] = Field(default_factory=list)
    funding_types_offered: list[FundingType] = Field(default_factory=list)
    for_codes: list[str] = Field(default_factory=list, description="ANZSRC 2020 FoR codes.")
    toa_codes: list[str] = Field(
        default_factory=list, description="ANZSRC type of activity, '1' to '4'."
    )
    keywords: list[str] = Field(default_factory=list)
    eligibility_text: str = Field(
        default="", description="Funder prose, kept for a future LLM check."
    )
    status: OpportunityStatus = OpportunityStatus.ACTIVE


class SearchRequest(BaseModel):
    """The drop-downs and free text from the frontend. Everything is optional."""

    for_codes: list[str] = Field(default_factory=list)
    toa_codes: list[str] = Field(default_factory=list)
    citizenships: list[str] = Field(default_factory=list, description="ISO 3166-1 alpha-2.")
    institution_country: str = Field(
        default="AU",
        description="ISO 3166-1 alpha-2 of the researcher's institution; UoM is in Australia.",
    )
    employer_type: EmployerType | None = None
    career_stage: CareerStage | None = None
    funding_types: list[FundingType] = Field(default_factory=list)
    research_description: str = ""
    hide_ineligible: bool = False
    include_closed: bool = False
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    weights: dict[str, float] | None = Field(
        default=None, description="Partial override of the default weights."
    )


class CriterionResult(BaseModel):
    """One of the four ratings shown next to a result."""

    score: float = Field(ge=0.0, le=1.0)
    label: str
    reasons: list[str] = Field(default_factory=list)


class RankedOpportunity(BaseModel):
    """Decision 5: the four scores stay separate next to the overall."""

    opportunity: Opportunity
    overall: float = Field(ge=0.0, le=1.0)
    eligibility: CriterionResult
    research_match: CriterionResult
    funding_value: CriterionResult
    deadline: CriterionResult
