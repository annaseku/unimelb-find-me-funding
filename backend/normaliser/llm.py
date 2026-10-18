"""The LLM extractor and the policy for merging its output onto a rule-built
record. Rules always win on dates and amounts; the model only fills the
prose-derived fields the rules cannot reach (funder name, summary,
eligibility paraphrase, and the classification lists).

The model is Gemini, the team's choice for its free tier. The `Extractor`
protocol keeps the pipeline indifferent to which provider sits behind it."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import date
from typing import Any, Protocol

from google import genai
from google.genai import types
from pydantic import BaseModel

from backend.normaliser.models import NormalisedRecord
from backend.ranking.models import CareerStage, EmployerType, FundingType

# Stable Flash model; override with FMF_LLM_MODEL. Chosen for the free tier,
# not for peak quality; a Pro model is a one-variable change.
DEFAULT_MODEL = "gemini-2.5-flash"
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

`summary` is two to three plain sentences describing what the scheme funds.

`is_funding_opportunity` is true when the page describes one or more specific grants,
fellowships, scholarships or awards that someone can apply for, or lists them. It is false for
dictionary or encyclopedia entries, news, journal or publisher pages, job boards, videos,
shops, software documentation and general information pages.

Dates are ISO 8601 (YYYY-MM-DD)."""


class ExtractedFields(BaseModel):
    """Everything the model may contribute, one field per Opportunity field
    it is allowed to touch. Defaults are all "not stated"."""

    # The model's verdict on the page as a whole; not an Opportunity field,
    # so merge never copies it. Only an explicit False drops the page.
    is_funding_opportunity: bool | None = None
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


class GeminiExtractor:
    """Calls the Gemini API and asks for JSON that matches ExtractedFields.
    The client is built lazily so importing this module never needs a key;
    `genai.Client()` reads GEMINI_API_KEY from the environment itself."""

    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        self._client = client if client is not None else genai.Client()
        # `or`, not a .get default: the crawl workflow passes an unset
        # repository variable through as an empty string.
        self._model = model or os.environ.get("FMF_LLM_MODEL") or DEFAULT_MODEL

    def extract(self, title: str, url: str, text: str) -> ExtractedFields:
        truncated = (text or "")[:MAX_TEXT_CHARS]
        contents = f"Title: {title}\nURL: {url}\n\n{truncated}"
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                # The full JSON schema, so optional fields and enums round-trip
                # exactly; we validate the text ourselves rather than rely on
                # the SDK's parsed attribute.
                response_json_schema=ExtractedFields.model_json_schema(),
                temperature=0,
            ),
        )
        return ExtractedFields.model_validate_json(response.text)


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
    """None when there is no GEMINI_API_KEY, or FMF_LLM is explicitly turned
    off; otherwise a real GeminiExtractor."""

    source = env if env is not None else os.environ
    if not source.get("GEMINI_API_KEY"):
        return None
    if source.get("FMF_LLM", "").lower() == "off":
        return None
    return GeminiExtractor()
