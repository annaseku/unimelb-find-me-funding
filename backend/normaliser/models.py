"""Shapes shared across the normaliser: the crawler row coming in, the
normalised record going out, and where each field came from."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.ranking.models import Opportunity

# Which stage produced a field's value. "missing" means neither the rules nor
# the model found anything, so the Opportunity carries its default.
Source = Literal["rule", "llm", "missing"]


class CrawledRow(BaseModel):
    """One row of the crawler's `opportunities` table, as stored by
    backend/crawler/storage.py. Field names match the columns exactly."""

    url: str
    title: str | None = None
    raw_text: str | None = None
    deadline_raw: str | None = None
    deadline_parsed: str | None = None
    funding_amount_raw: str | None = None
    eligibility_snippet: str | None = None
    source_query: str | None = None
    first_seen_at: str | None = None
    fetched_at: str | None = None
    fetch_failed: int = 0


class NormalisedRecord(BaseModel):
    """An Opportunity plus the audit trail of how it was derived."""

    opportunity: Opportunity
    provenance: dict[str, Source] = Field(
        default_factory=dict,
        description="Opportunity field name to the stage that set it.",
    )
    content_hash: str = Field(description="SHA-256 of title plus raw text; skips unchanged pages.")
    used_llm: bool = False


# Why a run stopped calling the LLM before its last row. "daily_quota" is the
# provider rate-limiting past every retry; "plan_error" is a rejected key or no credits;
# "not_configured" means the run had no extractor at all.
LlmStopReason = Literal["daily_quota", "plan_error", "not_configured"]


class PipelineRun(BaseModel):
    """How one normaliser run went, so the frontend can say when AI fields are
    missing and why."""

    finished_at: datetime
    llm_calls: int = 0
    llm_failures: int = 0
    llm_stop_reason: LlmStopReason | None = None
    llm_stop_detail: str = ""
