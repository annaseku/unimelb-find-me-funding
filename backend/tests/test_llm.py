"""The extractor protocol, the OpenRouter implementation, and the merge policy
that lets the model fill prose fields without ever overriding a value the
rules already parsed. No test touches the network."""

from __future__ import annotations

from datetime import date

import pytest

from backend.normaliser import llm as llm_module
from backend.normaliser.llm import (
    PROSE_FIELDS,
    RULE_PRIORITY_FIELDS,
    ExtractedFields,
    FakeExtractor,
    OpenRouterExtractor,
    extractor_from_env,
    merge,
)
from backend.normaliser.models import NormalisedRecord
from backend.ranking.models import CareerStage, EmployerType, Opportunity, OpportunityStatus


def make_record(**overrides) -> NormalisedRecord:
    """A rule-built record for a fictional scheme: deadline and funder came
    from a rule, amount_aud is missing (the rules found no figure)."""

    fields = {
        "id": "example-org-12345678",
        "title": "Example Fellowship",
        "funder": "example.org",
        "url": "https://example.org/fellowship",
        "source_urls": ["https://example.org/fellowship"],
        "summary": "A fellowship for early-career researchers.",
        "amount_aud": None,
        "amount_note": "",
        "deadline": date(2027, 1, 1),
        "citizenships_allowed": ["AU"],
    }
    fields.update(overrides)
    opportunity = Opportunity(**fields)
    return NormalisedRecord(
        opportunity=opportunity,
        provenance={
            "deadline": "rule",
            "amount_aud": "missing",
            "funder": "rule",
            "citizenships_allowed": "rule",
        },
        content_hash="abc123",
        used_llm=False,
    )


class _Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class StubCompletions:
    """Stands in for OpenAI().chat.completions: records kwargs, returns content."""

    def __init__(self, content: str):
        self.calls: list[dict] = []
        self._content = content

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _Obj(choices=[_Obj(message=_Obj(content=self._content))])


class StubClient:
    def __init__(self, content: str):
        self.chat = _Obj(completions=StubCompletions(content))

    @property
    def calls(self) -> list[dict]:
        return self.chat.completions.calls


def test_fake_extractor_records_every_call():
    result = ExtractedFields(funder="Recorded Funder")
    extractor = FakeExtractor(result)

    first = extractor.extract("Title A", "https://a.example", "text a")
    second = extractor.extract("Title B", "https://b.example", "text b")

    assert first is result
    assert second is result
    assert extractor.calls == [
        ("Title A", "https://a.example", "text a"),
        ("Title B", "https://b.example", "text b"),
    ]


def test_merge_overrides_a_prose_field_and_marks_provenance_llm():
    record = make_record(funder="example.org")
    extracted = ExtractedFields(funder="Example Research Council")

    merged = merge(record, extracted)

    assert merged.opportunity.funder == "Example Research Council"
    assert merged.provenance["funder"] == "llm"


def test_merge_keeps_a_rule_parsed_deadline_when_the_model_disagrees():
    record = make_record()
    extracted = ExtractedFields(deadline=date(2099, 12, 31))

    merged = merge(record, extracted)

    assert merged.opportunity.deadline == date(2027, 1, 1)
    assert merged.provenance["deadline"] == "rule"


def test_merge_fills_a_missing_amount_and_marks_it_llm():
    record = make_record()
    extracted = ExtractedFields(amount_aud=50_000, amount_note="stated in AUD on the page")

    merged = merge(record, extracted)

    assert merged.opportunity.amount_aud == 50_000
    assert merged.opportunity.amount_note == "stated in AUD on the page"
    assert merged.provenance["amount_aud"] == "llm"
    assert merged.provenance["amount_note"] == "llm"


def test_merge_does_not_fill_amount_when_a_rule_already_found_one():
    record = make_record(amount_aud=250_000, amount_note="stated in AUD")
    record = NormalisedRecord(
        opportunity=record.opportunity,
        provenance={**record.provenance, "amount_aud": "rule"},
        content_hash=record.content_hash,
    )
    extracted = ExtractedFields(amount_aud=999_999, amount_note="model guess")

    merged = merge(record, extracted)

    assert merged.opportunity.amount_aud == 250_000
    assert merged.opportunity.amount_note == "stated in AUD"
    assert merged.provenance["amount_aud"] == "rule"


def test_merge_empty_extracted_lists_do_not_wipe_rule_values():
    record = make_record()
    extracted = ExtractedFields()  # every list defaults to empty

    merged = merge(record, extracted)

    assert merged.opportunity.citizenships_allowed == ["AU"]
    assert merged.provenance["citizenships_allowed"] == "rule"


def test_merge_returns_a_new_record_and_never_mutates_the_input():
    record = make_record(funder="example.org")
    before = record.model_copy(deep=True)
    extracted = ExtractedFields(
        funder="Example Research Council",
        career_stages_allowed=[CareerStage.POSTDOC_0_2],
        employer_types_allowed=[EmployerType.UNIVERSITY],
    )

    merged = merge(record, extracted)

    assert record == before
    assert merged is not record
    assert merged.opportunity is not record.opportunity
    assert merged.used_llm is True
    assert record.used_llm is False


def test_merge_sets_used_llm_true_on_the_returned_record():
    record = make_record()
    merged = merge(record, ExtractedFields())
    assert merged.used_llm is True


def test_prose_and_rule_priority_field_sets_do_not_overlap():
    assert PROSE_FIELDS.isdisjoint(RULE_PRIORITY_FIELDS)
    assert "amount_aud" in RULE_PRIORITY_FIELDS
    assert "deadline" in RULE_PRIORITY_FIELDS
    assert "funder" in PROSE_FIELDS


