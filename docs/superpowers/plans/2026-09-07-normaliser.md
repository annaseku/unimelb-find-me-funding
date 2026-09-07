# Normaliser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the crawler's raw SQLite rows into structured `Opportunity` records so the ranker and API run on real crawled pages, with deterministic rules first and an optional Anthropic extractor filling the prose-derived fields.

**Architecture:** A new `backend/normaliser/` package. `parsers.py` handles crisp values (amount to AUD, deadline, status, id, summary, keywords). `lexicon.py` maps phrases to enum codes. `rules.py` composes them into a `NormalisedRecord` with per-field provenance. `llm.py` defines an `Extractor` protocol, an Anthropic implementation using structured outputs, a fake for tests, and the merge policy (model fills prose fields, never overrides a rule-parsed date or amount). `pipeline.py` reads the crawler table, writes `normalised_opportunities` in the same SQLite file, and skips unchanged pages by content hash. `backend/data/sqlite_repository.py` serves that table through the existing repository seam, selected by `FMF_DATA_SOURCE`. Design record: `docs/adr/ADR-003-normaliser.md` (Task 6). Shared models already exist in `backend/normaliser/models.py`; fixtures in `backend/tests/fixtures/crawled_rows.json`.

**Tech Stack:** Python 3.11 to 3.13, Pydantic v2, `anthropic` 1.x (`client.messages.parse(..., output_format=Model)`), python-dateutil (already a crawler dependency), sqlite3 from the standard library, pytest.

## Global Constraints

