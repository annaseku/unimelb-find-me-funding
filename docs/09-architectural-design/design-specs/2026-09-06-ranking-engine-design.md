# Ranking engine and search API: design spec

> Historical design spec, written before implementation with an AI coding agent. File paths reflect the repository at the time. Current design: `docs/09-architectural-design/`.

Date: 2026-09-06. Owner: Anna Sekulic (Ranker prototype, per Sprint Description). Status: approved in conversation, ready for an implementation plan.

## 1. Purpose

Build the prototype ranking engine for Find Me Funding and the FastAPI search endpoint the React frontend will call. The engine takes a researcher's search inputs plus a set of structured funding opportunities and returns them ranked, each carrying the four ratings the client brief requires: eligibility, match to user input, funding value, and time to deadline.

This sprint the engine consumes structured mock data, not the crawler's raw rows. The crawler stores raw signals only (title, page text, parsed deadline, raw dollar string, eligibility snippet); turning those into structured fields is a later normalisation step that will feed the same models this spec defines.

## 2. Decisions this spec implements

Source pages are in the Confluence space Crawlers unless stated.

- Decision 5 (Critical): four separate scores combined with configurable weights. Never one unexplained overall number. Scores and weights are returned to the client.
- Decision 4 (High): eligibility has four states: eligible, potentially eligible, unknown, likely ineligible. Uncertain opportunities stay in the results.
- Decision 3 (Critical): hybrid rules plus LLM. Deterministic checks for citizenship, employer type, career stage, funding type, amount and deadline. The LLM is out of scope this sprint (Sprint Description, 31 Aug) but the code leaves a named seam for it in research match and eligibility prose.
- Decision 6 (Critical): "more results" pages over the same ranked set. No crawl is triggered by a search.
- Decision 9 (Medium): closed opportunities are soft-deleted. Hidden by default, retrievable on request.
- Client brief: top 10 with the ability to ask for more, a direct link per result, and a visible rating against each of the four criteria.
- 20/08 meeting: no preference for Australian over international funding; English only; research funding only.

## 3. Decisions made in this design (discussion points for the team)

These were not settled on Confluence. Each is implemented as below and listed in the discussion-points document for the team and client to confirm or change. Changing any of them is a constant or a weight, not a rewrite.

1. Deadline direction: more lead time scores higher. Over 60 days 1.0, 60 to 30 days 0.8, 30 to 15 days 0.5, under 15 days 0.2, no deadline 0.5. Rationale: the client said a deadline six months out is far more useful than one due next week. The literal phrase "deadline urgency" on the architecture page reads the other way, so this needs confirming.
2. Likely-ineligible results are shown and de-ranked, not hidden. The API accepts `hide_ineligible` (default false) so the frontend can offer a toggle.
3. Default weights: eligibility 0.4, research match 0.3, funding value 0.15, deadline 0.15. Placeholder values chosen to honour "eligibility is the top priority". Callers may override per request.
4. Funding bands follow the backend README proposal: under $1M AUD 0.25, $1M to under $2M 0.5, $2M to under $5M 0.75, $5M and over 1.0, unknown 0.5. Most individual grants land in the bottom band, so the client may prefer finer bands.
5. Score values for eligibility states: eligible 1.0, potentially eligible 0.7, unknown 0.5, likely ineligible 0.1.
6. Country restrictions are stored on the opportunity but not checked, because the frontend collects no country or institution-location input. Citizenship is the proxy for now.

## 4. Package layout

New code lives alongside the untouched crawler package, following the structure proposed in the backend README.

```text
backend/
├── crawler/                 # Jummana's crawler, not modified
├── ranking/
│   ├── __init__.py
│   ├── models.py            # enums, Opportunity, SearchRequest, score/result types
│   ├── weights.py           # default weights, validation, normalisation
│   ├── eligibility.py       # four-state eligibility classifier
│   ├── research_match.py    # FoR, ToA and keyword overlap -> high/medium/low
│   ├── funding_value.py     # amount -> band -> score
│   ├── deadline.py          # days remaining -> band -> score
│   └── ranker.py            # score one, rank many, filter, page
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, routes
│   └── schemas.py           # SearchResponse and any API-only shapes
├── data/
│   ├── __init__.py
│   ├── mock_opportunities.json
│   ├── mock_profiles.json
│   └── repository.py        # loads mock data; the seam a crawler-backed store replaces
├── evals/
│   ├── __init__.py
│   ├── golden.json          # hand-labelled expectations
│   └── run_evals.py         # prints the eval report
├── tests/
│   ├── conftest.py          # fixed TODAY, fixtures, mock data loaders
│   ├── test_models.py
│   ├── test_weights.py
│   ├── test_eligibility.py
│   ├── test_research_match.py
│   ├── test_funding_value.py
│   ├── test_deadline.py
│   ├── test_ranker.py
│   ├── test_repository.py
│   ├── test_api.py
│   └── test_evals.py        # asserts the golden thresholds
├── pyproject.toml           # pytest and ruff config only
├── requirements.txt         # runtime (existing file, extended)
└── requirements-dev.txt     # pytest, httpx
```

