"""Research match is deterministic keyword and code overlap for now. The
docstring in the module names where an embedding or LLM scorer slots in."""

import math
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
import snowballstemmer

from backend.ranking.models import MatchLevel, Opportunity, SearchRequest
from backend.ranking.research_match import TermWeights, _stem, score_research_match, tokenize


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
    assert result.score == 1.0
    assert any("3103" in r for r in result.reasons)


def test_same_division_only_is_medium():
    result = score_research_match(make_opportunity(), SearchRequest(for_codes=["3104"]))
    assert result.label == MatchLevel.MEDIUM
    assert result.score == 0.5


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


def test_career_and_care_do_not_collide():
    assert _stem("career") != _stem("care")


@pytest.mark.parametrize(
    "words",
    [
        "including include involving involve related relating various specific particular general "
        "approach method methods area areas field fields work working focus focused aim aims "
        "develop developing development improve improving understand understanding investigate "
        "investigating explore exploring",
        "fellowship scholarship award prize early career postdoctoral postdoc phd doctoral "
        "researcher programme program scheme opportunity apply application applicant eligible "
        "eligibility funded support supported available provide offer university institute "
        "institution",
    ],
    ids=["filler", "funding"],
)
def test_filler_and_funding_vocabulary_do_not_contribute_to_opportunity_tokens(words):
    assert tokenize(words) == set()


def test_stop_word_inflections_do_not_contribute_to_opportunity_tokens():
    assert (
        tokenize("studies researchers applications fellowships opportunities scholarships") == set()
    )


def test_stop_word_inflections_do_not_dilute_description_coverage_or_appear_in_reasons():
    result = score_research_match(
        make_opportunity(title="Chemistry", summary="", keywords=[]),
        SearchRequest(
            research_description="Studies researchers applications scholarships chemistry"
        ),
    )
    assert result.score == 1.0
    assert result.reasons == ["Your description shares terms with the opportunity: chemistry."]


@pytest.mark.parametrize("weighted", [False, True])
def test_funding_only_description_is_medium_without_research_details(weighted):
    opportunity = make_opportunity(title="Early career fellowship", summary="", keywords=[])
    weights = TermWeights.from_opportunities([opportunity]) if weighted else None
    result = score_research_match(
        opportunity, SearchRequest(research_description="early career fellowship"), weights
    )
    assert result.score == 0.5
    assert result.label == MatchLevel.MEDIUM
    assert result.reasons == ["No research details were supplied to match on."]


@pytest.mark.parametrize("weighted", [False, True])
def test_funding_terms_do_not_match_a_research_topic_but_chemistry_does(weighted):
    funding = make_opportunity(
        id="funding", title="Early career fellowship", summary="", keywords=[]
    )
    chemistry = make_opportunity(id="chemistry", title="Chemistry", summary="", keywords=[])
    weights = TermWeights.from_opportunities([funding, chemistry]) if weighted else None
    request = SearchRequest(research_description="early career fellowship in chemistry")
    unrelated = score_research_match(funding, request, weights)
    matched = score_research_match(chemistry, request, weights)
    assert unrelated.score == 0.0
    assert unrelated.label == MatchLevel.LOW
    assert unrelated.reasons == ["Your description shares no terms with the opportunity."]
    assert matched.score == 1.0
    assert matched.label == MatchLevel.HIGH
    assert matched.reasons == ["Your description shares terms with the opportunity: chemistry."]


@pytest.mark.parametrize(
    ("first", "second", "stem"),
    [
        ("learning", "learn", "learn"),
        ("imaging", "image", "imag"),
        ("modelling", "models", "model"),
        ("studies", "study", "studi"),
    ],
)
def test_porter2_matches_related_words(first, second, stem):
    assert _stem(first) == _stem(second) == stem


def test_function_words_do_not_contribute_to_text_matches():
    assert not tokenize(
        "under over between within about after before through during into onto up down out "
        "more most other some such than then these those both each how what which who also "
        "can may could would should do does did not no I my me am you your they their them "
        "he she his her there here where when all any very just well way like etc"
    )


def weighted_corpus():
    opportunities = [
        make_opportunity(id=str(i), title="Learning", summary="", keywords=[]) for i in range(20)
    ]
    opportunities[-1] = make_opportunity(id="rare", title="Coral", summary="", keywords=[])
    return opportunities, TermWeights.from_opportunities(opportunities)


def test_a_single_shared_ubiquitous_term_stays_low():
    opportunities, weights = weighted_corpus()
    result = score_research_match(
        opportunities[0],
        SearchRequest(research_description="learning coral reef ecology"),
        weights,
    )
    assert result.label == MatchLevel.LOW
    assert result.score < 0.4


def test_a_rare_shared_term_outweighs_a_common_one():
    opportunities, weights = weighted_corpus()
    request = SearchRequest(research_description="learning coral reef ecology")
    common = score_research_match(opportunities[0], request, weights)
    rare = score_research_match(opportunities[-1], request, weights)
    assert rare.score > common.score
    assert weights.weight("learn") == pytest.approx(math.log(21 / 20) + 1)
    assert weights.weight("coral") == pytest.approx(math.log(21 / 2) + 1)
    assert weights.weight("ecolog") == pytest.approx(math.log(21) + 1)


def test_reasons_show_first_description_words_in_descending_weight_order():
    opportunity = make_opportunity(title="Learning image models", summary="", keywords=[])
    corpus = [opportunity] + [
        make_opportunity(id=str(i), title="Learning", summary="", keywords=[]) for i in range(10)
    ]
    result = score_research_match(
        opportunity,
        SearchRequest(research_description="learning Imaging image modelling models"),
        TermWeights.from_opportunities(corpus),
    )
    assert result.reasons == [
        "Your description shares terms with the opportunity: Imaging, modelling, learning."
    ]


def test_none_weights_keep_unweighted_coverage():
    opportunity = make_opportunity(title="Learning", summary="", keywords=[])
    request = SearchRequest(research_description="learning coral reef ecology")
    default = score_research_match(opportunity, request)
    explicit = score_research_match(opportunity, request, weights=None)
    assert explicit == default
    assert explicit.score == 0.5
    assert explicit.label == MatchLevel.MEDIUM


def test_concurrent_stemming_keeps_each_words_mutable_state_separate(monkeypatch):
    # Force two real Porter2 calls to interleave after loading different words.
    barrier = Barrier(2)
    stemmer_type = type(snowballstemmer.stemmer("english"))
    set_current = stemmer_type.set_current

    def interleaved_set_current(self, word):
        set_current(self, word)
        if word:
            barrier.wait(timeout=2)

    _stem.cache_clear()
    monkeypatch.setattr(stemmer_type, "set_current", interleaved_set_current)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {word: pool.submit(_stem, word) for word in ("imaging", "career")}
            actual = {word: future.result(timeout=3) for word, future in futures.items()}
        assert actual == {"imaging": "imag", "career": "career"}
    finally:
        _stem.cache_clear()
