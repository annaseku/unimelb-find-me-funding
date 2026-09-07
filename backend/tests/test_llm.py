"""Task 3: the extractor protocol, the Anthropic implementation, and the
merge policy that lets the model fill prose fields without ever overriding
a value the rules already parsed."""

from __future__ import annotations

from datetime import date

import pytest

from backend.normaliser.llm import (
    PROSE_FIELDS,
    RULE_PRIORITY_FIELDS,
    AnthropicExtractor,
    ExtractedFields,
    FakeExtractor,
    extractor_from_env,
    merge,
)
from backend.normaliser.models import NormalisedRecord
from backend.ranking.models import CareerStage, EmployerType, Opportunity


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


class StubMessages:
    def __init__(self, parsed_output):
        self.calls: list[dict] = []
        self._parsed_output = parsed_output

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return _StubResponse(self._parsed_output)


class _StubResponse:
    def __init__(self, parsed_output):
        self.parsed_output = parsed_output


class StubClient:
    def __init__(self, parsed_output):
        self.messages = StubMessages(parsed_output)


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


def test_anthropic_extractor_calls_the_client_with_expected_kwargs():
    stub_result = ExtractedFields(summary="A summary.")
    client = StubClient(stub_result)
    extractor = AnthropicExtractor(client=client, model="claude-test-model")

    long_text = "word " * 10_000  # far longer than MAX_TEXT_CHARS
    result = extractor.extract("A Title", "https://example.org/page", long_text)

    assert result is stub_result
    assert len(client.messages.calls) == 1
    kwargs = client.messages.calls[0]
    assert kwargs["model"] == "claude-test-model"
    assert kwargs["output_format"] is ExtractedFields
    assert kwargs["max_tokens"] == 4096
    assert "system" in kwargs and kwargs["system"]

    content = kwargs["messages"][0]["content"]
    assert "A Title" in content
    assert "https://example.org/page" in content
    # the raw text was truncated before being sent
    assert len(content) < len(long_text)


def test_anthropic_extractor_defaults_model_from_env(monkeypatch):
    monkeypatch.setenv("FMF_LLM_MODEL", "claude-opus-5-env")
    client = StubClient(ExtractedFields())
    extractor = AnthropicExtractor(client=client)

    extractor.extract("Title", "https://example.org", "text")

    assert client.messages.calls[0]["model"] == "claude-opus-5-env"


def test_extractor_from_env_with_no_key_is_none():
    assert extractor_from_env({}) is None


def test_extractor_from_env_with_key_returns_an_anthropic_extractor():
    extractor = extractor_from_env({"ANTHROPIC_API_KEY": "x"})
    assert isinstance(extractor, AnthropicExtractor)


def test_extractor_from_env_off_switch_is_none():
    assert extractor_from_env({"ANTHROPIC_API_KEY": "x", "FMF_LLM": "off"}) is None


@pytest.mark.parametrize("key", ["", None])
def test_extractor_from_env_empty_key_is_none(key):
    env = {} if key is None else {"ANTHROPIC_API_KEY": key}
    assert extractor_from_env(env) is None