Imports use the same absolute style as the crawler (`from backend.ranking.models import ...`), run from the repository root. `backend/pyproject.toml` sets `pythonpath = [".."]` so `pytest backend` works from the root.

Every module starts with a short docstring saying what it does and which Confluence decision it implements. Functions carry one or two line comments where a rule is not obvious from the code. The target reader is a teammate who has not read this spec.

## 5. Data model (`ranking/models.py`)

Pydantic v2 models. The vocabulary matches the crawler's query builder and the frontend inputs so the three sides agree.

Enums:

- `EmployerType`: university, research_institute, industry, philanthropic.
- `CareerStage`: undergraduate, graduate_student, postdoc_0_2, postdoc_2_5, postdoc_5_10, postdoc_10_plus.
- `FundingType`: salary, consumables, equipment, all, any.
- `EligibilityState`: eligible, potentially_eligible, unknown, likely_ineligible.
- `MatchLevel`: high, medium, low.
- `DeadlineBand`: over_60_days, days_60_to_30, days_30_to_15, under_15_days, closed, unknown.
- `FundingBand`: under_1m, from_1m_to_2m, from_2m_to_5m, over_5m, unknown.
- `OpportunityStatus`: active, closed.

`Opportunity` fields: `id` (slug), `title`, `funder`, `url`, `source_urls` (list), `summary`, `amount_aud` (int or None, the maximum available), `amount_note` (str, free text such as "up to" or "per year"), `deadline` (date or None), `opens_at` (date or None), `countries` (ISO 3166-1 alpha-2 list, where the applicant's institution must be based, informational only), `citizenships_allowed` (alpha-2 list, empty means unrestricted), `employer_types_allowed`, `career_stages_allowed`, `funding_types_offered` (each a list of the enum, empty means unrestricted or unstated), `for_codes` (ANZSRC 2020 codes as strings, two or four digits), `toa_codes` (ANZSRC type of activity, strings "1" to "4"), `keywords` (list), `eligibility_text` (prose kept for the future LLM check), `status`.

`SearchRequest` fields: `for_codes`, `toa_codes`, `citizenships`, `employer_type` (optional), `career_stage` (optional), `funding_types` (list), `research_description` (str), `hide_ineligible` (bool, default false), `include_closed` (bool, default false), `limit` (1 to 100, default 10), `offset` (0 or more, default 0), `weights` (optional override, see section 7). Every field is optional; an empty request ranks everything with no personalisation and every eligibility unknown or potentially eligible.

Result types:

- `CriterionResult`: `score` (0.0 to 1.0), `label` (the enum value for that criterion as a string), `reasons` (list of plain-English sentences).
- `RankedOpportunity`: `opportunity`, `overall` (0.0 to 1.0), `eligibility`, `research_match`, `funding_value`, `deadline` (each a `CriterionResult`).

## 6. Scoring rules

### 6.1 Eligibility (`ranking/eligibility.py`)

For each restriction the opportunity states, compare with the request and record pass, fail or unknown:

- Citizenship: `citizenships_allowed` non-empty. Pass if any requested citizenship is in the list. Fail if citizenships were supplied and none match. Unknown if none supplied.
- Employer type: `employer_types_allowed` non-empty. Same pattern with `employer_type`.
- Career stage: `career_stages_allowed` non-empty. Same pattern with `career_stage`.
- Funding type: `funding_types_offered` non-empty and the request lists funding types. Pass if the request contains all or any, or if any requested type is offered. Fail otherwise. If the request lists no funding types this check is skipped, not unknown, because the researcher expressed no need.

Outcome, checked in this order:

1. Any fail: likely_ineligible, 0.1.
2. No restrictions were checkable (opportunity states none, or every stated one was unknown): unknown 0.5 if at least one was stated, potentially_eligible 0.7 if none were stated. Reason text distinguishes "The funder states no restrictions we can check" from "Restrictions exist but your inputs did not cover them".
3. All checked restrictions passed and none unknown: eligible, 1.0.
4. Mixed pass and unknown: potentially_eligible, 0.7.

Every check appends a reason such as "Open to AU and NZ citizens; you selected AU." or "Restricted to postdocs 0 to 2 years; you selected graduate student." The reasons are the explanation the UI shows.

### 6.2 Research match (`ranking/research_match.py`)

Three components, each 0.0 to 1.0, combined with fixed internal weights and renormalised over the components that could be evaluated:

- FoR overlap (weight 0.5): 1.0 if any exact code matches, 0.5 if any code shares its two-digit division with an opportunity code, else 0.0. Evaluated only if both sides list codes.
- Text overlap (weight 0.4): tokenise the research description and the opportunity's title, summary and keywords (lower-case, alphanumeric, stop words removed, crude suffix stripping so "modelling" and "models" meet). Fraction of description tokens present in the opportunity tokens, scaled so 40 percent coverage gives 1.0. Evaluated only if the description has at least one token after stop-word removal.
- ToA overlap (weight 0.1): 1.0 if any code matches, else 0.0. Evaluated only if both sides list codes.

If no component can be evaluated, score 0.5 and label medium with the reason "No research details were supplied to match on". Labels: high at 0.6 or above, medium at 0.3 or above, low below. The docstring names this module as the seam where an embedding or LLM scorer replaces the text-overlap component (decision 7's semantic search).

### 6.3 Funding value (`ranking/funding_value.py`)

Band from `amount_aud` using the bands in section 3, item 4. Reason states the amount and band, or "Funding amount not stated" for unknown.

### 6.4 Deadline (`ranking/deadline.py`)

`days_remaining = (deadline - today).days`. Band edges are inclusive at the lower end: closed is below 0, under_15_days is 0 to 14, days_30_to_15 is 15 to 29, days_60_to_30 is 30 to 60, over_60_days is 61 and above. Scores from section 3, item 1. Unknown deadline scores 0.5 with band unknown. If `opens_at` is in the future the reason adds "Opens on <date>". `today` is always passed in, never read from the clock inside the module, so tests are deterministic.

### 6.5 Combining (`ranking/ranker.py`)

`score_opportunity(opportunity, request, weights, today)` runs the four scorers and builds a `RankedOpportunity`. `overall = sum(weight_i * score_i) / sum(weights)`, rounded to four decimal places.

`rank(opportunities, request, weights, today)`:

1. Drop `status == closed` and past-deadline opportunities unless `include_closed`.
2. Score every remaining opportunity.
3. Drop likely_ineligible results if `hide_ineligible`.
4. Sort likely-ineligible results after everything else, then by overall descending, then eligibility score descending, then id ascending. The tier rule was added after the first eval run showed a high-match ineligible opportunity landing at position 7 for the philanthropic-sector profile; the client called that outcome "pointless", so de-ranked means "below every result you could apply for", not merely "penalised".

Paging is applied by the API, not the ranker, so the ranker returns the full ordered list and the API reports its length as `total`.

## 7. Weights (`ranking/weights.py`)

`Weights` is a Pydantic model with four non-negative floats and a validator rejecting an all-zero set. `DEFAULT_WEIGHTS` holds the section 3 values. A request may override any subset; missing keys fall back to the defaults. The response echoes the weights actually used.

## 8. API (`api/`)

FastAPI application `backend.api.main:app`. CORS allows `http://localhost:5173` and `http://127.0.0.1:5173` (the Vite dev server) for all methods.

- `GET /api/health` returns `{"status": "ok", "version": "<package version>"}`.
- `POST /api/search` takes a `SearchRequest` body and returns `SearchResponse`: `results` (the page of `RankedOpportunity`), `total` (size of the full ranked set), `limit`, `offset`, `weights` (echoed). `today` is `date.today()` at request time.
- `GET /api/opportunities/{id}` returns the `Opportunity`, including closed ones, or 404.

Validation errors return FastAPI's standard 422. The OpenAPI schema at `/docs` is the authoritative API agreement for KAN-11; `docs/api-contract.md` is the human summary.

## 9. Mock data (`data/`)

`mock_opportunities.json`: about 30 opportunities modelled on real schemes (ARC Discovery and DECRA, NHMRC Ideas and Investigator, MRFF, Wellcome, ERC Starting and Consolidator, NIH R01, Marie Skłodowska-Curie, Fulbright, Gates Foundation, Ian Potter Foundation, Westpac Scholars, industry programs, university internal schemes). The file header and the loader docstring state the values are illustrative and not verified against the funders. Coverage requirements:

- Every FoR division used by the profiles, with several opportunities per division and some cross-disciplinary ones.
- All four funding bands plus at least three with no amount.
- All four deadline bands, at least three closed, at least two with no deadline, at least two with a future `opens_at`.
- Citizenship rules: unrestricted, AU only, AU or NZ, EU member states, US, UK, and one "any citizenship but institution must be in AU" (countries set, citizenship empty).
- Career stage rules across every stage, including a few restricted to a single stage.
- Employer type rules including industry-only and philanthropic-only.
- Funding type coverage across salary, consumables, equipment and combinations.

`mock_profiles.json`: eight researcher profiles as `SearchRequest` bodies with an `id` and a `label`, chosen so the evals exercise every eligibility state: for example an AU postdoc 2 to 5 in marine science, an international PhD student in computer science, a UK citizen in industry, a philanthropic-sector researcher, an undergraduate, a senior researcher 10 plus with no funding type preference, one profile with only a free-text description, and one empty profile.

`repository.py` exposes `OpportunityRepository` with `all()` and `get(id)`, backed by the JSON file. This is the only place the API touches data, so a crawler-backed repository replaces one class.

## 10. Tests (`tests/`)

Pytest. `conftest.py` defines `TODAY = date(2026, 9, 1)` and loads the mock files. Every test that depends on dates uses `TODAY`. One test file per module, test names state what they prove. Coverage targets:

- Models: enum vocabulary matches the crawler's query builder keys; empty request validates; limit bounds enforced.
- Weights: defaults sum as expected; all-zero rejected; partial override merges with defaults.
- Eligibility: one test per state, one per restriction kind, all/any never contradicts, no-inputs request is unknown or potentially eligible, reasons are non-empty.
- Research match: exact FoR gives high; same-division gives medium; text-only overlap; no details gives medium 0.5; stop words ignored.
- Funding value: one parametrised test over the band edges (999_999, 1_000_000, 1_999_999, 2_000_000, 4_999_999, 5_000_000) plus unknown.
- Deadline: parametrised band edges (61, 60, 30, 29, 15, 14, 0, minus 1) plus unknown and opens_at.
- Ranker: weighting entirely on one criterion reproduces that score; closed hidden by default and retrievable; hide_ineligible drops only likely_ineligible; sort order is deterministic; every result carries four criteria with reasons.
- Repository: loads all mock opportunities, ids unique, get returns None for a missing id, every record validates.
- API: health; empty search returns 10 with total equal to the mock count minus closed; offset paging is consistent; hide_ineligible works end to end; invalid limit is 422; get by id and 404; weights echoed.

## 11. Evals (`evals/`)

`golden.json` maps each profile id to: `expected_eligibility` (opportunity id to state, hand-labelled for around six opportunities per profile), `must_be_in_top_5` (ids) and `must_not_be_in_top_10` (ids). Labels are written by reading the mock data, not by running the code, so they test the rules rather than restate them.

`run_evals.py` (`python -m backend.evals.run_evals`) prints, per profile, eligibility label accuracy, top-5 and top-10 constraint pass rates, and then a weight-sensitivity table showing the top 5 under the default weights and three alternatives (eligibility-heavy, match-heavy, even). It exits non-zero if any threshold fails.

`tests/test_evals.py` asserts overall label accuracy of at least 0.9 and that every top-k constraint holds, so a ranking regression fails the suite.

## 12. Documentation

- `docs/adr/ADR-002-ranking-engine.md`: context, decision, alternatives (single module, plugin scorers, LLM-only), consequences, in the Architecture and Design page's ADR format.
- `docs/api-contract.md`: human summary of the endpoints and the contract rules (four scores always separate, weights echoed, four eligibility states, reasons shown to users, closed excluded by default, paging over the same set, total is the full set size).
- `docs/ranking-discussion-points.md`: the six items in section 3, each with what is implemented, the evidence, and the question for the client.
- `backend/README`: status table updated (ranking engine and API built as prototypes), how to run the API and the tests, how to run the evals.

## 13. Out of scope this sprint

- LLM or embedding scoring. Seams are named; nothing calls a model.
- Normalising crawler rows into `Opportunity` records.
- Deduplication across sources (decision 8). Mock data is already deduplicated; `source_urls` is carried so the field exists.
- Researcher profiles, saved searches, login (decision 10; Sprint Description lists profiles as out of scope).
- Triggering discovery when results are insufficient (decision 6, second half).
- Country and institution-location checks (no frontend input exists).

## 14. Delivery

Branch `feat/ranking-engine` off origin/main, one commit per unit of work, each pushed to origin as it lands, per Anna's instruction. Units: spec; plan; models, weights and tooling; eligibility; research match; funding value and deadline; ranker; mock data and repository; API; evals; documentation.
