"""Weights are the one knob the team has agreed is configurable (decision 5)."""

import pytest
from pydantic import ValidationError

from backend.ranking.weights import DEFAULT_WEIGHTS, Weights, resolve_weights


def test_defaults_put_eligibility_first_as_the_client_asked():
    assert DEFAULT_WEIGHTS.eligibility == max(DEFAULT_WEIGHTS.as_dict().values())


def test_default_weights_sum_to_one():
    assert sum(DEFAULT_WEIGHTS.as_dict().values()) == pytest.approx(1.0)


def test_all_zero_weights_are_rejected():
    with pytest.raises(ValidationError):
        Weights(eligibility=0, research_match=0, funding_value=0, deadline=0)


def test_negative_weight_is_rejected():
    with pytest.raises(ValidationError):
        Weights(eligibility=-1, research_match=1, funding_value=1, deadline=1)


def test_partial_override_keeps_the_other_defaults():
    weights = resolve_weights({"research_match": 0.9})
    assert weights.research_match == 0.9
    assert weights.eligibility == DEFAULT_WEIGHTS.eligibility


def test_none_override_returns_defaults():
    assert resolve_weights(None) == DEFAULT_WEIGHTS


def test_unknown_key_is_rejected():
    with pytest.raises(ValidationError):
        resolve_weights({"vibes": 1.0})
