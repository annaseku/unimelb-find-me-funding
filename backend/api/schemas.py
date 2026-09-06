"""Response shapes for the search API. Request shapes live in
backend/ranking/models.py because the ranker shares them."""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.ranking.models import RankedOpportunity


class HealthResponse(BaseModel):
    status: str
    version: str


class SearchResponse(BaseModel):
    results: list[RankedOpportunity]
    total: int = Field(description="Size of the full ranked set, not of this page.")
    limit: int
    offset: int
    weights: dict[str, float] = Field(description="Weights used for this search, echoed.")
