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

from backend.ranking.models import CriterionResult, MatchLevel, Opportunity, SearchRequest

HIGH_THRESHOLD = 0.6
MEDIUM_THRESHOLD = 0.3

# Coverage of the description at which text overlap counts as a full match.
FULL_TEXT_COVERAGE = 0.4

_WORD = re.compile(r"[a-z0-9]+")
_STOP_WORDS = frozenset(
    """a an and are as at be by for from has have in into is it its of on or that the
    this to was were will with we our study project research grant funding fund
    using use based new""".split()
)
_SUFFIXES = ("ling", "ing", "ies", "ers", "er", "ed", "es", "s")


def _stem(word: str) -> str:
    # Crude suffix stripping is enough to let "modelling" meet "models".
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> set[str]:
    return {_stem(w) for w in _WORD.findall(text.lower()) if w not in _STOP_WORDS}


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


def _text_overlap(description: str, opportunity: Opportunity) -> tuple[float, str] | None:
    wanted = tokenize(description)
    if not wanted:
        return None
    available = tokenize(" ".join([opportunity.title, opportunity.summary, *opportunity.keywords]))
    shared = wanted & available
    coverage = len(shared) / len(wanted)
    score = min(coverage / FULL_TEXT_COVERAGE, 1.0)
    if shared:
        return (
            score,
            f"Your description shares terms with the opportunity: {', '.join(sorted(shared)[:5])}.",
        )
    return 0.0, "Your description shares no terms with the opportunity."


def _toa_overlap(wanted: list[str], offered: list[str]) -> tuple[float, str]:
    if set(wanted) & set(offered):
        return 1.0, "Type of activity matches."
    return 0.0, "Type of activity differs."


def score_research_match(opportunity: Opportunity, request: SearchRequest) -> CriterionResult:
    # (weight, score, reason) for each signal we could evaluate.
    signals: list[tuple[float, float, str]] = []

    if request.for_codes and opportunity.for_codes:
        score, reason = _for_overlap(request.for_codes, opportunity.for_codes)
        signals.append((0.5, score, reason))

    text = _text_overlap(request.research_description, opportunity)
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
