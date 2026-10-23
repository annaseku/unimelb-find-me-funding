# Ranking Engine and Search API Implementation Plan

> Historical plan, kept as a record of GenAI use: it was executed with an AI coding agent, and its file paths and steps reflect the repository at the time. Current design: `docs/09-architectural-design/`.

**Goal:** A prototype ranking engine that scores structured funding opportunities against a researcher's search inputs on four criteria, plus the FastAPI endpoint the React frontend calls, with mock data, tests and a golden-set eval.

**Architecture:** One small module per criterion under `backend/ranking/` (eligibility, research match, funding value, deadline), a combiner that applies configurable weights, a JSON-backed repository under `backend/data/`, and a thin FastAPI app under `backend/api/`. Every scorer returns a score, a label and plain-English reasons, so the UI can show why a result ranked where it did. The spec is `docs/superpowers/specs/2026-09-06-ranking-engine-design.md`; read it first.

**Tech Stack:** Python 3.11+ (3.13 locally), Pydantic v2, FastAPI, uvicorn, pytest, httpx (for FastAPI's TestClient). No LLM calls.

## Global Constraints

- Imports are absolute from the repository root, matching the crawler: `from backend.ranking.models import ...`. Run `pytest backend` and `uvicorn backend.api.main:app --reload` from the repository root.
- Do not modify anything under `backend/crawler/`.
- Every module starts with a docstring naming what it does and which Confluence decision it implements. Add a one or two line comment wherever a rule is not obvious from the code. The reader is a teammate who has not read the spec.
- Every test that involves dates uses `TODAY = date(2026, 9, 1)` from `backend/tests/conftest.py`. Never call `date.today()` in `backend/ranking/`.
- Enum string values are exactly: EmployerType university, research_institute, industry, philanthropic. CareerStage undergraduate, graduate_student, postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus. FundingType salary, consumables, equipment, all, any. These match `backend/crawler/queryBuilder.py`.
- Score constants: eligibility eligible 1.0, potentially_eligible 0.7, unknown 0.5, likely_ineligible 0.1. Deadline over_60_days 1.0, days_60_to_30 0.8, days_30_to_15 0.5, under_15_days 0.2, unknown 0.5, closed 0.0. Funding under_1m 0.25, from_1m_to_2m 0.5, from_2m_to_5m 0.75, over_5m 1.0, unknown 0.5. Default weights eligibility 0.4, research_match 0.3, funding_value 0.15, deadline 0.15.
- Commit after every task and push to `origin feat/ranking-engine` straight after each commit. Commit messages end with the two attribution trailers shown in Task 1.
- Prose in any `.md` file is one line per paragraph or list item, never hard-wrapped.

---

## File structure

| Path | Responsibility |
| --- | --- |
| `backend/pyproject.toml` | pytest and ruff config only (`pythonpath = [".."]`, `testpaths = ["tests"]`) |
| `backend/requirements.txt` | runtime deps: existing three plus fastapi, uvicorn, pydantic |
| `backend/requirements-dev.txt` | pytest, httpx |
| `backend/ranking/__init__.py` | package marker, exports `__version__ = "0.1.0"` |
| `backend/ranking/models.py` | enums, `Opportunity`, `SearchRequest`, `CriterionResult`, `RankedOpportunity` |
| `backend/ranking/weights.py` | `Weights`, `DEFAULT_WEIGHTS`, `resolve_weights` |
| `backend/ranking/eligibility.py` | `score_eligibility(opportunity, request) -> CriterionResult` |
| `backend/ranking/research_match.py` | `score_research_match(opportunity, request) -> CriterionResult` |
| `backend/ranking/funding_value.py` | `score_funding_value(opportunity) -> CriterionResult` |
| `backend/ranking/deadline.py` | `score_deadline(opportunity, today) -> CriterionResult` |
| `backend/ranking/ranker.py` | `score_opportunity`, `rank` |
| `backend/data/__init__.py` | package marker |
| `backend/data/mock_opportunities.json` | about 30 illustrative opportunities |
| `backend/data/mock_profiles.json` | eight researcher profiles |
| `backend/data/repository.py` | `OpportunityRepository`, `load_mock_opportunities`, `load_mock_profiles` |
| `backend/api/__init__.py` | package marker |
| `backend/api/schemas.py` | `SearchResponse`, `HealthResponse` |
| `backend/api/main.py` | FastAPI app, CORS, three routes |
| `backend/evals/__init__.py` | package marker |
| `backend/evals/golden.json` | hand-labelled expectations per profile |
| `backend/evals/run_evals.py` | eval runner and report |
| `backend/tests/conftest.py` | `TODAY`, fixtures |
| `backend/tests/test_*.py` | one per module, see tasks |
| `docs/adr/ADR-002-ranking-engine.md` | architecture decision record |
| `docs/api-contract.md` | human summary of the API |
| `docs/ranking-discussion-points.md` | the six open items for the team and client |
| `backend/README` | status table, run instructions |

---

### Task 1: Tooling, models and weights

**Files:**
- Create: `backend/pyproject.toml`, `backend/requirements-dev.txt`, `backend/ranking/__init__.py`, `backend/ranking/models.py`, `backend/ranking/weights.py`, `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/test_models.py`, `backend/tests/test_weights.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: every enum and model in `backend/ranking/models.py` exactly as written below; `Weights`, `DEFAULT_WEIGHTS`, `resolve_weights(override: dict | Weights | None) -> Weights` in `backend/ranking/weights.py`.

- [ ] **Step 1: Tooling files**

`backend/pyproject.toml`:

```toml
# Tool configuration only. Runtime dependencies stay in requirements.txt so
# teammates keep using plain venv + pip, as the crawler README describes.

[tool.pytest.ini_options]
# ".." puts the repository root on sys.path so `backend.ranking...` imports
# resolve the same way they do for the crawler.
pythonpath = [".."]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

`backend/requirements.txt` (append to the existing three lines):

```text
fastapi
uvicorn
pydantic
```

`backend/requirements-dev.txt`:

```text
-r requirements.txt
pytest
httpx
```

Install: `backend/.venv/bin/pip install -r backend/requirements-dev.txt`

`backend/ranking/__init__.py`:

```python
"""Ranking engine for Find Me Funding.

Scores funding opportunities against a researcher's search inputs on the four
criteria in the client brief (eligibility, research match, funding value,
deadline) and combines them with configurable weights. See
docs/superpowers/specs/2026-09-06-ranking-engine-design.md.
"""

__version__ = "0.1.0"
```

`backend/tests/__init__.py` is empty. `backend/tests/conftest.py`:

```python
"""Shared test fixtures.

Every date-sensitive test uses TODAY instead of the real clock so the suite
does not start failing as mock deadlines drift into the past.
"""

from datetime import date

import pytest

TODAY = date(2026, 9, 1)


@pytest.fixture
def today() -> date:
    return TODAY
```

- [ ] **Step 2: Write the failing model tests**

`backend/tests/test_models.py`:

```python
"""The models are the contract between crawler, ranker and frontend, so the
vocabulary is tested explicitly."""

import pytest
from pydantic import ValidationError

from backend.crawler.queryBuilder import CAREER_STAGE_TERMS, FUNDING_TYPE_TERMS
from backend.ranking.models import (
    CareerStage,
    FundingType,
    Opportunity,
    SearchRequest,
)


def test_career_stage_values_match_the_crawler_query_builder():
    assert {s.value for s in CareerStage} == set(CAREER_STAGE_TERMS)


def test_funding_type_values_match_the_crawler_query_builder():
    assert {f.value for f in FundingType} == set(FUNDING_TYPE_TERMS)


def test_empty_search_request_is_valid_and_defaults_to_ten_results():
    request = SearchRequest()
    assert request.limit == 10
    assert request.offset == 0
    assert request.hide_ineligible is False
    assert request.include_closed is False


@pytest.mark.parametrize("limit", [0, 101])
def test_limit_outside_one_to_one_hundred_is_rejected(limit):
    with pytest.raises(ValidationError):
        SearchRequest(limit=limit)


def test_opportunity_lists_default_to_empty_meaning_unrestricted():
    opportunity = Opportunity(
        id="x", title="X", funder="F", url="https://example.org", summary="s"
    )
    assert opportunity.citizenships_allowed == []
    assert opportunity.amount_aud is None
    assert opportunity.deadline is None
    assert opportunity.status == "active"
```

Run: `backend/.venv/bin/pytest backend/tests/test_models.py -v`
Expected: FAIL with ModuleNotFoundError for `backend.ranking.models`.

- [ ] **Step 3: Write the models**

`backend/ranking/models.py`:

```python
"""Shared data model for the ranking engine and the search API.

The enum values deliberately match the keys in backend/crawler/queryBuilder.py
and the frontend drop-downs, so all three sides speak the same vocabulary.
Implements Confluence decision 4 (four eligibility states) and decision 5
(four separate scores reported alongside the overall).
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class EmployerType(StrEnum):
    UNIVERSITY = "university"
    RESEARCH_INSTITUTE = "research_institute"
    INDUSTRY = "industry"
    PHILANTHROPIC = "philanthropic"


class CareerStage(StrEnum):
    UNDERGRADUATE = "undergraduate"
    GRADUATE_STUDENT = "graduate_student"
    POSTDOC_0_2 = "postdoc_0_2"
    POSTDOC_2_5 = "postdoc_2_5"
    POSTDOC_5_10 = "postdoc_5_10"
    POSTDOC_10_PLUS = "postdoc_10_plus"


class FundingType(StrEnum):
    SALARY = "salary"
    CONSUMABLES = "consumables"
    EQUIPMENT = "equipment"
    ALL = "all"    # the researcher wants every kind
    ANY = "any"    # the researcher has no preference


class EligibilityState(StrEnum):
    """Decision 4: four states, never a yes/no."""

    ELIGIBLE = "eligible"
    POTENTIALLY_ELIGIBLE = "potentially_eligible"
    UNKNOWN = "unknown"
    LIKELY_INELIGIBLE = "likely_ineligible"


class MatchLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DeadlineBand(StrEnum):
    """The bands named in the client brief, plus closed and unknown."""

    OVER_60_DAYS = "over_60_days"
    DAYS_60_TO_30 = "days_60_to_30"
    DAYS_30_TO_15 = "days_30_to_15"
    UNDER_15_DAYS = "under_15_days"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class FundingBand(StrEnum):
    UNDER_1M = "under_1m"
    FROM_1M_TO_2M = "from_1m_to_2m"
    FROM_2M_TO_5M = "from_2m_to_5m"
    OVER_5M = "over_5m"
    UNKNOWN = "unknown"


class OpportunityStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"   # soft-deleted, decision 9


class Opportunity(BaseModel):
    """One funding opportunity, already deduplicated across its sources.

    An empty list for any *_allowed or *_offered field means the funder
    states no restriction (or we could not find one), not "nobody".
    """

    id: str
    title: str
    funder: str
    url: str
    source_urls: list[str] = Field(default_factory=list)
    summary: str
    amount_aud: int | None = Field(default=None, description="Maximum available, AUD.")
    amount_note: str = ""
    deadline: date | None = None
    opens_at: date | None = None
    countries: list[str] = Field(
        default_factory=list,
        description="Where the applicant's institution must be based. Informational for now.",
    )
    citizenships_allowed: list[str] = Field(default_factory=list)
    employer_types_allowed: list[EmployerType] = Field(default_factory=list)
    career_stages_allowed: list[CareerStage] = Field(default_factory=list)
    funding_types_offered: list[FundingType] = Field(default_factory=list)
    for_codes: list[str] = Field(default_factory=list, description="ANZSRC 2020 FoR codes.")
    toa_codes: list[str] = Field(default_factory=list, description="ANZSRC type of activity, '1' to '4'.")
    keywords: list[str] = Field(default_factory=list)
    eligibility_text: str = Field(default="", description="Funder prose, kept for a future LLM check.")
    status: OpportunityStatus = OpportunityStatus.ACTIVE


class SearchRequest(BaseModel):
    """The drop-downs and free text from the frontend. Everything is optional."""

    for_codes: list[str] = Field(default_factory=list)
    toa_codes: list[str] = Field(default_factory=list)
    citizenships: list[str] = Field(default_factory=list, description="ISO 3166-1 alpha-2.")
    employer_type: EmployerType | None = None
    career_stage: CareerStage | None = None
    funding_types: list[FundingType] = Field(default_factory=list)
    research_description: str = ""
    hide_ineligible: bool = False
    include_closed: bool = False
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    weights: dict[str, float] | None = Field(
        default=None, description="Partial override of the default weights."
    )


class CriterionResult(BaseModel):
    """One of the four ratings shown next to a result."""

    score: float = Field(ge=0.0, le=1.0)
    label: str
    reasons: list[str] = Field(default_factory=list)


class RankedOpportunity(BaseModel):
    """Decision 5: the four scores stay separate next to the overall."""

    opportunity: Opportunity
    overall: float = Field(ge=0.0, le=1.0)
    eligibility: CriterionResult
    research_match: CriterionResult
    funding_value: CriterionResult
    deadline: CriterionResult
```

Run: `backend/.venv/bin/pytest backend/tests/test_models.py -v`
Expected: PASS.

- [ ] **Step 4: Write the failing weight tests**

`backend/tests/test_weights.py`:

```python
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
```

Run: `backend/.venv/bin/pytest backend/tests/test_weights.py -v`
Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 5: Write weights.py**

```python
"""Configurable weights for combining the four scores (decision 5).

The defaults are placeholders that put eligibility first because the client
called it the top priority. The relative weighting is still an open team
decision; see docs/ranking-discussion-points.md.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Weights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eligibility: float = Field(ge=0.0)
    research_match: float = Field(ge=0.0)
    funding_value: float = Field(ge=0.0)
    deadline: float = Field(ge=0.0)

    @model_validator(mode="after")
    def _at_least_one_non_zero(self) -> Weights:
        # An all-zero set would divide by zero when normalising.
        if self.total() == 0:
            raise ValueError("at least one weight must be greater than zero")
        return self

    def total(self) -> float:
        return self.eligibility + self.research_match + self.funding_value + self.deadline

    def as_dict(self) -> dict[str, float]:
        return self.model_dump()


DEFAULT_WEIGHTS = Weights(
    eligibility=0.4,
    research_match=0.3,
    funding_value=0.15,
    deadline=0.15,
)


def resolve_weights(override: dict[str, float] | Weights | None) -> Weights:
    """Merge a partial override from the request onto the defaults."""
    if override is None:
        return DEFAULT_WEIGHTS
    if isinstance(override, Weights):
        return override
    return Weights(**{**DEFAULT_WEIGHTS.as_dict(), **override})
```

Run: `backend/.venv/bin/pytest backend/tests -v`
Expected: all PASS.

- [ ] **Step 6: Commit and push**

```bash
git add backend/pyproject.toml backend/requirements.txt backend/requirements-dev.txt backend/ranking backend/tests
git commit -m "feat(ranking): data model, enums and configurable weights

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GcwEUZg1iAJP772ndk3CSx"
git push origin feat/ranking-engine
```

---

### Task 2: Eligibility classifier

**Files:**
- Create: `backend/ranking/eligibility.py`, `backend/tests/test_eligibility.py`

**Interfaces:**
- Consumes: `Opportunity`, `SearchRequest`, `CriterionResult`, `EligibilityState`, `FundingType` from Task 1.
- Produces: `score_eligibility(opportunity: Opportunity, request: SearchRequest) -> CriterionResult` whose `label` is an `EligibilityState` value; constant `ELIGIBILITY_SCORES: dict[EligibilityState, float]`.

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_eligibility.py`:

```python
"""Eligibility is the client's top priority and has four states (decision 4).
Each test names the rule it proves."""

import pytest

from backend.ranking.eligibility import ELIGIBILITY_SCORES, score_eligibility
from backend.ranking.models import (
    CareerStage,
    EligibilityState,
    EmployerType,
    FundingType,
    Opportunity,
    SearchRequest,
)


def make_opportunity(**overrides) -> Opportunity:
    base = dict(id="o1", title="T", funder="F", url="https://example.org", summary="s")
    return Opportunity(**{**base, **overrides})


def test_no_restrictions_stated_is_potentially_eligible():
    result = score_eligibility(make_opportunity(), SearchRequest())
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE
    assert result.score == ELIGIBILITY_SCORES[EligibilityState.POTENTIALLY_ELIGIBLE]
    assert any("no restrictions" in r.lower() for r in result.reasons)


def test_restriction_stated_but_nothing_supplied_is_unknown():
    opportunity = make_opportunity(citizenships_allowed=["AU"])
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.UNKNOWN


def test_citizenship_mismatch_is_likely_ineligible_and_still_scored():
    opportunity = make_opportunity(citizenships_allowed=["AU", "NZ"])
    result = score_eligibility(opportunity, SearchRequest(citizenships=["GB"]))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE
    assert result.score > 0, "decision 4: de-ranked, never dropped by the scorer"
    assert any("AU" in r and "GB" in r for r in result.reasons)


def test_one_of_several_citizenships_matching_passes():
    opportunity = make_opportunity(citizenships_allowed=["AU"])
    result = score_eligibility(opportunity, SearchRequest(citizenships=["GB", "AU"]))
    assert result.label == EligibilityState.ELIGIBLE


def test_all_stated_restrictions_passing_is_eligible_with_score_one():
    opportunity = make_opportunity(
        citizenships_allowed=["AU"],
        employer_types_allowed=[EmployerType.UNIVERSITY],
        career_stages_allowed=[CareerStage.POSTDOC_2_5],
        funding_types_offered=[FundingType.SALARY],
    )
    request = SearchRequest(
        citizenships=["AU"],
        employer_type=EmployerType.UNIVERSITY,
        career_stage=CareerStage.POSTDOC_2_5,
        funding_types=[FundingType.SALARY],
    )
    result = score_eligibility(opportunity, request)
    assert result.label == EligibilityState.ELIGIBLE
    assert result.score == 1.0
    assert len(result.reasons) == 4


def test_mixed_pass_and_unknown_is_potentially_eligible():
    opportunity = make_opportunity(
        citizenships_allowed=["AU"], career_stages_allowed=[CareerStage.UNDERGRADUATE]
    )
    result = score_eligibility(opportunity, SearchRequest(citizenships=["AU"]))
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE


def test_employer_type_mismatch_fails():
    opportunity = make_opportunity(employer_types_allowed=[EmployerType.INDUSTRY])
    result = score_eligibility(opportunity, SearchRequest(employer_type=EmployerType.UNIVERSITY))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE


def test_career_stage_mismatch_fails():
    opportunity = make_opportunity(career_stages_allowed=[CareerStage.POSTDOC_0_2])
    result = score_eligibility(opportunity, SearchRequest(career_stage=CareerStage.GRADUATE_STUDENT))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE


@pytest.mark.parametrize("wanted", [FundingType.ALL, FundingType.ANY])
def test_all_or_any_funding_type_never_contradicts(wanted):
    opportunity = make_opportunity(funding_types_offered=[FundingType.EQUIPMENT])
    result = score_eligibility(opportunity, SearchRequest(funding_types=[wanted]))
    assert result.label == EligibilityState.ELIGIBLE


def test_funding_type_not_offered_fails():
    opportunity = make_opportunity(funding_types_offered=[FundingType.EQUIPMENT])
    result = score_eligibility(opportunity, SearchRequest(funding_types=[FundingType.SALARY]))
    assert result.label == EligibilityState.LIKELY_INELIGIBLE


def test_funding_type_is_skipped_when_the_researcher_lists_none():
    # No requested funding type means no need was expressed, so it is neither
    # a pass nor an unknown; the opportunity has nothing else stated.
    opportunity = make_opportunity(funding_types_offered=[FundingType.EQUIPMENT])
    result = score_eligibility(opportunity, SearchRequest())
    assert result.label == EligibilityState.POTENTIALLY_ELIGIBLE


def test_every_result_has_at_least_one_reason():
    for request in (SearchRequest(), SearchRequest(citizenships=["AU"])):
        assert score_eligibility(make_opportunity(citizenships_allowed=["AU"]), request).reasons
```

Run: `backend/.venv/bin/pytest backend/tests/test_eligibility.py -v` Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 2: Write eligibility.py**

```python
"""Deterministic eligibility classification (decisions 3 and 4).

Every restriction the funder states is checked against the researcher's
inputs and yields pass, fail or unknown. The four-state outcome means an
opportunity with one unverifiable requirement is still shown, as the client
asked. Nothing here calls an LLM; the funder's eligibility prose is kept on
the opportunity for a future LLM pass on the ambiguous cases.
"""

from __future__ import annotations

from enum import Enum

from backend.ranking.models import (
    CriterionResult,
    EligibilityState,
    FundingType,
    Opportunity,
    SearchRequest,
)

ELIGIBILITY_SCORES: dict[EligibilityState, float] = {
    EligibilityState.ELIGIBLE: 1.0,
    EligibilityState.POTENTIALLY_ELIGIBLE: 0.7,
    EligibilityState.UNKNOWN: 0.5,
    EligibilityState.LIKELY_INELIGIBLE: 0.1,
}


class Check(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"   # the funder restricts this, the researcher said nothing


def _join(values) -> str:
    return ", ".join(str(v) for v in values)


def _check_membership(label: str, allowed: list, supplied: list) -> tuple[Check, str]:
    """Shared rule for citizenship, employer type and career stage.

    `allowed` is non-empty (the caller only calls this when the funder
    restricts the field). `supplied` is whatever the researcher selected.
    """
    if not supplied:
        return Check.UNKNOWN, f"{label} is restricted to {_join(allowed)}; you did not say."
    matches = [s for s in supplied if s in allowed]
    if matches:
        return Check.PASS, f"{label} accepted: open to {_join(allowed)}; you selected {_join(matches)}."
    return Check.FAIL, f"{label} restricted to {_join(allowed)}; you selected {_join(supplied)}."


def _check_funding_type(offered: list[FundingType], wanted: list[FundingType]) -> tuple[Check, str]:
    # "all" and "any" mean the researcher will take whatever is offered.
    if FundingType.ALL in wanted or FundingType.ANY in wanted:
        return Check.PASS, f"Funding type: offers {_join(offered)}, which suits any preference."
    overlap = [w for w in wanted if w in offered]
    if overlap:
        return Check.PASS, f"Funding type: offers {_join(overlap)}, which you asked for."
    return Check.FAIL, f"Funding type: offers {_join(offered)} but you asked for {_join(wanted)}."


def score_eligibility(opportunity: Opportunity, request: SearchRequest) -> CriterionResult:
    checks: list[Check] = []
    reasons: list[str] = []

    if opportunity.citizenships_allowed:
        outcome, reason = _check_membership(
            "Citizenship", opportunity.citizenships_allowed, request.citizenships
        )
        checks.append(outcome)
        reasons.append(reason)

    if opportunity.employer_types_allowed:
        supplied = [request.employer_type] if request.employer_type else []
        outcome, reason = _check_membership(
            "Employer type", opportunity.employer_types_allowed, supplied
        )
        checks.append(outcome)
        reasons.append(reason)

    if opportunity.career_stages_allowed:
        supplied = [request.career_stage] if request.career_stage else []
        outcome, reason = _check_membership(
            "Career stage", opportunity.career_stages_allowed, supplied
        )
        checks.append(outcome)
        reasons.append(reason)

    # Funding type is only a restriction if the researcher expressed a need.
    if opportunity.funding_types_offered and request.funding_types:
        outcome, reason = _check_funding_type(
            opportunity.funding_types_offered, request.funding_types
        )
        checks.append(outcome)
        reasons.append(reason)

    state = _state_from_checks(checks)
    if not reasons:
        reasons.append("The funder states no restrictions we can check.")
    elif state == EligibilityState.UNKNOWN:
        reasons.append("Restrictions exist but your inputs did not cover them.")
    return CriterionResult(score=ELIGIBILITY_SCORES[state], label=state, reasons=reasons)


def _state_from_checks(checks: list[Check]) -> EligibilityState:
    # Order matters: one hard contradiction outranks any number of passes.
    if Check.FAIL in checks:
        return EligibilityState.LIKELY_INELIGIBLE
    passes = checks.count(Check.PASS)
    unknowns = checks.count(Check.UNKNOWN)
    if passes == 0 and unknowns == 0:
        return EligibilityState.POTENTIALLY_ELIGIBLE   # nothing checkable was stated
    if passes == 0:
        return EligibilityState.UNKNOWN
    if unknowns == 0:
        return EligibilityState.ELIGIBLE
    return EligibilityState.POTENTIALLY_ELIGIBLE
```

Run: `backend/.venv/bin/pytest backend/tests/test_eligibility.py -v` Expected: PASS.

- [ ] **Step 3: Commit and push** (message `feat(ranking): four-state deterministic eligibility classifier`, files `backend/ranking/eligibility.py backend/tests/test_eligibility.py`, then push to origin feat/ranking-engine, trailers as in Task 1).

---

### Task 3: Research match

**Files:**
- Create: `backend/ranking/research_match.py`, `backend/tests/test_research_match.py`

**Interfaces:**
- Consumes: `Opportunity`, `SearchRequest`, `CriterionResult`, `MatchLevel` from Task 1.
- Produces: `score_research_match(opportunity, request) -> CriterionResult` with a `MatchLevel` label; `tokenize(text: str) -> set[str]`.

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_research_match.py`:

```python
"""Research match is deterministic keyword and code overlap for now. The
docstring in the module names where an embedding or LLM scorer slots in."""

from backend.ranking.models import MatchLevel, Opportunity, SearchRequest
from backend.ranking.research_match import score_research_match, tokenize


def make_opportunity(**overrides) -> Opportunity:
    base = dict(
        id="o1",
        title="Coral reef resilience grant",
        funder="F",
        url="https://example.org",
        summary="Supports research into coral reef ecosystems and ocean acidification.",
        keywords=["marine", "coral"],
        for_codes=["3103"],
        toa_codes=["3"],
    )
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
```

Run: `backend/.venv/bin/pytest backend/tests/test_research_match.py -v` Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 2: Write research_match.py**

```python
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
        return 0.5, f"Same research division ({', '.join(sorted(divisions))}) but not your exact code."
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
        return score, f"Your description shares terms with the opportunity: {', '.join(sorted(shared)[:5])}."
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
```

Run: `backend/.venv/bin/pytest backend/tests/test_research_match.py -v` Expected: PASS. If `test_text_overlap_alone_can_reach_high` fails, check the stemming: adjust `_SUFFIXES` order or the minimum stem length rather than the test.

- [ ] **Step 3: Commit and push** (message `feat(ranking): research match from FoR, ToA and keyword overlap`, files `backend/ranking/research_match.py backend/tests/test_research_match.py`, push, trailers as in Task 1).

---

### Task 4: Funding value and deadline

**Files:**
- Create: `backend/ranking/funding_value.py`, `backend/ranking/deadline.py`, `backend/tests/test_funding_value.py`, `backend/tests/test_deadline.py`

**Interfaces:**
- Consumes: `Opportunity`, `CriterionResult`, `FundingBand`, `DeadlineBand` from Task 1; `TODAY` from conftest.
- Produces: `score_funding_value(opportunity) -> CriterionResult` (label a `FundingBand`); `score_deadline(opportunity, today: date) -> CriterionResult` (label a `DeadlineBand`); `days_remaining(opportunity, today) -> int | None`.

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_funding_value.py`:

```python
"""Funding bands follow the backend README proposal; edges are tested exactly."""

import pytest

from backend.ranking.funding_value import score_funding_value
from backend.ranking.models import FundingBand, Opportunity


def make_opportunity(amount) -> Opportunity:
    return Opportunity(
        id="o1", title="T", funder="F", url="https://example.org", summary="s", amount_aud=amount
    )


@pytest.mark.parametrize(
    ("amount", "band", "score"),
    [
        (1, FundingBand.UNDER_1M, 0.25),
        (999_999, FundingBand.UNDER_1M, 0.25),
        (1_000_000, FundingBand.FROM_1M_TO_2M, 0.5),
        (1_999_999, FundingBand.FROM_1M_TO_2M, 0.5),
        (2_000_000, FundingBand.FROM_2M_TO_5M, 0.75),
        (4_999_999, FundingBand.FROM_2M_TO_5M, 0.75),
        (5_000_000, FundingBand.OVER_5M, 1.0),
        (None, FundingBand.UNKNOWN, 0.5),
    ],
)
def test_band_edges(amount, band, score):
    result = score_funding_value(make_opportunity(amount))
    assert result.label == band
    assert result.score == score


def test_reason_states_the_amount():
    assert "$1,500,000" in score_funding_value(make_opportunity(1_500_000)).reasons[0]


def test_reason_for_unknown_amount():
    assert "not stated" in score_funding_value(make_opportunity(None)).reasons[0].lower()
```

`backend/tests/test_deadline.py`:

```python
"""More lead time scores higher (team decision, flagged for the client)."""

from datetime import timedelta

import pytest

from backend.ranking.deadline import days_remaining, score_deadline
from backend.ranking.models import DeadlineBand, Opportunity
from backend.tests.conftest import TODAY


def make_opportunity(days=None, opens_in=None) -> Opportunity:
    return Opportunity(
        id="o1",
        title="T",
        funder="F",
        url="https://example.org",
        summary="s",
        deadline=None if days is None else TODAY + timedelta(days=days),
        opens_at=None if opens_in is None else TODAY + timedelta(days=opens_in),
    )


@pytest.mark.parametrize(
    ("days", "band", "score"),
    [
        (200, DeadlineBand.OVER_60_DAYS, 1.0),
        (61, DeadlineBand.OVER_60_DAYS, 1.0),
        (60, DeadlineBand.DAYS_60_TO_30, 0.8),
        (30, DeadlineBand.DAYS_60_TO_30, 0.8),
        (29, DeadlineBand.DAYS_30_TO_15, 0.5),
        (15, DeadlineBand.DAYS_30_TO_15, 0.5),
        (14, DeadlineBand.UNDER_15_DAYS, 0.2),
        (0, DeadlineBand.UNDER_15_DAYS, 0.2),
        (-1, DeadlineBand.CLOSED, 0.0),
        (None, DeadlineBand.UNKNOWN, 0.5),
    ],
)
def test_band_edges(days, band, score):
    result = score_deadline(make_opportunity(days), TODAY)
    assert result.label == band
    assert result.score == score


def test_days_remaining_is_none_without_a_deadline():
    assert days_remaining(make_opportunity(None), TODAY) is None


def test_future_opening_date_is_mentioned():
    result = score_deadline(make_opportunity(days=120, opens_in=30), TODAY)
    assert any("opens on" in r.lower() for r in result.reasons)


def test_reason_mentions_days_remaining():
    assert "45 days" in score_deadline(make_opportunity(45), TODAY).reasons[0]
```

Run: `backend/.venv/bin/pytest backend/tests/test_funding_value.py backend/tests/test_deadline.py -v` Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 2: Write funding_value.py**

```python
"""Funding value banding (client criterion 3).

Bands are the ones proposed in backend/crawler/README. Most single-project
grants fall in the bottom band, which the team has flagged for the client;
change the edges in BANDS if that decision changes.
"""

from __future__ import annotations

from backend.ranking.models import CriterionResult, FundingBand, Opportunity

# (lower edge inclusive, band, score), checked from the top down.
BANDS: list[tuple[int, FundingBand, float]] = [
    (5_000_000, FundingBand.OVER_5M, 1.0),
    (2_000_000, FundingBand.FROM_2M_TO_5M, 0.75),
    (1_000_000, FundingBand.FROM_1M_TO_2M, 0.5),
    (0, FundingBand.UNDER_1M, 0.25),
]
UNKNOWN_SCORE = 0.5

_LABELS = {
    FundingBand.OVER_5M: "$5M or more",
    FundingBand.FROM_2M_TO_5M: "$2M to $5M",
    FundingBand.FROM_1M_TO_2M: "$1M to $2M",
    FundingBand.UNDER_1M: "under $1M",
}


def score_funding_value(opportunity: Opportunity) -> CriterionResult:
    amount = opportunity.amount_aud
    if amount is None:
        # Decision 4 applies to amounts too: unknown sits mid-range, not at zero.
        return CriterionResult(
            score=UNKNOWN_SCORE, label=FundingBand.UNKNOWN, reasons=["Funding amount not stated."]
        )
    for lower_edge, band, score in BANDS:
        if amount >= lower_edge:
            note = f" ({opportunity.amount_note})" if opportunity.amount_note else ""
            return CriterionResult(
                score=score,
                label=band,
                reasons=[f"Up to ${amount:,} AUD{note}, in the {_LABELS[band]} band."],
            )
    raise ValueError(f"negative funding amount on {opportunity.id}")
```

- [ ] **Step 3: Write deadline.py**

```python
"""Time-to-deadline banding (client criterion 4).

Bands are from the brief. More lead time scores higher because the client
said a deadline six months out is far more useful than one due next week;
the architecture page's phrase "deadline urgency" reads the other way, so
this is on the discussion list. `today` is always passed in so the ranker
never reads the clock and tests stay deterministic.
"""

from __future__ import annotations

from datetime import date

from backend.ranking.models import CriterionResult, DeadlineBand, Opportunity

# (lowest days remaining inclusive, band, score), checked from the top down.
BANDS: list[tuple[int, DeadlineBand, float]] = [
    (61, DeadlineBand.OVER_60_DAYS, 1.0),
    (30, DeadlineBand.DAYS_60_TO_30, 0.8),
    (15, DeadlineBand.DAYS_30_TO_15, 0.5),
    (0, DeadlineBand.UNDER_15_DAYS, 0.2),
]
CLOSED_SCORE = 0.0
UNKNOWN_SCORE = 0.5


def days_remaining(opportunity: Opportunity, today: date) -> int | None:
    if opportunity.deadline is None:
        return None
    return (opportunity.deadline - today).days


def score_deadline(opportunity: Opportunity, today: date) -> CriterionResult:
    days = days_remaining(opportunity, today)
    reasons: list[str] = []
    if opportunity.opens_at and opportunity.opens_at > today:
        reasons.append(f"Opens on {opportunity.opens_at.isoformat()}.")

    if days is None:
        reasons.insert(0, "No deadline stated.")
        return CriterionResult(score=UNKNOWN_SCORE, label=DeadlineBand.UNKNOWN, reasons=reasons)
    if days < 0:
        reasons.insert(0, f"Closed on {opportunity.deadline.isoformat()}.")
        return CriterionResult(score=CLOSED_SCORE, label=DeadlineBand.CLOSED, reasons=reasons)
    for lowest_days, band, score in BANDS:
        if days >= lowest_days:
            reasons.insert(0, f"Closes in {days} days ({opportunity.deadline.isoformat()}).")
            return CriterionResult(score=score, label=band, reasons=reasons)
    raise AssertionError("unreachable: every non-negative day count lands in a band")
```

Run: `backend/.venv/bin/pytest backend/tests -v` Expected: all PASS.

- [ ] **Step 4: Commit and push** (message `feat(ranking): funding value and deadline banding`, the four files above, push, trailers as in Task 1).

---

### Task 5: Ranker (combine, filter, sort)

**Files:**
- Create: `backend/ranking/ranker.py`, `backend/tests/test_ranker.py`

**Interfaces:**
- Consumes: the four scorers from Tasks 2 to 4; `Weights`, `resolve_weights` from Task 1; `EligibilityState`, `DeadlineBand`, `OpportunityStatus`, `RankedOpportunity` from Task 1.
- Produces: `score_opportunity(opportunity, request, weights: Weights, today: date) -> RankedOpportunity`; `rank(opportunities: list[Opportunity], request: SearchRequest, weights: Weights, today: date) -> list[RankedOpportunity]` (full ordered list, no paging).

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_ranker.py`:

```python
"""The combiner is decision 5: four separate scores, configurable weights,
never one opaque number. Closed results are soft-deleted (decision 9)."""

from datetime import timedelta

import pytest

from backend.ranking.models import (
    DeadlineBand,
    EligibilityState,
    Opportunity,
    OpportunityStatus,
    SearchRequest,
)
from backend.ranking.ranker import rank, score_opportunity
from backend.ranking.weights import DEFAULT_WEIGHTS, Weights
from backend.tests.conftest import TODAY


def make_opportunity(**overrides) -> Opportunity:
    base = dict(
        id="o1",
        title="Machine learning grant",
        funder="F",
        url="https://example.org",
        summary="Funds machine learning research.",
        amount_aud=100_000,
        deadline=TODAY + timedelta(days=90),
        for_codes=["4611"],
    )
    return Opportunity(**{**base, **overrides})


def test_every_result_carries_four_criteria_with_reasons():
    ranked = score_opportunity(make_opportunity(), SearchRequest(), DEFAULT_WEIGHTS, TODAY)
    for criterion in (ranked.eligibility, ranked.research_match, ranked.funding_value, ranked.deadline):
        assert criterion.reasons
        assert 0.0 <= criterion.score <= 1.0
    assert 0.0 <= ranked.overall <= 1.0


def test_weighting_everything_on_one_criterion_reproduces_that_score():
    weights = Weights(eligibility=0, research_match=0, funding_value=1, deadline=0)
    ranked = score_opportunity(make_opportunity(), SearchRequest(), weights, TODAY)
    assert ranked.overall == pytest.approx(ranked.funding_value.score)


def test_overall_is_the_weighted_average():
    ranked = score_opportunity(make_opportunity(), SearchRequest(for_codes=["4611"]), DEFAULT_WEIGHTS, TODAY)
    expected = (
        0.4 * ranked.eligibility.score
        + 0.3 * ranked.research_match.score
        + 0.15 * ranked.funding_value.score
        + 0.15 * ranked.deadline.score
    )
    assert ranked.overall == pytest.approx(expected, abs=1e-4)


def test_past_deadline_is_hidden_by_default_and_retrievable():
    opportunities = [
        make_opportunity(id="open"),
        make_opportunity(id="past", deadline=TODAY - timedelta(days=1)),
    ]
    assert [r.opportunity.id for r in rank(opportunities, SearchRequest(), DEFAULT_WEIGHTS, TODAY)] == ["open"]
    shown = rank(opportunities, SearchRequest(include_closed=True), DEFAULT_WEIGHTS, TODAY)
    assert {r.opportunity.id for r in shown} == {"open", "past"}
    past = next(r for r in shown if r.opportunity.id == "past")
    assert past.deadline.label == DeadlineBand.CLOSED


def test_closed_status_is_hidden_even_with_a_future_deadline():
    opportunities = [make_opportunity(id="archived", status=OpportunityStatus.CLOSED)]
    assert rank(opportunities, SearchRequest(), DEFAULT_WEIGHTS, TODAY) == []


def test_hide_ineligible_drops_only_likely_ineligible():
    opportunities = [
        make_opportunity(id="fits", citizenships_allowed=["AU"]),
        make_opportunity(id="unknown"),
        make_opportunity(id="wrong", citizenships_allowed=["US"]),
    ]
    request = SearchRequest(citizenships=["AU"], hide_ineligible=True)
    ids = [r.opportunity.id for r in rank(opportunities, request, DEFAULT_WEIGHTS, TODAY)]
    assert "wrong" not in ids
    assert {"fits", "unknown"} <= set(ids)


def test_ineligible_is_shown_and_ranked_last_by_default():
    opportunities = [
        make_opportunity(id="wrong", citizenships_allowed=["US"]),
        make_opportunity(id="fits", citizenships_allowed=["AU"]),
    ]
    results = rank(opportunities, SearchRequest(citizenships=["AU"]), DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in results] == ["fits", "wrong"]
    assert results[-1].eligibility.label == EligibilityState.LIKELY_INELIGIBLE


def test_ties_break_on_eligibility_then_id():
    # Same overall by construction: identical except eligibility state and id.
    weights = Weights(eligibility=0, research_match=1, funding_value=0, deadline=0)
    opportunities = [
        make_opportunity(id="b"),
        make_opportunity(id="a"),
        make_opportunity(id="c", citizenships_allowed=["AU"]),
    ]
    results = rank(opportunities, SearchRequest(citizenships=["AU"]), weights, TODAY)
    assert [r.opportunity.id for r in results] == ["c", "a", "b"]


def test_best_first():
    opportunities = [
        make_opportunity(id="weak", for_codes=["9999"], amount_aud=1_000),
        make_opportunity(id="strong", amount_aud=6_000_000),
    ]
    results = rank(opportunities, SearchRequest(for_codes=["4611"]), DEFAULT_WEIGHTS, TODAY)
    assert [r.opportunity.id for r in results] == ["strong", "weak"]
```

Run: `backend/.venv/bin/pytest backend/tests/test_ranker.py -v` Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 2: Write ranker.py**

```python
"""Combine the four criterion scores into an ordered result list.

Decision 5: the four scores are computed separately, combined with
configurable weights, and all four travel with the result so the UI can
show why something ranked where it did. Decision 9: closed opportunities are
soft-deleted, so they are filtered here at read time rather than removed
from the data. Paging is the API's job; this module returns the full list.
"""

from __future__ import annotations

from datetime import date

from backend.ranking.deadline import score_deadline
from backend.ranking.eligibility import score_eligibility
from backend.ranking.funding_value import score_funding_value
from backend.ranking.models import (
    DeadlineBand,
    EligibilityState,
    Opportunity,
    OpportunityStatus,
    RankedOpportunity,
    SearchRequest,
)
from backend.ranking.research_match import score_research_match
from backend.ranking.weights import Weights


def score_opportunity(
    opportunity: Opportunity, request: SearchRequest, weights: Weights, today: date
) -> RankedOpportunity:
    eligibility = score_eligibility(opportunity, request)
    research_match = score_research_match(opportunity, request)
    funding_value = score_funding_value(opportunity)
    deadline = score_deadline(opportunity, today)

    weighted = (
        weights.eligibility * eligibility.score
        + weights.research_match * research_match.score
        + weights.funding_value * funding_value.score
        + weights.deadline * deadline.score
    )
    overall = round(weighted / weights.total(), 4)

    return RankedOpportunity(
        opportunity=opportunity,
        overall=overall,
        eligibility=eligibility,
        research_match=research_match,
        funding_value=funding_value,
        deadline=deadline,
    )


def rank(
    opportunities: list[Opportunity], request: SearchRequest, weights: Weights, today: date
) -> list[RankedOpportunity]:
    ranked = [
        score_opportunity(o, request, weights, today)
        for o in opportunities
        if request.include_closed or _is_open(o, today)
    ]

    if request.hide_ineligible:
        # Discussion point 2: shown and de-ranked by default, hidden on request.
        ranked = [r for r in ranked if r.eligibility.label != EligibilityState.LIKELY_INELIGIBLE]

    # Highest overall first; equal overalls prefer the more eligible one; then
    # a stable id order so two runs always agree.
    ranked.sort(key=lambda r: (-r.overall, -r.eligibility.score, r.opportunity.id))
    return ranked


def _is_open(opportunity: Opportunity, today: date) -> bool:
    if opportunity.status == OpportunityStatus.CLOSED:
        return False
    return score_deadline(opportunity, today).label != DeadlineBand.CLOSED
```

Run: `backend/.venv/bin/pytest backend/tests -v` Expected: all PASS.

- [ ] **Step 3: Commit and push** (message `feat(ranking): weighted combiner with closed and ineligible filtering`, files `backend/ranking/ranker.py backend/tests/test_ranker.py`, push, trailers as in Task 1).

---

### Task 6: Mock data and repository

**Files:**
- Create: `backend/data/__init__.py`, `backend/data/mock_opportunities.json`, `backend/data/mock_profiles.json`, `backend/data/repository.py`, `backend/tests/test_repository.py`

**Interfaces:**
- Consumes: `Opportunity`, `SearchRequest` from Task 1.
- Produces: `class OpportunityRepository` with `all() -> list[Opportunity]` and `get(id: str) -> Opportunity | None`; `load_mock_opportunities() -> list[Opportunity]`; `load_mock_profiles() -> list[MockProfile]` where `MockProfile` has `id: str`, `label: str`, `request: SearchRequest`; `get_repository() -> OpportunityRepository` (module-level singleton loaded once).

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_repository.py`:

```python
"""The repository is the only seam between the API and the data, so the mock
file is validated here rather than at request time."""

from datetime import date

from backend.data.repository import (
    OpportunityRepository,
    load_mock_opportunities,
    load_mock_profiles,
)
from backend.ranking.models import (
    CareerStage,
    DeadlineBand,
    EmployerType,
    FundingBand,
    Opportunity,
    OpportunityStatus,
)
from backend.ranking.deadline import score_deadline
from backend.ranking.funding_value import score_funding_value
from backend.tests.conftest import TODAY


def test_every_mock_record_validates_and_ids_are_unique():
    opportunities = load_mock_opportunities()
    assert len(opportunities) >= 30
    assert all(isinstance(o, Opportunity) for o in opportunities)
    assert len({o.id for o in opportunities}) == len(opportunities)


def test_mock_data_covers_every_funding_band():
    bands = {score_funding_value(o).label for o in load_mock_opportunities()}
    assert bands == set(FundingBand)


def test_mock_data_covers_every_deadline_band_relative_to_today():
    bands = {score_deadline(o, TODAY).label for o in load_mock_opportunities()}
    assert bands == set(DeadlineBand)


def test_mock_data_has_closed_status_past_deadline_and_future_opening():
    opportunities = load_mock_opportunities()
    assert sum(o.status == OpportunityStatus.CLOSED for o in opportunities) >= 2
    assert any(o.status == OpportunityStatus.ACTIVE and o.deadline and o.deadline < TODAY for o in opportunities)
    assert sum(1 for o in opportunities if o.opens_at and o.opens_at > TODAY) >= 2
    assert sum(1 for o in opportunities if o.amount_aud is None) >= 3
    assert sum(1 for o in opportunities if o.deadline is None) >= 2


def test_mock_data_covers_every_career_stage_and_employer_type():
    opportunities = load_mock_opportunities()
    stages = {s for o in opportunities for s in o.career_stages_allowed}
    employers = {e for o in opportunities for e in o.employer_types_allowed}
    assert stages == set(CareerStage)
    assert employers == set(EmployerType)


def test_profiles_load_as_search_requests():
    profiles = load_mock_profiles()
    assert len(profiles) == 8
    assert len({p.id for p in profiles}) == 8
    assert any(p.request.model_dump(exclude_defaults=True) == {} for p in profiles), "one empty profile"


def test_repository_get_and_missing():
    repo = OpportunityRepository(load_mock_opportunities())
    first = repo.all()[0]
    assert repo.get(first.id) == first
    assert repo.get("does-not-exist") is None
```

Run: `backend/.venv/bin/pytest backend/tests/test_repository.py -v` Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 2: Write repository.py**

```python
"""Loads the mock opportunity set and exposes it behind a small repository.

This is the seam decision 7 describes between the structured funding store
and the search layer: the API only ever calls `all()` and `get()`, so a
crawler-backed repository replaces this one class and nothing else changes.

The mock values are illustrative. Scheme names are real so the demo reads
naturally, but amounts, dates and rules were not verified with the funders.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from backend.ranking.models import Opportunity, SearchRequest

_DATA_DIR = Path(__file__).parent
OPPORTUNITIES_FILE = _DATA_DIR / "mock_opportunities.json"
PROFILES_FILE = _DATA_DIR / "mock_profiles.json"


class MockProfile(BaseModel):
    id: str
    label: str
    request: SearchRequest


class OpportunityRepository:
    def __init__(self, opportunities: list[Opportunity]) -> None:
        self._by_id = {o.id: o for o in opportunities}

    def all(self) -> list[Opportunity]:
        return list(self._by_id.values())

    def get(self, opportunity_id: str) -> Opportunity | None:
        return self._by_id.get(opportunity_id)


def load_mock_opportunities(path: Path = OPPORTUNITIES_FILE) -> list[Opportunity]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    # The file carries a top-level note explaining it is illustrative.
    return [Opportunity(**record) for record in payload["opportunities"]]


def load_mock_profiles(path: Path = PROFILES_FILE) -> list[MockProfile]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    return [MockProfile(**record) for record in payload["profiles"]]


@lru_cache(maxsize=1)
def get_repository() -> OpportunityRepository:
    """Loaded once per process; the API depends on this."""
    return OpportunityRepository(load_mock_opportunities())
```

- [ ] **Step 3: Write mock_opportunities.json**

Top-level shape:

```json
{
  "_note": "Illustrative mock data for the Find Me Funding prototype. Scheme names are real; amounts, dates and eligibility rules are plausible but were NOT verified with the funders. Do not treat as advice.",
  "opportunities": [ ... ]
}
```

Write exactly these 30 records. Dates are relative to the test clock TODAY = 2026-09-01: under 15 days is 1 to 15 Sept 2026, 30 to 15 is 16 to 30 Sept, 60 to 30 is 1 to 31 Oct, over 60 is 1 Nov onward. `for_codes` may be two-digit divisions or four-digit groups. Every record has a `summary` of two to four sentences that mentions the scheme's research themes in plain words (these feed keyword matching), `keywords` of four to eight terms, `eligibility_text` of one to three sentences paraphrasing the rules in the funder's voice, `source_urls` containing the `url`, and `toa_codes` from "1" pure basic, "2" strategic basic, "3" applied, "4" experimental development. Use plausible real-looking `url`s on the funder's domain.

| id | title | funder | for_codes | amount_aud | amount_note | deadline | opens_at | countries | citizenships_allowed | employer_types_allowed | career_stages_allowed | funding_types_offered | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| arc-discovery-2027 | ARC Discovery Projects 2027 | Australian Research Council | 31, 34, 37, 40, 44, 46, 49, 51 | 2500000 | up to $500,000 per year for five years | 2027-03-10 | | AU | | university | postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| arc-decra-2028 | ARC Discovery Early Career Researcher Award 2028 | Australian Research Council | 31, 34, 37, 40, 44, 46, 49, 51 | 480000 | over three years | 2026-10-14 | | AU | | university | postdoc_0_2, postdoc_2_5 | salary, consumables | active |
| arc-linkage-continuous | ARC Linkage Projects | Australian Research Council | 31, 34, 37, 40, 44, 46, 49, 51 | | varies with partner contribution | | | AU | | university | postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| nhmrc-ideas-2027 | NHMRC Ideas Grants 2027 | National Health and Medical Research Council | 32, 42, 3202, 4206 | 1200000 | over up to five years | 2027-02-24 | | AU | | university, research_institute | postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| nhmrc-investigator-el | NHMRC Investigator Grant, Emerging Leadership | National Health and Medical Research Council | 32, 42 | 1500000 | salary plus research support over five years | 2026-09-10 | | AU | | university, research_institute | postdoc_0_2, postdoc_2_5, postdoc_5_10 | salary, consumables | active |
| mrff-indigenous-health | MRFF Indigenous Health Research 2026 | Department of Health and Aged Care | 42, 4206, 45 | 3000000 | | 2026-11-30 | | AU | | university, research_institute, philanthropic | | salary, consumables, equipment | active |
| wellcome-discovery-2026 | Wellcome Discovery Award | Wellcome Trust | 31, 32, 42, 3202 | 6000000 | up to eight years | 2026-12-01 | | | | university, research_institute | postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| erc-starting-2027 | ERC Starting Grant 2027 | European Research Council | 31, 32, 34, 37, 40, 44, 46, 49, 51 | 2500000 | up to five years, host must be in an EU or associated country | 2026-10-20 | | AT, BE, DE, DK, ES, FI, FR, IE, IT, NL, NO, PL, PT, SE | | university, research_institute | postdoc_2_5, postdoc_5_10 | salary, consumables, equipment | active |
| erc-consolidator-2027 | ERC Consolidator Grant 2027 | European Research Council | 31, 32, 34, 37, 40, 44, 46, 49, 51 | 3300000 | up to five years | 2027-01-15 | 2026-11-01 | AT, BE, DE, DK, ES, FI, FR, IE, IT, NL, NO, PL, PT, SE | | university, research_institute | postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| nih-r01-cancer-genomics | NIH R01: Cancer Genomics and Computational Oncology | National Institutes of Health | 32, 3202, 3105, 4905 | 3800000 | over five years | 2026-10-05 | | | | university, research_institute, industry | postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| nih-k99-r00 | NIH K99/R00 Pathway to Independence Award | National Institutes of Health | 32, 42 | 1400000 | | 2026-10-12 | | | | university, research_institute | postdoc_0_2, postdoc_2_5 | salary | active |
| msca-postdoctoral-2026 | Marie Skłodowska-Curie Postdoctoral Fellowship 2026 | European Commission | 31, 32, 34, 37, 40, 44, 46, 49, 51 | 300000 | two years | 2026-09-10 | | | | university, research_institute, industry | postdoc_0_2, postdoc_2_5, postdoc_5_10 | salary | active |
| fulbright-au-postdoctoral | Fulbright Future Scholarship, Postdoctoral | Fulbright Australia | 31, 32, 34, 37, 40, 42, 44, 46, 49, 51 | 60000 | living allowance and travel | 2026-09-25 | | | AU | | postdoc_0_2, postdoc_2_5, postdoc_5_10 | salary | active |
| fulbright-us-scholar-au | Fulbright US Scholar Award to Australia | Fulbright Australia | 31, 32, 34, 37, 40, 42, 44, 46, 49, 51 | 50000 | | 2026-09-15 | | | US | | postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus | salary | active |
| gates-grand-challenges-health | Grand Challenges: Global Health Equity | Gates Foundation | 32, 42, 4206 | 150000 | seed funding | 2026-11-18 | | | | university, research_institute, industry, philanthropic | | salary, consumables, equipment | active |
| ian-potter-science-2027 | Ian Potter Foundation Science Grants 2027 | Ian Potter Foundation | 31, 37, 3103 | 400000 | | 2027-04-01 | 2027-01-15 | AU | | philanthropic | | equipment, consumables | active |
| westpac-research-fellowship | Westpac Research Fellowship | Westpac Scholars Trust | 31, 34, 37, 40, 42, 44, 46, 49, 51 | 500000 | over three years | 2026-11-02 | | AU | AU | university | postdoc_2_5, postdoc_5_10 | salary, consumables | active |
| csiro-early-career-postdoc | CSIRO Early Research Career Postdoctoral Fellowship | CSIRO | 31, 34, 37, 40, 46, 51 | 350000 | three-year salary | 2026-09-20 | | AU | AU, NZ | research_institute | postdoc_0_2 | salary | active |
| csiro-industry-phd | CSIRO Industry PhD Program | CSIRO | 34, 40, 46 | 180000 | four-year stipend | 2026-10-31 | | AU | AU, NZ | university, industry | graduate_student | salary | active |
| google-phd-fellowship-2027 | Google PhD Fellowship 2027 | Google | 46, 4602, 4611 | 120000 | two-year stipend | 2027-03-01 | | | | university | graduate_student | salary | active |
| aws-cloud-credits-research | AWS Cloud Credit for Research | Amazon Web Services | 46, 49, 4611 | 30000 | credits, not cash | | | | | university, research_institute | | equipment | active |
| ukri-future-leaders-2026 | UKRI Future Leaders Fellowship, Round 10 | UK Research and Innovation | 31, 32, 34, 37, 40, 44, 46, 49, 51 | 2800000 | up to seven years | 2026-12-08 | | GB | | university, research_institute, industry | postdoc_0_2, postdoc_2_5, postdoc_5_10 | salary, consumables, equipment | active |
| innovate-uk-energy-catalyst | Innovate UK Energy Catalyst Round 12 | Innovate UK | 40, 4008 | 1800000 | | 2026-10-08 | | GB | | industry | | equipment, salary | active |
| arena-advancing-renewables | ARENA Advancing Renewables Program | Australian Renewable Energy Agency | 40, 4008 | 8000000 | | | | AU | | industry, university, research_institute | | equipment, consumables, salary | active |
| arc-future-fellowships-2026 | ARC Future Fellowships 2026 | Australian Research Council | 31, 34, 37, 40, 44, 46, 49, 51 | 1100000 | over four years | 2026-07-15 | | AU | | university | postdoc_5_10, postdoc_10_plus | salary, consumables | closed |
| nhmrc-synergy-2026 | NHMRC Synergy Grants 2026 | National Health and Medical Research Council | 32, 42 | 5000000 | over five years | 2026-08-05 | | AU | | university, research_institute | postdoc_5_10, postdoc_10_plus | salary, consumables, equipment | active |
| lowitja-indigenous-health-2026 | Lowitja Institute Community-Led Research Grants 2026 | Lowitja Institute | 42, 4206, 45 | | | | | AU | | university, research_institute, philanthropic | | consumables, salary | closed |
| uom-summer-research-2026 | University of Melbourne Summer Research Scholarship | University of Melbourne | 31, 32, 34, 37, 40, 42, 44, 46, 49, 51 | 6000 | stipend for eight weeks | 2026-09-30 | | AU | | university | undergraduate | salary | active |
| amsi-vacation-research-2026 | AMSI Vacation Research Scholarship | Australian Mathematical Sciences Institute | 49, 51, 4905, 5108 | 5000 | six-week stipend | 2026-09-28 | | AU | AU, NZ | university | undergraduate | salary | active |
| gbrf-reef-trust-partnership | Reef Trust Partnership: Reef Restoration and Adaptation | Great Barrier Reef Foundation | 31, 3103, 3708 | | scaled to project | 2026-12-15 | | AU | | university, research_institute, philanthropic | | consumables, equipment | active |

Summaries must contain the theme words a matching profile would use. In particular: `gbrf-reef-trust-partnership` mentions coral reef, ocean acidification and resilience; `nih-r01-cancer-genomics` mentions cancer, genomic, statistical methods; `google-phd-fellowship-2027` and `aws-cloud-credits-research` mention machine learning; `innovate-uk-energy-catalyst` and `arena-advancing-renewables` mention battery, energy storage, grid; `mrff-indigenous-health` and `lowitja-indigenous-health-2026` mention Indigenous community health; `amsi-vacation-research-2026` mentions quantum and mathematics; `arc-discovery-2027` is generic across disciplines.

- [ ] **Step 4: Write mock_profiles.json**

```json
{
  "_note": "Researcher profiles used by the tests, the evals and the frontend demo. Illustrative only.",
  "profiles": [
    {
      "id": "au-marine-postdoc",
      "label": "Australian marine ecologist, university postdoc 2 to 5 years, wants consumables or equipment",
      "request": {
        "for_codes": ["3103", "3708"],
        "toa_codes": ["2"],
        "citizenships": ["AU"],
        "employer_type": "university",
        "career_stage": "postdoc_2_5",
        "funding_types": ["consumables", "equipment"],
        "research_description": "Coral reef resilience to ocean acidification, combining field surveys with ecosystem modelling."
      }
    },
    {
      "id": "intl-cs-phd",
      "label": "Indian citizen, PhD student in computer science at an Australian university, needs a stipend",
      "request": {
        "for_codes": ["4611"],
        "toa_codes": ["3"],
        "citizenships": ["IN"],
        "employer_type": "university",
        "career_stage": "graduate_student",
        "funding_types": ["salary"],
        "research_description": "Machine learning for medical imaging, focusing on segmentation of MRI scans."
      }
    },
    {
      "id": "uk-industry-engineer",
      "label": "British engineer in industry, 5 to 10 years post PhD, needs equipment",
      "request": {
        "for_codes": ["4008"],
        "toa_codes": ["4"],
        "citizenships": ["GB"],
        "employer_type": "industry",
        "career_stage": "postdoc_5_10",
        "funding_types": ["equipment"],
        "research_description": "Battery energy storage systems and their integration with the electricity grid."
      }
    },
    {
      "id": "philanthropic-health-ecr",
      "label": "Early career researcher at a philanthropic health organisation, any funding type",
      "request": {
        "for_codes": ["4206"],
        "citizenships": ["AU"],
        "employer_type": "philanthropic",
        "career_stage": "postdoc_0_2",
        "funding_types": ["any"],
        "research_description": "Evaluation of Indigenous community health programs in regional Australia."
      }
    },
    {
      "id": "undergrad-physics",
      "label": "Australian undergraduate in physics looking for a paid summer project",
      "request": {
        "for_codes": ["5108"],
        "citizenships": ["AU"],
        "employer_type": "university",
        "career_stage": "undergraduate",
        "funding_types": ["salary"],
        "research_description": "Quantum sensing summer research project using diamond defects."
      }
    },
    {
      "id": "senior-climate-scientist",
      "label": "Dual AU and NZ citizen at a research institute, 10 plus years post PhD, no funding type preference",
      "request": {
        "for_codes": ["3702"],
        "citizenships": ["AU", "NZ"],
        "employer_type": "research_institute",
        "career_stage": "postdoc_10_plus",
        "research_description": "Regional climate model downscaling to support agricultural adaptation planning."
      }
    },
    {
      "id": "text-only-biostatistics",
      "label": "Free-text description only, nothing else supplied",
      "request": {
        "research_description": "Statistical methods for genomic data in cancer, including survival models and machine learning."
      }
    },
    {
      "id": "empty",
      "label": "Empty search: no personalisation at all",
      "request": {}
    }
  ]
}
```

Run: `backend/.venv/bin/pytest backend/tests -v` Expected: all PASS. If a coverage test fails, fix the data, not the test.

- [ ] **Step 5: Commit and push** (message `feat(data): illustrative mock opportunities, profiles and repository`, files `backend/data backend/tests/test_repository.py`, push, trailers as in Task 1).

---

### Task 7: FastAPI search endpoint

**Files:**
- Create: `backend/api/__init__.py`, `backend/api/schemas.py`, `backend/api/main.py`, `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `rank` from Task 5; `resolve_weights` from Task 1; `get_repository` from Task 6; `SearchRequest`, `RankedOpportunity`, `Opportunity` from Task 1; `__version__` from `backend.ranking`.
- Produces: ASGI app `backend.api.main:app` with `GET /api/health`, `POST /api/search`, `GET /api/opportunities/{opportunity_id}`; `SearchResponse` with `results`, `total`, `limit`, `offset`, `weights`.

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_api.py`:

```python
"""The API is the seam with the React frontend (Jira KAN-11). These tests pin
the contract rules in docs/api-contract.md."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.data.repository import get_repository
from backend.ranking.models import SearchRequest
from backend.ranking.ranker import rank
from backend.ranking.weights import DEFAULT_WEIGHTS


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def open_count() -> int:
    # The API uses the real clock, so the expected total is computed the same way.
    return len(rank(get_repository().all(), SearchRequest(), DEFAULT_WEIGHTS, date.today()))


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["version"]


def test_empty_search_returns_first_ten_and_total_of_open_set(client):
    body = client.post("/api/search", json={}).json()
    assert len(body["results"]) == 10
    assert body["total"] == open_count()
    assert body["limit"] == 10
    assert body["offset"] == 0


def test_every_result_has_four_scores_labels_and_reasons(client):
    result = client.post("/api/search", json={}).json()["results"][0]
    for key in ("eligibility", "research_match", "funding_value", "deadline"):
        assert set(result[key]) == {"score", "label", "reasons"}
        assert result[key]["reasons"]
    assert "overall" in result
    assert result["opportunity"]["url"].startswith("http")


def test_offset_paging_continues_the_same_ordering(client):
    first = client.post("/api/search", json={"limit": 5}).json()["results"]
    second = client.post("/api/search", json={"limit": 5, "offset": 5}).json()["results"]
    everything = client.post("/api/search", json={"limit": 100}).json()["results"]
    assert [r["opportunity"]["id"] for r in first + second] == [
        r["opportunity"]["id"] for r in everything[:10]
    ]


def test_weights_are_echoed_and_overridable(client):
    default = client.post("/api/search", json={}).json()["weights"]
    assert default == DEFAULT_WEIGHTS.as_dict()
    custom = client.post("/api/search", json={"weights": {"deadline": 0.9}}).json()["weights"]
    assert custom["deadline"] == 0.9
    assert custom["eligibility"] == DEFAULT_WEIGHTS.eligibility


def test_hide_ineligible_removes_likely_ineligible_end_to_end(client):
    request = {"citizenships": ["US"], "employer_type": "industry", "limit": 100}
    shown = client.post("/api/search", json=request).json()["results"]
    hidden = client.post("/api/search", json={**request, "hide_ineligible": True}).json()["results"]
    assert any(r["eligibility"]["label"] == "likely_ineligible" for r in shown)
    assert not any(r["eligibility"]["label"] == "likely_ineligible" for r in hidden)
    assert len(hidden) < len(shown)


def test_include_closed_adds_the_soft_deleted_records(client):
    open_total = client.post("/api/search", json={}).json()["total"]
    all_total = client.post("/api/search", json={"include_closed": True}).json()["total"]
    assert all_total == len(get_repository().all())
    assert all_total > open_total


@pytest.mark.parametrize("payload", [{"limit": 0}, {"limit": 101}, {"career_stage": "professor"}])
def test_invalid_input_is_422(client, payload):
    assert client.post("/api/search", json=payload).status_code == 422


def test_get_opportunity_by_id_including_closed(client):
    closed = next(o for o in get_repository().all() if o.status == "closed")
    body = client.get(f"/api/opportunities/{closed.id}").json()
    assert body["id"] == closed.id


def test_unknown_opportunity_is_404(client):
    assert client.get("/api/opportunities/nope").status_code == 404
```

Run: `backend/.venv/bin/pytest backend/tests/test_api.py -v` Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 2: Write schemas.py and main.py**

`backend/api/__init__.py` is empty. `backend/api/schemas.py`:

```python
"""Response shapes for the search API. Request shapes live in
backend/ranking/models.py because the ranker shares them."""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.ranking.models import RankedOpportunity


class HealthResponse(BaseModel):
    status: str
    version: str


class SearchResponse(BaseModel):
    results: list[RankedOpportunity]
    total: int = Field(description="Size of the full ranked set, not of this page.")
    limit: int
    offset: int
    weights: dict[str, float] = Field(description="Weights used for this search, echoed.")
```

`backend/api/main.py`:

```python
"""FastAPI search service for the React frontend.

Run from the repository root:  uvicorn backend.api.main:app --reload
Interactive docs at http://localhost:8000/docs are the authoritative API
agreement (Jira KAN-11); docs/api-contract.md is the human summary.

Decision 6: a search ranks what is already indexed and "more results" pages
over the same ranked set. Nothing here triggers a crawl.
"""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import ranking
from backend.api.schemas import HealthResponse, SearchResponse
from backend.data.repository import get_repository
from backend.ranking.models import Opportunity, SearchRequest
from backend.ranking.ranker import rank
from backend.ranking.weights import resolve_weights

app = FastAPI(title="Find Me Funding API", version=ranking.__version__)

# The Vite dev server; add the deployed frontend origin here when there is one.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=ranking.__version__)


@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    weights = resolve_weights(request.weights)
    ranked = rank(get_repository().all(), request, weights, date.today())
    page = ranked[request.offset : request.offset + request.limit]
    return SearchResponse(
        results=page,
        total=len(ranked),
        limit=request.limit,
        offset=request.offset,
        weights=weights.as_dict(),
    )


@app.get("/api/opportunities/{opportunity_id}", response_model=Opportunity)
def get_opportunity(opportunity_id: str) -> Opportunity:
    # Closed records are returned too: they are soft-deleted, not gone (decision 9).
    opportunity = get_repository().get(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return opportunity
```

Run: `backend/.venv/bin/pytest backend/tests -v` Expected: all PASS. Then smoke it: `backend/.venv/bin/uvicorn backend.api.main:app --port 8000 &`, `curl -s -X POST localhost:8000/api/search -H 'content-type: application/json' -d '{"citizenships":["AU"],"career_stage":"postdoc_2_5","for_codes":["3103"]}' | head -c 600`, then stop the server.

- [ ] **Step 3: Commit and push** (message `feat(api): FastAPI search endpoint with paging, weights echo and CORS`, files `backend/api backend/tests/test_api.py`, push, trailers as in Task 1).

---

### Task 8: Golden-set evals

**Files:**
- Create: `backend/evals/__init__.py`, `backend/evals/golden.json`, `backend/evals/run_evals.py`, `backend/tests/test_evals.py`

**Interfaces:**
- Consumes: `rank`, `DEFAULT_WEIGHTS`, `Weights`, `load_mock_opportunities`, `load_mock_profiles`, `TODAY`.
- Produces: `evaluate(today: date, weights: Weights = DEFAULT_WEIGHTS) -> EvalReport` with fields `label_accuracy: float`, `top5_pass_rate: float`, `top10_exclusion_pass_rate: float`, `per_profile: list[ProfileReport]`; `main()` printing the report and a weight-sensitivity table, exit code 1 on threshold failure.

- [ ] **Step 1: Write golden.json by hand**

Label by reading the data table in Task 6 and the rules in Tasks 2 to 5, not by running the code. For each of the eight profiles give `expected_eligibility` for at least six opportunities (covering more than one state where the profile allows it), `must_be_in_top_5` (one to three ids) and `must_not_be_in_top_10` (one to three ids). Shape:

```json
{
  "_note": "Hand-labelled expectations. Labels were derived by reading mock_opportunities.json against the rules in the spec, not by running the ranker. A failing eval means either the rules changed or a label is wrong; decide which before editing.",
  "today": "2026-09-01",
  "profiles": {
    "au-marine-postdoc": {
      "expected_eligibility": {
        "arc-discovery-2027": "eligible",
        "gbrf-reef-trust-partnership": "eligible",
        "gates-grand-challenges-health": "eligible",
        "csiro-early-career-postdoc": "likely_ineligible",
        "google-phd-fellowship-2027": "likely_ineligible",
        "ian-potter-science-2027": "likely_ineligible",
        "wellcome-discovery-2026": "likely_ineligible",
        "msca-postdoctoral-2026": "likely_ineligible"
      },
      "must_be_in_top_5": ["gbrf-reef-trust-partnership", "arc-discovery-2027"],
      "must_not_be_in_top_10": ["google-phd-fellowship-2027", "fulbright-us-scholar-au", "nih-k99-r00"]
    }
  }
}
```

Worked reasoning for the first profile, to copy for the others: the AU marine postdoc is a university postdoc_2_5 wanting consumables or equipment. `arc-discovery-2027` states no citizenship, allows university, allows postdoc_2_5, offers consumables: every stated check passes, so eligible. `csiro-early-career-postdoc` allows AU citizens but only research institutes and only postdoc_0_2: employer fails, so likely ineligible. `msca-postdoctoral-2026` passes employer and stage but offers only salary while the researcher asked for consumables or equipment: funding type fails. `gbrf-reef-trust-partnership` is eligible, matches FoR 3103 exactly and mentions coral reef acidification, closes in over 60 days, so it must be in the top 5.

For `empty`, every opportunity is unknown or potentially eligible, so `expected_eligibility` uses those two states only and `must_not_be_in_top_10` lists the three closed or past-deadline ids (they are filtered out entirely).

- [ ] **Step 2: Write the failing eval test**

`backend/tests/test_evals.py`:

```python
"""Ranking quality regression: the golden set must keep passing."""

from backend.evals.run_evals import evaluate
from backend.tests.conftest import TODAY


def test_golden_thresholds_hold():
    report = evaluate(TODAY)
    failures = [f for p in report.per_profile for f in p.failures]
    assert report.label_accuracy >= 0.9, failures
    assert report.top5_pass_rate == 1.0, failures
    assert report.top10_exclusion_pass_rate == 1.0, failures
```

- [ ] **Step 3: Write run_evals.py**

```python
"""Golden-set evaluation of the ranker.

Usage, from the repository root:  python -m backend.evals.run_evals

Compares the ranker's output for each mock profile against hand-written
expectations in golden.json, then shows how the top 5 shifts under a few
alternative weightings so the team can see what the open weighting decision
actually changes. Exit code 1 if any threshold fails.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from backend.data.repository import load_mock_opportunities, load_mock_profiles
from backend.ranking.ranker import rank
from backend.ranking.weights import DEFAULT_WEIGHTS, Weights

GOLDEN_FILE = Path(__file__).parent / "golden.json"

ALTERNATIVE_WEIGHTS = {
    "default": DEFAULT_WEIGHTS,
    "eligibility-heavy": Weights(eligibility=0.7, research_match=0.2, funding_value=0.05, deadline=0.05),
    "match-heavy": Weights(eligibility=0.3, research_match=0.5, funding_value=0.1, deadline=0.1),
    "even": Weights(eligibility=0.25, research_match=0.25, funding_value=0.25, deadline=0.25),
}


@dataclass
class ProfileReport:
    profile_id: str
    labels_checked: int = 0
    labels_correct: int = 0
    top5_checks: int = 0
    top5_passed: int = 0
    top10_checks: int = 0
    top10_passed: int = 0
    failures: list[str] = field(default_factory=list)


@dataclass
class EvalReport:
    per_profile: list[ProfileReport]

    def _rate(self, passed: str, checked: str) -> float:
        total = sum(getattr(p, checked) for p in self.per_profile)
        return sum(getattr(p, passed) for p in self.per_profile) / total if total else 1.0

    @property
    def label_accuracy(self) -> float:
        return self._rate("labels_correct", "labels_checked")

    @property
    def top5_pass_rate(self) -> float:
        return self._rate("top5_passed", "top5_checks")

    @property
    def top10_exclusion_pass_rate(self) -> float:
        return self._rate("top10_passed", "top10_checks")


def evaluate(today: date, weights: Weights = DEFAULT_WEIGHTS) -> EvalReport:
    golden = json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))["profiles"]
    opportunities = load_mock_opportunities()
    reports = []
    for profile in load_mock_profiles():
        expected = golden.get(profile.id)
        if expected is None:
            continue
        report = ProfileReport(profile_id=profile.id)
        ranked = rank(opportunities, profile.request, weights, today)
        by_id = {r.opportunity.id: r for r in ranked}
        order = [r.opportunity.id for r in ranked]

        for opp_id, label in expected.get("expected_eligibility", {}).items():
            report.labels_checked += 1
            actual = by_id[opp_id].eligibility.label if opp_id in by_id else "filtered-out"
            if actual == label:
                report.labels_correct += 1
            else:
                report.failures.append(f"{profile.id}: {opp_id} eligibility {actual!r}, expected {label!r}")

        for opp_id in expected.get("must_be_in_top_5", []):
            report.top5_checks += 1
            if opp_id in order[:5]:
                report.top5_passed += 1
            else:
                position = order.index(opp_id) + 1 if opp_id in order else None
                report.failures.append(f"{profile.id}: {opp_id} expected in top 5, was at {position}")

        for opp_id in expected.get("must_not_be_in_top_10", []):
            report.top10_checks += 1
            if opp_id not in order[:10]:
                report.top10_passed += 1
            else:
                report.failures.append(f"{profile.id}: {opp_id} expected outside top 10, was at {order.index(opp_id) + 1}")
        reports.append(report)
    return EvalReport(per_profile=reports)


def _print_report(report: EvalReport) -> None:
    print(f"{'profile':30} {'labels':>8} {'top5':>6} {'top10x':>7}")
    for p in report.per_profile:
        print(
            f"{p.profile_id:30} {p.labels_correct:>3}/{p.labels_checked:<4} "
            f"{p.top5_passed:>2}/{p.top5_checks:<3} {p.top10_passed:>3}/{p.top10_checks:<3}"
        )
    print(
        f"\nlabel accuracy {report.label_accuracy:.2f}   top-5 {report.top5_pass_rate:.2f}   "
        f"top-10 exclusion {report.top10_exclusion_pass_rate:.2f}"
    )
    for p in report.per_profile:
        for failure in p.failures:
            print("  FAIL", failure)


def _print_weight_sensitivity(today: date) -> None:
    print("\nTop 5 under alternative weightings (open decision, see docs/ranking-discussion-points.md)")
    opportunities = load_mock_opportunities()
    for profile in load_mock_profiles():
        print(f"\n{profile.id}")
        for name, weights in ALTERNATIVE_WEIGHTS.items():
            top = [r.opportunity.id for r in rank(opportunities, profile.request, weights, today)[:5]]
            print(f"  {name:18} {', '.join(top)}")


def main() -> int:
    today = date.fromisoformat(json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))["today"])
    report = evaluate(today)
    _print_report(report)
    _print_weight_sensitivity(today)
    ok = report.label_accuracy >= 0.9 and report.top5_pass_rate == 1.0 and report.top10_exclusion_pass_rate == 1.0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

Run: `backend/.venv/bin/python -m backend.evals.run_evals` from the repository root, then `backend/.venv/bin/pytest backend/tests/test_evals.py -v`. Expected: report prints; test passes. If a label fails, re-read the data and the rule and decide whether the label or the data is wrong. Do not change scorer code to make a label pass.

- [ ] **Step 4: Commit and push** (message `feat(evals): golden-set ranking evals with weight sensitivity report`, files `backend/evals backend/tests/test_evals.py`, push, trailers as in Task 1).

---

### Task 9: Documentation

**Files:**
- Create: `docs/adr/ADR-002-ranking-engine.md`, `docs/api-contract.md`, `docs/ranking-discussion-points.md`
- Modify: `backend/README` (the status table rows for ranking and API, plus a short "Running the API and tests" section after "Running the crawler")

Prose is one line per paragraph or list item, never hard-wrapped. Keep each document short; they are read by teammates and pasted into Confluence.

- [ ] **Step 1: ADR-002**

Sections in the team's ADR format from the Architecture and Design page: Decision ID, Decision, Status (Proposed), Context, Options (single module; one module per criterion; pluggable scorer classes; LLM-only score), Rationale, Consequences, Evidence (Confluence decisions 3, 4, 5, 6, 9; 20/08 meeting notes; this spec). State the four score constants tables and the default weights.

- [ ] **Step 2: api-contract.md**

Endpoints with example request and response JSON (take a real response from the running server, trimmed to one result), then the seven contract rules: four scores always separate; weights echoed; four eligibility states; reasons are user-facing; closed excluded by default; paging is limit plus offset over the same set; total is the full set size. Note the `hide_ineligible` and `include_closed` flags and the `weights` override. Say the OpenAPI schema at `/docs` wins if the two disagree. Mention KAN-11.

- [ ] **Step 3: ranking-discussion-points.md**

The six items from spec section 3, each as: what is implemented, the evidence for it, the question for the client, and what changes if the answer differs (a constant, a weight, a flag default). Add the weight-sensitivity output from `run_evals` for one profile as an illustration.

- [ ] **Step 4: README update**

Change the two status rows to "Prototype built (structured mock data)". Add:

```text
## Running the API and tests

From the repository root:

    pip install -r backend/requirements-dev.txt
    uvicorn backend.api.main:app --reload      # docs at http://localhost:8000/docs
    pytest backend                             # unit, API and golden-set tests
    python -m backend.evals.run_evals          # ranking eval report

The ranker currently scores the illustrative opportunities in backend/data/mock_opportunities.json. Wiring it to the crawler's SQLite rows needs a normalisation step that turns raw text into the structured Opportunity fields; see docs/adr/ADR-002-ranking-engine.md.
```

- [ ] **Step 5: Commit and push** (message `docs: ADR-002, API contract, ranking discussion points, README`, files `docs/adr docs/api-contract.md docs/ranking-discussion-points.md backend/README`, push, trailers as in Task 1).

---

## Self-review notes

Spec coverage: sections 4 to 12 map to Tasks 1 to 9; section 13 is out of scope by design. Type names are consistent across tasks (`CriterionResult`, `RankedOpportunity`, `Weights`, `OpportunityRepository`, `MockProfile`). The mock-data coverage in Task 6 replaces the spec's "EU member states citizenship rule" with EU-country `countries` restrictions on the ERC records, because citizenship is not what the ERC restricts; the spec's coverage intent (varied rules across every state) is still met.
