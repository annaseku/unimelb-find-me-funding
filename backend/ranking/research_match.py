"""Research match: how well the opportunity fits what the researcher wants
to fund (client criterion 2, decision 3's "research fit").

Three signals, each 0.0 to 1.0, combined with fixed internal weights and
renormalised over the signals that could actually be evaluated:

  FoR code overlap   0.5   exact ANZSRC code, or half credit for same division
  text overlap       0.4   description tokens found in the opportunity text
  ToA code overlap   0.1   type of activity

LLM / embedding seam: replace `_text_overlap` with a semantic similarity
call and nothing downstream changes, because callers only see the
CriterionResult. This is decision 7's "investigate semantic search".
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import log
from threading import local

import snowballstemmer

from backend.ranking.models import CriterionResult, MatchLevel, Opportunity, SearchRequest

HIGH_THRESHOLD = 0.75
MEDIUM_THRESHOLD = 0.4

# Coverage of the description at which text overlap counts as a full match.
FULL_TEXT_COVERAGE = 0.5

_WORD = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP_WORDS = frozenset(
    """a an and are as at be by for from has have in into is it its of on or that the
    this to was were will with we our study project research grant funding fund
    using use based new under over between within about after before through during
    onto up down out more most other some such than then these those both each how
    what which who also can may could would should do does did not no i my me am
    you your they their them he she his her there here where when all any very just
    well way like etc including include involving involve related relating various
    specific particular general approach method methods area areas field fields work
    working focus focused aim aims develop developing development improve improving
    understand understanding investigate investigating explore exploring fellowship
    scholarship award prize early career postdoctoral postdoc phd doctoral researcher
    programme program scheme opportunity apply application applicant eligible eligibility
    funded support supported available provide offer university institute institution""".split()
)
_STEMMERS = local()


@lru_cache(maxsize=16384)
def _stem(word: str) -> str:
    # Snowball mutates its working buffer, so concurrent requests need separate instances.
    if not hasattr(_STEMMERS, "english"):
        _STEMMERS.english = snowballstemmer.stemmer("english")
    return _STEMMERS.english.stemWord(word)


_STOP_STEMS = frozenset(_stem(w) for w in _STOP_WORDS)


def tokenize(text: str) -> set[str]:
    return {_stem(w) for w in _WORD.findall(text.lower())} - _STOP_STEMS


def _opportunity_tokens(opportunity: Opportunity) -> set[str]:
    return tokenize(" ".join([opportunity.title, opportunity.summary, *opportunity.keywords]))


@dataclass
class TermWeights:
    """Document-frequency weights and token sets for one ranked corpus."""

    _tokens: dict[str, set[str]]
    _weights: dict[str, float]
    _unseen_weight: float

    @classmethod
    def from_opportunities(cls, opportunities: list[Opportunity]) -> TermWeights:
        tokens = {o.id: _opportunity_tokens(o) for o in opportunities}
        frequencies = Counter(term for terms in tokens.values() for term in terms)
        count = len(opportunities)
        return cls(
            tokens,
            {term: log((count + 1) / (df + 1)) + 1 for term, df in frequencies.items()},
            log(count + 1) + 1,
        )

    def weight(self, term: str) -> float:
        return self._weights.get(term, self._unseen_weight)

    def tokens_for(self, opportunity: Opportunity) -> set[str]:
        tokens = self._tokens.get(opportunity.id)
        return tokens if tokens is not None else _opportunity_tokens(opportunity)


def _for_overlap(wanted: list[str], offered: list[str]) -> tuple[float, str]:
    exact = sorted(set(wanted) & set(offered))
    if exact:
        return 1.0, f"Matches your field of research code {', '.join(exact)}."
    divisions = {c[:2] for c in wanted} & {c[:2] for c in offered}
    if divisions:
        return (
            0.5,
            f"Same research division ({', '.join(sorted(divisions))}) but not your exact code.",
        )
    return 0.0, "Different field of research codes."


def _text_overlap(
    description: str, opportunity: Opportunity, weights: TermWeights | None = None
) -> tuple[float, str] | None:
    wanted: dict[str, str] = {}
    for word in _WORD.findall(description):
        stem = _stem(word.lower())
        if stem not in _STOP_STEMS:
            wanted.setdefault(stem, word)
    if not wanted:
        return None
    available = (
        weights.tokens_for(opportunity) if weights is not None else _opportunity_tokens(opportunity)
    )
    term_weights = {term: weights.weight(term) if weights is not None else 1.0 for term in wanted}
    shared = [term for term in wanted if term in available]
    coverage = sum(term_weights[term] for term in shared) / sum(term_weights.values())
    score = min(coverage / FULL_TEXT_COVERAGE, 1.0)
    if shared:
        shared.sort(key=lambda term: -term_weights[term])
        words = ", ".join(wanted[term] for term in shared[:5])
        return (
            score,
            f"Your description shares terms with the opportunity: {words}.",
        )
    return 0.0, "Your description shares no terms with the opportunity."


def _toa_overlap(wanted: list[str], offered: list[str]) -> tuple[float, str]:
    if set(wanted) & set(offered):
        return 1.0, "Type of activity matches."
    return 0.0, "Type of activity differs."


def score_research_match(
    opportunity: Opportunity, request: SearchRequest, weights: TermWeights | None = None
) -> CriterionResult:
    # (weight, score, reason) for each signal we could evaluate.
    signals: list[tuple[float, float, str]] = []

    if request.for_codes and opportunity.for_codes:
        score, reason = _for_overlap(request.for_codes, opportunity.for_codes)
        signals.append((0.5, score, reason))

    text = _text_overlap(request.research_description, opportunity, weights)
    if text is not None:
        signals.append((0.4, *text))

    if request.toa_codes and opportunity.toa_codes:
        score, reason = _toa_overlap(request.toa_codes, opportunity.toa_codes)
        signals.append((0.1, score, reason))

    if not signals:
        return CriterionResult(
            score=0.5,
            label=MatchLevel.MEDIUM,
            reasons=["No research details were supplied to match on."],
        )

    total_weight = sum(w for w, _, _ in signals)
    score = round(sum(w * s for w, s, _ in signals) / total_weight, 4)
    return CriterionResult(score=score, label=_level(score), reasons=[r for _, _, r in signals])


def _level(score: float) -> MatchLevel:
    if score >= HIGH_THRESHOLD:
        return MatchLevel.HIGH
    if score >= MEDIUM_THRESHOLD:
        return MatchLevel.MEDIUM
    return MatchLevel.LOW
