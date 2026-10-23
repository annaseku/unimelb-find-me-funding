"""Research match is deterministic keyword and code overlap for now. The
docstring in the module names where an embedding or LLM scorer slots in."""

from backend.ranking.models import MatchLevel, Opportunity, SearchRequest
from backend.ranking.research_match import score_research_match, tokenize


def make_opportunity(**overrides) -> Opportunity:
    base = {
        "id": "o1",
        "title": "Coral reef resilience grant",
        "funder": "F",
        "url": "https://example.org",
        "summary": "Supports research into coral reef ecosystems and ocean acidification.",
        "keywords": ["marine", "coral"],
        "for_codes": ["3103"],
        "toa_codes": ["3"],
    }
    return Opportunity(**{**base, **overrides})


def test_exact_for_code_match_is_high():
    result = score_research_match(make_opportunity(), SearchRequest(for_codes=["3103"]))
    assert result.label == MatchLevel.HIGH
    assert any("3103" in r for r in result.reasons)


def test_same_division_only_is_medium():
    result = score_research_match(make_opportunity(), SearchRequest(for_codes=["3104"]))
    assert result.label == MatchLevel.MEDIUM


def test_unrelated_for_code_and_unrelated_text_is_low():
    request = SearchRequest(for_codes=["4611"], research_description="quantum compilers")
    result = score_research_match(make_opportunity(), request)
    assert result.label == MatchLevel.LOW


def test_text_overlap_alone_can_reach_high():
    request = SearchRequest(research_description="coral reef ocean acidification")
    result = score_research_match(make_opportunity(for_codes=[], toa_codes=[]), request)
    assert result.label == MatchLevel.HIGH


def test_no_research_details_supplied_is_medium_half():
    result = score_research_match(make_opportunity(), SearchRequest())
    assert result.score == 0.5
    assert result.label == MatchLevel.MEDIUM
    assert any("no research details" in r.lower() for r in result.reasons)


def test_toa_match_adds_a_small_bonus():
    without = score_research_match(make_opportunity(), SearchRequest(for_codes=["3103"]))
    with_toa = score_research_match(
        make_opportunity(), SearchRequest(for_codes=["3103"], toa_codes=["3"])
    )
    assert with_toa.score >= without.score
    assert any("type of activity" in r.lower() for r in with_toa.reasons)


def test_tokenize_drops_stop_words_and_strips_common_suffixes():
    tokens = tokenize("The modelling of models and the research")
    assert "the" not in tokens
    assert "and" not in tokens
    assert "of" not in tokens
    assert "research" not in tokens
    # "modelling" and "models" should meet on a shared stem.
    assert len({t for t in tokens if t.startswith("model")}) == 1
