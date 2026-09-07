"""The LLM extractor and the policy for merging its output onto a rule-built
record. Rules always win on dates and amounts; the model only fills the
prose-derived fields the rules cannot reach (funder name, summary,
eligibility paraphrase, and the classification lists)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import date
from typing import Any, Protocol

import anthropic
from pydantic import BaseModel

from backend.normaliser.models import NormalisedRecord
from backend.ranking.models import CareerStage, EmployerType, FundingType

DEFAULT_MODEL = "claude-opus-5"
MAX_TEXT_CHARS = 20_000

# Fields the model may set or override, provided it returns a non-empty
# value. Anything not listed here (amount and deadline) is rule-priority.
PROSE_FIELDS: frozenset[str] = frozenset(
    {
        "funder",
        "summary",
        "opens_at",
        "countries",
        "citizenships_allowed",
        "employer_types_allowed",
        "career_stages_allowed",
        "funding_types_offered",
        "for_codes",
        "toa_codes",
        "keywords",
        "eligibility_text",
    }
)

# Fields a rule parses directly from the page. The model may only fill these
# in when the rules found nothing at all, never override a value the rules set.
RULE_PRIORITY_FIELDS: frozenset[str] = frozenset({"amount_aud", "amount_note", "deadline"})

SYSTEM_PROMPT = """You extract structured funding-opportunity data from a crawled web page.

Extract only what the page states. Leave a field null (or an empty list) when the page does
not state it: never guess or infer a value that is not written down.

Use ISO 3166-1 alpha-2 codes for `countries` and `citizenships_allowed`. `countries` means
the countries where the applicant's institution must be based, not where the funder is
headquartered.

Use ANZSRC 2020 codes (two or four digits) for `for_codes`. Use "1" to "4" for `toa_codes`.

`amount_aud` is the maximum amount available, in whole Australian dollars. Convert other
currencies approximately and explain the conversion in `amount_note`. Leave both null when
no amount is stated.

`eligibility_text` is a faithful one to three sentence paraphrase of the stated eligibility
rules, not a copy of the whole page.

`summary` is two to three plain sentences describing what the scheme funds."""


class ExtractedFields(BaseModel):
    """Everything the model may contribute, one field per Opportunity field
    it is allowed to touch. Defaults are all "not stated"."""

    funder: str | None = None
    summary: str | None = None
    amount_aud: int | None = None
    amount_note: str | None = None
    deadline: date | None = None
    opens_at: date | None = None
    countries: list[str] = []
    citizenships_allowed: list[str] = []
    employer_types_allowed: list[EmployerType] = []
    career_stages_allowed: list[CareerStage] = []
    funding_types_offered: list[FundingType] = []
    for_codes: list[str] = []
    toa_codes: list[str] = []
    keywords: list[str] = []
    eligibility_text: str | None = None


class Extractor(Protocol):
    def extract(self, title: str, url: str, text: str) -> ExtractedFields: ...


class AnthropicExtractor:
    """Calls the Anthropic API with structured outputs. The client is built
    lazily so importing this module never requires an API key."""

    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        self._client = client if client is not None else anthropic.Anthropic()
        self._model = model or os.environ.get("FMF_LLM_MODEL", DEFAULT_MODEL)

    def extract(self, title: str, url: str, text: str) -> ExtractedFields:
        truncated = (text or "")[:MAX_TEXT_CHARS]
        content = f"Title: {title}\nURL: {url}\n\n{truncated}"
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
            output_format=ExtractedFields,
        )
        return response.parsed_output


class FakeExtractor:
    """Test double: always returns the same result, and remembers every call."""

    def __init__(self, result: ExtractedFields) -> None:
        self._result = result
        self.calls: list[tuple[str, str, str]] = []

    def extract(self, title: str, url: str, text: str) -> ExtractedFields:
        self.calls.append((title, url, text))
        return self._result


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or value == []


def merge(record: NormalisedRecord, extracted: ExtractedFields) -> NormalisedRecord:
    """Layer the model's output onto a rule-built record. Never mutates
    `record`; always returns a new one with `used_llm=True`."""

    opportunity = record.opportunity.model_copy(deep=True)
    provenance = dict(record.provenance)

    for field in PROSE_FIELDS:
        value = getattr(extracted, field)
        if not _is_empty(value):
            setattr(opportunity, field, value)
            provenance[field] = "llm"

    # Amount and deadline are rule-priority: the model only fills a gap, it
    # never overrides a value the rules already parsed from the page.
    if provenance.get("amount_aud", "missing") == "missing" and extracted.amount_aud is not None:
        opportunity.amount_aud = extracted.amount_aud
        opportunity.amount_note = extracted.amount_note or ""
        provenance["amount_aud"] = "llm"
        provenance["amount_note"] = "llm"

    if provenance.get("deadline", "missing") == "missing" and extracted.deadline is not None:
        opportunity.deadline = extracted.deadline
        provenance["deadline"] = "llm"

    return NormalisedRecord(
        opportunity=opportunity,
        provenance=provenance,
        content_hash=record.content_hash,
        used_llm=True,
    )


def extractor_from_env(env: Mapping[str, str] | None = None) -> Extractor | None:
    """None when there is no API key, or FMF_LLM is explicitly turned off;
    otherwise a real AnthropicExtractor."""

    source = env if env is not None else os.environ
    if not source.get("ANTHROPIC_API_KEY"):
        return None
    if source.get("FMF_LLM", "").lower() == "off":
        return None
    return AnthropicExtractor()