- CI runs `ruff check backend`, `ruff format --check backend` (line length 100, isort with `known-first-party = ["backend"]`), `pytest backend -q` on Python 3.11, 3.12 and 3.13, and `python -m backend.evals.run_evals`. Run all of these locally before reporting done: `backend/.venv/bin/ruff check backend && backend/.venv/bin/ruff format backend && backend/.venv/bin/pytest backend -q`.
- Python 3.11 compatibility: no `type X = ...` aliases, no PEP 695 generics. `from __future__ import annotations` at the top of every module.
- Imports are absolute from the repository root: `from backend.normaliser.models import CrawledRow`.
- Do not modify anything under `backend/crawler/`. Importing from it (for example `backend.crawler.storage.init_db` in a test, or `backend.crawler.config.DB_PATH`) is fine.
- Do not modify `backend/.env.example` or add one; another branch owns it. Environment variable names used here: `FMF_DATA_SOURCE` (`mock` default, or `sqlite`), `FMF_DB_PATH` (defaults to the crawler's `DB_PATH`), `FMF_LLM_MODEL` (defaults to `claude-opus-5`), `ANTHROPIC_API_KEY` (read by the Anthropic SDK itself, never by our code).
- Tests never touch the network and never need a key. Date-sensitive tests use `TODAY = date(2026, 9, 1)` from `backend/tests/conftest.py`. Never call `date.today()` inside `backend/normaliser/` except in `run.py`'s argument default.
- Every module starts with a short docstring saying what it does. Add a one or two line comment where a rule is not obvious. No docstrings that restate the code.
- Australian English in prose. Do not run git commands; the orchestrator commits per task.

## File structure

| Path | Responsibility | Task |
| --- | --- | --- |
| `backend/normaliser/__init__.py`, `models.py` | package docstring; `CrawledRow`, `NormalisedRecord`, `Source` | done |
| `backend/tests/fixtures/crawled_rows.json` | five realistic crawler rows | done |
| `backend/normaliser/parsers.py` + `backend/tests/test_parsers.py` | amount, deadline, status, id, summary, keywords | 1 |
| `backend/normaliser/lexicon.py` + `backend/tests/test_lexicon.py` | phrase to code tables for citizenship, employer, career stage, funding type, FoR division | 2 |
| `backend/normaliser/llm.py` + `backend/tests/test_llm.py` | `ExtractedFields`, `Extractor` protocol, `AnthropicExtractor`, `FakeExtractor`, `merge`, `extractor_from_env` | 3 |
| `backend/normaliser/rules.py` + `backend/tests/test_rules.py` | `normalise_row`, `load_fixture_rows` | 4 (needs 1, 2) |
| `backend/normaliser/pipeline.py`, `run.py`, `backend/data/sqlite_repository.py`, edit `backend/data/repository.py`, tests | database round trip, CLI, repository switch, API on SQLite | 5 (needs 3, 4) |
| `docs/adr/ADR-003-normaliser.md`, `backend/README.md` | design record, status row, how to run | 6 |

---

### Task 1: Parsers

**Files:** create `backend/normaliser/parsers.py`, `backend/tests/test_parsers.py`.

**Interfaces (exact names and signatures):**

```python
RATES_TO_AUD: dict[str, float]  # {"AUD": 1.0, "USD": 1.5, "EUR": 1.65, "GBP": 1.9, "NZD": 0.93, "CAD": 1.1}
MIN_AMOUNT_AUD = 1_000

def parse_amount_aud(raw: str | None) -> tuple[int | None, str]:
    """Returns (amount in whole AUD, note). Note explains the conversion or why None."""

def parse_deadline(deadline_parsed: str | None, deadline_raw: str | None) -> date | None: ...
def derive_status(deadline: date | None, today: date) -> OpportunityStatus: ...
def make_id(url: str) -> str: ...
def funder_from_url(url: str) -> str: ...
def summarise(raw_text: str | None, title: str | None, max_chars: int = 400) -> str: ...
def keywords_from(title: str | None, limit: int = 8) -> list[str]: ...
```

Rules:

- `parse_amount_aud`: find the first money figure in the string. Currency detection, in this order: `€` or `EUR` gives EUR; `£` or `GBP` gives GBP; `US$` or `USD` gives USD; `NZ$` or `NZD` gives NZD; `CA$` or `CAD` gives CAD; `A$`, `AUD` or a bare `$` gives AUD (bare `$` is assumed AUD because the crawler targets Australian researchers; say so in the note). Multipliers: `million`, `m`, `mn` give 1,000,000; `billion`, `bn`, `b` give 1,000,000,000; `k` or `thousand` give 1,000. Commas inside the number are allowed. Convert with `RATES_TO_AUD` and round to an int. Figures under `MIN_AMOUNT_AUD` after conversion return `(None, "figure below $1,000 ignored")`. No figure returns `(None, "no amount found")`. Notes for a conversion read like `"converted from EUR 1,500,000 at 1.65 AUD per EUR"`; for AUD, `"stated in AUD"` or `"currency not stated, assumed AUD"`.
- `parse_deadline`: if `deadline_parsed` is a valid ISO date, use it. Otherwise try `dateutil.parser.parse(deadline_raw, fuzzy=True, default=datetime(1900, 1, 1))` and accept only years 2020 to 2100. Otherwise `None`.
- `derive_status`: `CLOSED` when the deadline is before `today`, else `ACTIVE`. No deadline is `ACTIVE`.
- `make_id`: host without a leading `www.`, dots and non-alphanumerics replaced by hyphens, then a hyphen and the first 8 hex characters of SHA-256 of the full URL. Example shape: `erc-europa-eu-3f2a9c1d`. Deterministic: same URL, same id.
- `funder_from_url`: host without `www.`, for example `arc.gov.au`. The model may later replace this with the organisation's name.
- `summarise`: if the text starts with the title (case-insensitive), drop that prefix once. Collapse whitespace. Cut at the last sentence end (`. `, `? `, `! `) before `max_chars`; if there is none, cut at `max_chars` and append `…`. Empty or None text gives `""`.
- `keywords_from`: lowercase alphabetic words from the title of length 4 or more, excluding a small stop list (`with`, `from`, `that`, `this`, `grant`, `grants`, `funding`, `program`, `programme`, `scheme`, `award`, `awards`, `research`), unique in order of appearance, at most `limit`.

Required tests (`test_parsers.py`), each its own function with the value in the name where useful:

- amount: `"$500,000"` gives `500_000` and note contains "assumed AUD"; `"AUD 2,000,000"` gives `2_000_000` and note "stated in AUD"; `"A$1.2 million"` gives `1_200_000`; `"EUR 1.5 million"` gives `2_475_000` and note mentions EUR and 1.65; `"£3m"` gives `5_700_000`; `"US$750k"` gives `1_125_000`; `"$5 application fee"` gives `None` with "below"; `None` and `""` give `None` with "no amount found"; `"up to EUR 1.5 million for a period of 5 years"` takes the first figure, not the 5.
- deadline: ISO string wins over raw; raw `"24 February 2027, 5:00 pm AEDT"` parses to 2027-02-24 when parsed is None; garbage raw gives None; a parsed year outside 2020 to 2100 falls back to raw or None.
- status: deadline yesterday relative to TODAY is CLOSED, tomorrow is ACTIVE, None is ACTIVE.
- id: deterministic; two different URLs on the same host get different ids; `www.` is stripped.
- summarise: title prefix removed; cuts at a sentence boundary within 400 characters; None gives `""`.
- keywords: `"ERC Starting Grant - Funding Opportunities for Early-Career Researchers"` yields a list that includes `starting`, `opportunities`, `early`, `career`, `researchers` and excludes `grant` and `funding`; limit respected.

Commit message: `feat(normaliser): parsers for amount, deadline, status, id, summary and keywords`.

---

### Task 2: Lexicon

**Files:** create `backend/normaliser/lexicon.py`, `backend/tests/test_lexicon.py`.

**Interfaces:**

```python
def find_citizenships(text: str | None) -> list[str]: ...        # ISO 3166-1 alpha-2, sorted, unique
def find_employer_types(text: str | None) -> list[EmployerType]: ...
def find_career_stages(text: str | None) -> list[CareerStage]: ...
def find_funding_types(text: str | None) -> list[FundingType]: ...
def find_for_divisions(text: str | None) -> list[str]: ...        # two-digit ANZSRC 2020 division codes, sorted
def stages_for_years(low: int, high: int | None) -> list[CareerStage]: ...
```

All matching is case-insensitive on whole words or phrases (use `\b` boundaries; hyphens and spaces interchangeable, so `early-career` and `early career` both match). `None` or empty text returns `[]`. Return lists are sorted by enum value order for stages and employer types, alphabetically for codes.

Tables:

- Citizenship phrases: `australian citizen(s)`, `citizens of australia`, `australian permanent resident(s)` give `AU`; `new zealand citizen(s)` gives `NZ`; `us citizen(s)`, `u.s. citizen(s)`, `united states citizen(s)` give `US`; `uk national(s)`, `british citizen(s)`, `uk citizen(s)` give `GB`; `canadian citizen(s)` gives `CA`. `any nationality`, `all nationalities`, `no citizenship requirement(s)`, `no citizenship or residency requirements` set nothing (the function returns `[]`, which the ranker treats as unrestricted). Australian permanent residents counting as AU is an assumption; comment it.
- Employer phrases: `university`, `universities`, `higher education` give UNIVERSITY; `research institute(s)`, `medical research institute`, `research organisation(s)`, `research organization(s)` give RESEARCH_INSTITUTE; `industry`, `company`, `companies`, `business(es)`, `sme(s)` give INDUSTRY; `philanthropic`, `not-for-profit`, `non-profit`, `nonprofit`, `charity`, `charities`, `ngo(s)` give PHILANTHROPIC.
- Career stage phrases: `undergraduate(s)` gives UNDERGRADUATE; `phd student(s)`, `phd candidate(s)`, `doctoral student(s)`, `graduate student(s)`, `postgraduate(s)`, `masters student(s)`, `enrolled student(s)` give GRADUATE_STUDENT; `early career`, `early-career`, `ecr(s)` give POSTDOC_0_2 and POSTDOC_2_5; `mid career`, `mid-career` gives POSTDOC_5_10; `senior researcher(s)`, `established researcher(s)`, `professor(s)`, `research leader(s)` give POSTDOC_10_PLUS; `postdoctoral`, `postdoc(s)`, `post-doctoral` give all four postdoc stages. Numeric ranges: `N-M years` / `N to M years` / `between N and M years` / `up to M years` / `within M years` when the sentence also contains `phd`, `doctorate`, `doctoral` or `completion`. `stages_for_years(low, high)` returns the postdoc bands overlapping `[low, high]` using band edges 0 to 2, 2 to 5, 5 to 10, 10 and above; `high=None` means open-ended. `0-10 years ... since completion of PhD` gives all four; `2 and up to 7 years` gives POSTDOC_2_5 and POSTDOC_5_10; `within 10 years of their PhD` gives the first three.
- Funding type phrases: `salary`, `salaries`, `stipend(s)`, `living allowance`, `fellowship salary` give SALARY; `consumables`, `research costs`, `project costs`, `direct costs`, `operating costs`, `travel` give CONSUMABLES; `equipment`, `infrastructure`, `instrument(s)`, `instrumentation` give EQUIPMENT. A phrase preceded within 6 words by `not`, `no`, `does not`, `is not available`, `excluding`, `excludes` is a negation and must not count (the NHMRC fixture says "Salary support ... is not available", so SALARY must not be returned for it).
- FoR divisions (ANZSRC 2020, two-digit) with keyword lists, all 23: 30 agricultural (`agriculture`, `agricultural`, `crop`, `livestock`, `farming`, `veterinary`), 31 biological (`biology`, `biological`, `ecology`, `ecosystem`, `marine`, `coral`, `reef`, `genetics`, `species`, `zoology`, `botany`), 32 biomedical (`biomedical`, `cancer`, `oncology`, `clinical`, `genomic`, `neuroscience`, `immunology`, `medical research`, `disease`), 33 built environment (`architecture`, `urban planning`, `construction`, `building design`), 34 chemical (`chemistry`, `chemical`, `catalysis`), 35 commerce (`management`, `marketing`, `accounting`, `business administration`), 36 creative arts (`creative arts`, `music`, `visual arts`, `performing arts`, `design practice`), 37 earth (`climate`, `geoscience`, `oceanography`, `atmospheric`, `geology`, `earth science`), 38 economics (`economics`, `econometrics`), 39 education (`education`, `pedagogy`, `teaching and learning`), 40 engineering (`engineering`, `battery`, `energy storage`, `grid`, `renewable`, `materials engineering`, `robotics`), 41 environmental (`environmental`, `conservation`, `biodiversity`, `pollution`), 42 health (`health`, `public health`, `epidemiology`, `nursing`, `health services`), 43 history (`history`, `heritage`, `archaeology`), 44 human society (`sociology`, `social science`, `anthropology`, `policy`, `criminology`), 45 indigenous studies (`indigenous`, `aboriginal`, `torres strait`, `first nations`), 46 computing (`machine learning`, `artificial intelligence`, `computing`, `computer science`, `software`, `data science`, `algorithm`, `cybersecurity`), 47 language (`linguistics`, `literature`, `languages`, `communication studies`, `media studies`), 48 law (`law`, `legal`, `jurisprudence`), 49 mathematical (`mathematics`, `mathematical`, `statistics`, `statistical`), 50 philosophy (`philosophy`, `ethics`, `theology`, `religious studies`), 51 physical (`physics`, `quantum`, `astronomy`, `astrophysics`, `photonics`), 52 psychology (`psychology`, `psychological`, `cognitive science`). Return the codes whose keywords appear at least once in the text.

Required tests: one per table with a positive and a negative case; the negation rule using the NHMRC sentence; `stages_for_years` edge cases `(0, 2)`, `(2, 7)`, `(0, 10)`, `(10, None)`, `(0, None)`; `find_for_divisions("coral reef ecosystems and ocean acidification")` gives `["31", "37"]`; hyphen and space equivalence for `early-career`; empty and None input.

Commit message: `feat(normaliser): phrase lexicon for citizenship, employer, career stage, funding type and FoR division`.

---

### Task 3: LLM extractor and merge policy

**Files:** create `backend/normaliser/llm.py`, `backend/tests/test_llm.py`.

**Interfaces:**

```python
DEFAULT_MODEL = "claude-opus-5"
MAX_TEXT_CHARS = 20_000

class ExtractedFields(BaseModel):
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

class AnthropicExtractor:
    def __init__(self, client: Any | None = None, model: str | None = None) -> None: ...
    def extract(self, title: str, url: str, text: str) -> ExtractedFields: ...

class FakeExtractor:
    def __init__(self, result: ExtractedFields) -> None: ...   # records every call in self.calls
    def extract(self, title: str, url: str, text: str) -> ExtractedFields: ...

PROSE_FIELDS: frozenset[str]   # fields the model may override when it returns a non-empty value
RULE_PRIORITY_FIELDS: frozenset[str] = frozenset({"amount_aud", "amount_note", "deadline"})

def merge(record: NormalisedRecord, extracted: ExtractedFields) -> NormalisedRecord: ...
def extractor_from_env(env: Mapping[str, str] | None = None) -> Extractor | None: ...
```

Rules:

- `AnthropicExtractor.__init__` builds `anthropic.Anthropic()` lazily only if `client` is None (import `anthropic` inside the module at top is fine; the package is in requirements). `model` defaults to `os.environ.get("FMF_LLM_MODEL", DEFAULT_MODEL)`.
- `extract` truncates `text` to `MAX_TEXT_CHARS`, then calls `self._client.messages.parse(model=..., max_tokens=4096, system=SYSTEM_PROMPT, messages=[{"role": "user", "content": <title, url, text>}], output_format=ExtractedFields)` and returns `response.parsed_output`. The system prompt tells the model: extract only what the page states, leave a field null or empty when not stated, use ISO 3166-1 alpha-2 for countries and citizenships, `countries` means where the applicant's institution must be based, ANZSRC 2020 codes (two or four digit) for `for_codes`, `"1"` to `"4"` for `toa_codes`, `amount_aud` is the maximum in whole Australian dollars converting other currencies approximately and saying so in `amount_note`, `eligibility_text` is a faithful one to three sentence paraphrase of the stated eligibility rules, `summary` two to three plain sentences on what the scheme funds.
- `merge`: for each field in `PROSE_FIELDS` (`funder`, `summary`, `opens_at`, `countries`, `citizenships_allowed`, `employer_types_allowed`, `career_stages_allowed`, `funding_types_offered`, `for_codes`, `toa_codes`, `keywords`, `eligibility_text`), if the extracted value is non-empty (not None, not `""`, not `[]`) it replaces the record's value and provenance becomes `"llm"`. For `RULE_PRIORITY_FIELDS`, the extracted value is used only when the record's provenance for that field is `"missing"`. Returns a new `NormalisedRecord` with `used_llm=True`; never mutates the input. `amount_note` follows `amount_aud`.
- `extractor_from_env`: returns `None` when `ANTHROPIC_API_KEY` is absent or empty, or when `FMF_LLM` is `"off"`; otherwise an `AnthropicExtractor()`.

Required tests: `FakeExtractor` records calls; `merge` overrides a prose field and marks provenance `llm`; `merge` keeps a rule-parsed deadline when the model disagrees; `merge` fills a missing amount and marks it `llm`; empty extracted lists do not wipe rule values; input record is unchanged after merge; `AnthropicExtractor` with a stub client object (a tiny class whose `messages.parse(**kwargs)` records kwargs and returns an object with `parsed_output`) passes `output_format=ExtractedFields`, the configured model, and truncated text; `extractor_from_env({})` is None, `extractor_from_env({"ANTHROPIC_API_KEY": "x"})` is an `AnthropicExtractor` (construct with a stub client via monkeypatching `anthropic.Anthropic` or accept that constructing the real client with a fake key does not make a network call, which it does not).

For the record type in tests, build a `NormalisedRecord` by hand from an `Opportunity` with `provenance={"deadline": "rule", "amount_aud": "missing", "funder": "rule"}`.

Commit message: `feat(normaliser): Anthropic extractor with structured output and rule-first merge policy`.

---

### Task 4: Rules (compose a record)

**Files:** create `backend/normaliser/rules.py`, `backend/tests/test_rules.py`. Needs Tasks 1 and 2.

**Interfaces:**

```python
FIXTURE_FILE = Path(__file__).parents[1] / "tests" / "fixtures" / "crawled_rows.json"  # only for the helper below

def content_hash(row: CrawledRow) -> str: ...            # sha256 hex of (title or "") + "\n" + (raw_text or "")
def normalise_row(row: CrawledRow, today: date) -> NormalisedRecord: ...
def load_fixture_rows(path: Path = FIXTURE_FILE) -> list[CrawledRow]: ...
```

`normalise_row` builds the `Opportunity`:

- `id = make_id(row.url)`, `url = row.url`, `source_urls = [row.url]`, `title = row.title or funder_from_url(row.url)`, `funder = funder_from_url(row.url)` (provenance `rule`).
- `summary = summarise(row.raw_text, row.title)`; `keywords = keywords_from(row.title)`.
- `amount_aud, amount_note = parse_amount_aud(row.funding_amount_raw)`; provenance `rule` if an amount was found, else `missing`.
- `deadline = parse_deadline(row.deadline_parsed, row.deadline_raw)`; provenance `rule` or `missing`. `status = derive_status(deadline, today)`.
- `citizenships_allowed = find_citizenships(row.raw_text)`; `employer_types_allowed = find_employer_types(row.eligibility_snippet)`; `career_stages_allowed = find_career_stages((row.title or "") + " " + (row.eligibility_snippet or "") + " " + (row.raw_text or ""))`; `funding_types_offered = find_funding_types(row.raw_text)`; `for_codes = find_for_divisions((row.title or "") + " " + summary)`; each with provenance `rule` when non-empty, else `missing`.
- `toa_codes = []`, `countries = []`, `opens_at = None` (all `missing`; the model fills these).
- `eligibility_text = row.eligibility_snippet or ""` (provenance `rule` when present).
- `content_hash` as above, `used_llm=False`.

Required tests against the fixture rows (load them with `load_fixture_rows`, index by URL):

- ERC: amount `2_475_000`, deadline 2026-10-14, status ACTIVE at TODAY, career stages all four postdoc bands, employer types include RESEARCH_INSTITUTE, citizenships `[]` (any nationality), for_codes empty or a subset (generic page), provenance for `deadline` and `amount_aud` is `rule`, `countries` provenance is `missing`.
- ARC Discovery: amount `500_000`, deadline 2027-03-10, employer types `[UNIVERSITY]`, citizenships `[]`, funding types include CONSUMABLES or SALARY only if the text supports them (it does not mention them; assert the list is what the lexicon returns and that the test documents the expectation you observed, do not force it).
- NHMRC Ideas: amount `1_200_000`, deadline 2027-02-24, employer types contain UNIVERSITY and RESEARCH_INSTITUTE, citizenships `["AU"]`, career stages include POSTDOC_0_2, POSTDOC_2_5 and POSTDOC_5_10 (early career, mid career, within 10 years), funding types contain CONSUMABLES and EQUIPMENT and not SALARY, for_codes include `"42"` or `"32"`.
- News page: amount `7_500_000`? No: `"$5 million"` parses to `5_000_000` assumed AUD, and that is a false positive the rules cannot detect; assert the amount and assert `eligibility_text == ""`, `employer_types_allowed == []`, status ACTIVE (no deadline), for_codes include `"31"`.
- Travel award: amount `3_000`, deadline 2026-08-15, status CLOSED at TODAY, citizenships `["AU", "NZ"]`, career stages include UNDERGRADUATE and GRADUATE_STUDENT, employer types `[UNIVERSITY]`.
- `content_hash` changes when raw_text changes and is stable otherwise; ids are unique across the five fixtures; every produced Opportunity validates (constructing it is the assertion).

Commit message: `feat(normaliser): rule-based row normalisation with per-field provenance`.

---

### Task 5: Pipeline, CLI, SQLite repository, API switch

**Files:** create `backend/normaliser/pipeline.py`, `backend/normaliser/run.py`, `backend/data/sqlite_repository.py`, `backend/tests/test_pipeline.py`, `backend/tests/test_sqlite_repository.py`; modify `backend/data/repository.py` (only `get_repository`) and append to `backend/tests/test_api.py`. Needs Tasks 3 and 4.

**Interfaces:**

```python
# pipeline.py
NORMALISED_TABLE = "normalised_opportunities"

@dataclass
class PipelineStats:
    rows_read: int = 0
    normalised: int = 0
    skipped_unchanged: int = 0
    llm_calls: int = 0
    llm_failures: int = 0

def init_normalised_table(conn: sqlite3.Connection) -> None: ...
def read_crawled_rows(conn: sqlite3.Connection) -> list[CrawledRow]: ...        # WHERE fetch_failed = 0
def load_normalised(conn: sqlite3.Connection) -> list[NormalisedRecord]: ...
def normalise_database(db_path: str | Path, today: date, extractor: Extractor | None = None, force: bool = False) -> PipelineStats: ...

# sqlite_repository.py
class SqliteRepository(OpportunityRepository):
    def __init__(self, db_path: str | Path) -> None: ...   # loads NORMALISED_TABLE once; empty repo if the table is absent

# repository.py, replace get_repository only
def get_repository() -> OpportunityRepository:
    """FMF_DATA_SOURCE=sqlite reads FMF_DB_PATH (default crawler DB_PATH); anything else is the mock set."""
```

Table columns: `id TEXT PRIMARY KEY, url TEXT UNIQUE NOT NULL, content_hash TEXT NOT NULL, opportunity_json TEXT NOT NULL, provenance_json TEXT NOT NULL, used_llm INTEGER NOT NULL DEFAULT 0, normalised_at TEXT NOT NULL`. Store `opportunity.model_dump(mode="json")` as JSON.

`normalise_database` logic: open the connection, `init_normalised_table`, read existing `(url -> content_hash, used_llm)`, then for each crawled row: compute `content_hash(row)`; skip (count `skipped_unchanged`) when `not force` and the stored hash matches and (`used_llm` is true or `extractor is None`); otherwise `normalise_row`, then if `extractor` is given call `extractor.extract(title, url, raw_text)` inside try/except (any exception counts `llm_failures`, logs a warning with `logging`, and keeps the rule-only record), `merge` on success and count `llm_calls`; upsert with `INSERT ... ON CONFLICT(url) DO UPDATE`. `normalised_at` is `datetime.now(timezone.utc).isoformat()`. Return the stats.

`run.py`: `python -m backend.normaliser.run [--db PATH] [--today YYYY-MM-DD] [--no-llm] [--force]`. Default `--db` is `backend.crawler.config.DB_PATH`, default `--today` is `date.today()`. Builds the extractor with `extractor_from_env()` unless `--no-llm`. Prints one line per stat and a final line saying which data source the API will need (`FMF_DATA_SOURCE=sqlite FMF_DB_PATH=<db>`).

`get_repository` keeps `@lru_cache(maxsize=1)`; tests call `get_repository.cache_clear()` after setting environment variables with `monkeypatch.setenv`.

Required tests:

- `test_pipeline.py`: build a temp database with `backend.crawler.storage.init_db(str(tmp_path / "t.db"))` and `save_opportunity(url, fields, source_query, db_path=...)` for the five fixture rows (map fixture fields into the `fields` dict the crawler's `save_opportunity` expects; mark one extra row `fetch_failed` via `mark_fetch_failed` and assert it is not read). Then: `normalise_database(db, TODAY)` reads 5, normalises 5, skips 0; a second run skips 5; `force=True` normalises 5 again; `load_normalised` returns 5 valid records with unique ids; with a `FakeExtractor` the second run over unchanged rows normalises them (because `used_llm` was false) and `llm_calls == 5` and every record has `used_llm`; an extractor whose `extract` raises counts `llm_failures == 5` and still writes rule-only records; the crawler's `opportunities` table is unchanged after the run (row count and one sample row identical).
- `test_sqlite_repository.py`: after `normalise_database`, `SqliteRepository(db).all()` has 5 and `get(id)` works; a database with no normalised table gives an empty repository, not an exception.
- `test_api.py` additions: with `monkeypatch.setenv("FMF_DATA_SOURCE", "sqlite")` and `FMF_DB_PATH` pointing at a normalised temp database, `get_repository.cache_clear()`, then `POST /api/search` with `{"include_closed": true, "limit": 100}` returns `total == 5`; restore by clearing the cache again in a fixture teardown so the existing mock-based tests keep passing. Use a pytest fixture that yields and clears.
- Run `python -m backend.normaliser.run --db <temp> --no-llm --today 2026-09-01` once by hand and paste its output in your report.

Commit message: `feat(normaliser): SQLite pipeline, CLI and repository switch for the API`.

---

### Task 6: Documentation

**Files:** create `docs/adr/ADR-003-normaliser.md`; modify `backend/README.md`.

- ADR-003 in the same table-plus-sections format as `docs/adr/ADR-002-ranking-engine.md`: Decision (rules first, model fills prose fields, own table, repository switch), Status Proposed, Context (crawler stores raw signals, ranker needs structured fields, decision 3 hybrid), Options (rules only, rules plus model, model only), Decision details (the merge policy, the provenance record, the content-hash skip, the env variables, the currency table as an approximation), Consequences (false positives such as a news page's "$5 million" become visible through provenance and are the model's job to correct; bare `$` assumed AUD), Evidence.
- README: change the "Normalising crawler rows" status row to "Prototype built"; add a "Normaliser" section after "Running the API and tests" with: what it does in two sentences, the run command, the environment variables (`FMF_DATA_SOURCE`, `FMF_DB_PATH`, `FMF_LLM_MODEL`, and that `ANTHROPIC_API_KEY` enables the extractor and everything works without it), and one sentence on cost (the extractor runs once per changed page and is skipped for unchanged pages).
- Prose is one line per paragraph or list item, never hard-wrapped.

Commit message: `docs: ADR-003 normaliser and README run instructions`.