def test_openrouter_extractor_calls_the_client_with_expected_kwargs():
    client = StubClient('{"summary": "A summary.", "for_codes": ["3103"]}')
    extractor = OpenRouterExtractor(client=client, model="vendor/test-model")

    long_text = "word " * 10_000  # far longer than MAX_TEXT_CHARS
    result = extractor.extract("A Title", "https://example.org/page", long_text)

    assert result == ExtractedFields(summary="A summary.", for_codes=["3103"])
    assert len(client.calls) == 1
    kwargs = client.calls[0]
    assert kwargs["model"] == "vendor/test-model"
    assert kwargs["temperature"] == 0
    response_format = kwargs["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["schema"] == ExtractedFields.model_json_schema()
    # Only providers that honour the schema may serve the request.
    assert kwargs["extra_body"] == {"provider": {"require_parameters": True}}

    system, user = kwargs["messages"]
    assert system["role"] == "system" and system["content"]
    assert "A Title" in user["content"]
    assert "https://example.org/page" in user["content"]
    # the raw text was truncated before being sent
    assert len(user["content"]) < len(long_text)


def test_openrouter_extractor_caps_the_reply_length():
    # Regression (crawl run 39157596776): with no cap, a runaway reply ran for
    # over an hour per page because the request timeout never fires mid-stream.
    client = StubClient("{}")
    OpenRouterExtractor(client=client, model="vendor/test-model").extract(
        "Title", "https://example.org", "text"
    )
    assert client.calls[0]["max_tokens"] == llm_module.MAX_OUTPUT_TOKENS
    assert llm_module.MAX_OUTPUT_TOKENS <= 2000


def test_openrouter_extractor_accepts_json_wrapped_in_a_code_fence():
    client = StubClient('```json\n{"summary": "Fenced."}\n```')
    extractor = OpenRouterExtractor(client=client, model="vendor/test-model")
    assert extractor.extract("T", "https://example.org", "text").summary == "Fenced."


def test_openrouter_extractor_defaults_to_an_open_weight_model(monkeypatch):
    monkeypatch.delenv("FMF_LLM_MODEL", raising=False)
    client = StubClient("{}")
    OpenRouterExtractor(client=client).extract("Title", "https://example.org", "text")
    assert client.calls[0]["model"] == llm_module.DEFAULT_MODEL


def test_openrouter_extractor_takes_the_model_from_env(monkeypatch):
    monkeypatch.setenv("FMF_LLM_MODEL", "vendor/from-env")
    client = StubClient("{}")
    OpenRouterExtractor(client=client).extract("Title", "https://example.org", "text")
    assert client.calls[0]["model"] == "vendor/from-env"


def test_openrouter_extractor_rejects_json_that_does_not_match_the_schema():
    client = StubClient('{"amount_aud": "lots"}')
    extractor = OpenRouterExtractor(client=client, model="vendor/test-model")

    with pytest.raises(ValueError):
        extractor.extract("Title", "https://example.org", "text")


def test_extractor_from_env_with_no_key_is_none():
    assert extractor_from_env({}) is None


def test_extractor_from_env_with_key_returns_an_openrouter_extractor():
    extractor = extractor_from_env({"OPENROUTER_API_KEY": "x"})
    assert isinstance(extractor, OpenRouterExtractor)


def test_a_leftover_gemini_key_no_longer_enables_the_extractor():
    assert extractor_from_env({"GEMINI_API_KEY": "x"}) is None


def test_extractor_from_env_off_switch_is_none():
    assert extractor_from_env({"OPENROUTER_API_KEY": "x", "FMF_LLM": "off"}) is None


@pytest.mark.parametrize("key", ["", None])
def test_extractor_from_env_empty_key_is_none(key):
    env = {} if key is None else {"OPENROUTER_API_KEY": key}
    assert extractor_from_env(env) is None


def test_client_targets_openrouter_with_the_key_and_a_request_timeout(monkeypatch):
    # Without a timeout, a stalled request hangs the whole crawl until the job limit.
    built = {}
    monkeypatch.setattr(llm_module, "OpenAI", lambda **kwargs: built.update(kwargs))
    OpenRouterExtractor(api_key="test-key")
    assert built == {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "test-key",
        "timeout": llm_module.REQUEST_TIMEOUT_S,
    }


def test_extractor_schema_includes_nullable_funding_classification():
    client = StubClient("{}")
    OpenRouterExtractor(client=client).extract("T", "https://example.org", "text")
    schema = client.calls[0]["response_format"]["json_schema"]["schema"]
    field = schema["properties"]["is_funding_opportunity"]
    assert {"type": "boolean"} in field["anyOf"]
    assert {"type": "null"} in field["anyOf"]
    assert field["default"] is None


def test_merge_soft_deletes_non_funding_and_records_llm_provenance_without_mutating_input():
    record = make_record()
    before = record.model_copy(deep=True)
    merged = merge(record, ExtractedFields(is_funding_opportunity=False))
    assert merged.opportunity.status == OpportunityStatus.NOT_FUNDING
    assert merged.provenance["status"] == "llm"
    assert record == before


@pytest.mark.parametrize("classification", [True, None])
@pytest.mark.parametrize("status", list(OpportunityStatus))
def test_merge_positive_or_unknown_classification_preserves_status_and_provenance(
    classification, status
):
    record = make_record(status=status)
    record.provenance["status"] = "rule"
    merged = merge(record, ExtractedFields(is_funding_opportunity=classification))
    assert merged.opportunity.status == status
    assert merged.provenance["status"] == "rule"


def test_funding_classification_is_not_a_prose_field():
    assert "is_funding_opportunity" not in PROSE_FIELDS
