"""The LLM extractor and the policy for merging its output onto a rule-built
record. Rules always win on dates and amounts; the model only fills the
prose-derived fields the rules cannot reach (funder name, summary,
eligibility paraphrase, and the classification lists).

The model is reached through OpenRouter (OpenAI-compatible, pay-as-you-go),
defaulting to a small open-weight model; Gemini's free tier throttled every
crawl (KAN-67, KAN-69). The `Extractor` protocol keeps the pipeline
indifferent to which provider sits behind it."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import date
from typing import Any, Protocol

from openai import OpenAI
from pydantic import BaseModel

from backend.normaliser.models import NormalisedRecord
from backend.ranking.models import CareerStage, EmployerType, FundingType, OpportunityStatus

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Apache-2.0 open-weight, non-reasoning, supports structured outputs, and costs
# about US$0.10 a weekly crawl. Override with FMF_LLM_MODEL (any OpenRouter id).
DEFAULT_MODEL = "qwen/qwen3-30b-a3b-instruct-2507"
MAX_TEXT_CHARS = 20_000
# One stalled request once hung a crawl run for 4.5 hours (2026-10-18). A
# timeout raises, and the pipeline goes rules-only for that row.
REQUEST_TIMEOUT_S = 60.0
# The timeout never fires while tokens keep arriving: four runaway replies of up
# to 790,000 characters held run 39157596776 for over four hours (KAN-70). A
# full ExtractedFields reply is a few hundred tokens, so a capped runaway ends
# in seconds as invalid JSON and the row falls back to rules.
MAX_OUTPUT_TOKENS = 1500

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

`is_funding_opportunity` is true when the page describes one or more grants, fellowships,
scholarships, awards, prizes or funding programmes that researchers or students can apply
for, or a funder's listing or index of such schemes. It is false for dictionary entries,
encyclopaedia articles, software or technical documentation, news articles that announce no
scheme, videos, shops and commercial product pages, generic organisation home pages that
name no scheme, job adverts, journal home pages, search-engine, login or CAPTCHA pages.
Leave it null only when the page text is too short or garbled to tell.

Dates are ISO 8601 (YYYY-MM-DD)."""


class ExtractedFields(BaseModel):
    """The funding classification and fields the model may contribute.
    Defaults are all "not stated"."""

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


def _strip_code_fence(text: str) -> str:
    """Some models wrap JSON in a ```json fence even when asked for JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return text


class OpenRouterExtractor:
    """Calls a model through OpenRouter and asks for JSON that matches
    ExtractedFields. The client is built lazily so importing this module never
    needs a key."""

    def __init__(
        self, client: Any | None = None, model: str | None = None, api_key: str | None = None
    ) -> None:
        self._client = (
            client
            if client is not None
            else OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=api_key or os.environ.get("OPENROUTER_API_KEY"),
                timeout=REQUEST_TIMEOUT_S,
            )
        )
        self._model = model or os.environ.get("FMF_LLM_MODEL") or DEFAULT_MODEL

    def extract(self, title: str, url: str, text: str) -> ExtractedFields:
        truncated = (text or "")[:MAX_TEXT_CHARS]
        contents = f"Title: {title}\nURL: {url}\n\n{truncated}"
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": contents},
            ],
            # The full JSON schema, so optional fields and enums round-trip
            # exactly; we validate the text ourselves rather than trust it.
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extracted_fields",
                    "schema": ExtractedFields.model_json_schema(),
                },
            },
            temperature=0,
            max_tokens=MAX_OUTPUT_TOKENS,
            # Route only to providers that honour response_format for this model.
            extra_body={"provider": {"require_parameters": True}},
        )
        content = response.choices[0].message.content or ""
        return ExtractedFields.model_validate_json(_strip_code_fence(content))


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

    if extracted.is_funding_opportunity is False:
        opportunity.status = OpportunityStatus.NOT_FUNDING
        provenance["status"] = "llm"

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
    """None when there is no OPENROUTER_API_KEY, or FMF_LLM is explicitly
    turned off; otherwise a real OpenRouterExtractor."""

    source = env if env is not None else os.environ
    key = source.get("OPENROUTER_API_KEY")
    if not key:
        return None
    if source.get("FMF_LLM", "").lower() == "off":
        return None
    return OpenRouterExtractor(api_key=key, model=source.get("FMF_LLM_MODEL") or None)
