# Jira board snapshot (KAN)

A read-only copy of the team's Jira project KAN, taken 23 October 2026, so the board can be read without an Atlassian login. Jira remains the source of truth: [live board](https://annaseku01.atlassian.net/jira/software/projects/KAN/boards). The client is referred to by role, not by name.

68 work items: 39 Done, 25 To Do, 3 In Review, 1 In Progress.

## KAN-12: Crawler and Discovery

6 of 8 items done.

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-4](#kan-4) | Story | Done | jummana alshimary | Dynamic web crawling/discovery rather than a fixed curated list of funding sites |
| [KAN-9](#kan-9) | Story | Done | jummana alshimary | Back End Team prototype model |
| [KAN-18](#kan-18) | Story | Done | Unassigned | Discover candidate funding pages from a search profile |
| [KAN-19](#kan-19) | Story | Done | Unassigned | Gate every fetch on robots.txt |
| [KAN-20](#kan-20) | Story | Done | Unassigned | Fetch funding pages and extract raw fields |
| [KAN-21](#kan-21) | Story | Done | Unassigned | Re-crawl opportunities once their data goes stale |
| [KAN-22](#kan-22) | Story | In Review | Anna Sekulic | Identify our crawler with a descriptive User-Agent and contact URL |
| [KAN-49](#kan-49) | Task | To Do | Unassigned | Add an automated test for the robots.txt gate |

## KAN-13: Normalisation and LLM Extraction

4 of 4 items done.

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-23](#kan-23) | Story | Done | Unassigned | Parse dates and funding amounts with deterministic rules |
| [KAN-24](#kan-24) | Story | Done | Unassigned | Use Gemini to fill the prose fields rules cannot reach |
| [KAN-25](#kan-25) | Story | Done | Unassigned | Record provenance for every extracted field |
| [KAN-26](#kan-26) | Story | Done | Unassigned | Skip normalisation when a page has not changed |

## KAN-14: Ranking Engine

4 of 5 items done.

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-27](#kan-27) | Story | Done | Unassigned | Score eligibility as four states, never a yes or no |
| [KAN-28](#kan-28) | Story | Done | Unassigned | Score research match, funding value and deadline |
| [KAN-29](#kan-29) | Story | Done | Unassigned | Combine the four scores with configurable weights |
| [KAN-30](#kan-30) | Story | Done | Unassigned | Guard ranking quality with a golden-set eval harness in CI |
| [KAN-31](#kan-31) | Story | To Do | Unassigned | Agree the final ranking weights with the client |

## KAN-15: Data and Persistence

3 of 3 items done.

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-32](#kan-32) | Story | Done | Unassigned | Define the repository seam so the data store can be swapped |
| [KAN-33](#kan-33) | Story | Done | Unassigned | Serve ranked results from Supabase Postgres |
| [KAN-34](#kan-34) | Story | Done | Unassigned | Soft-delete closed opportunities instead of removing them |

## KAN-16: API and Frontend

4 of 6 items done.

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-8](#kan-8) | Story | Done | Andrew Rosen | Front end Demo |
| [KAN-11](#kan-11) | Story | In Review | Unassigned | Agree the API contract between front end and back end |
| [KAN-35](#kan-35) | Story | Done | Unassigned | Serve ranked search results from POST /api/search |
| [KAN-36](#kan-36) | Story | Done | Unassigned | Build the search form with dropdowns matching the backend vocabulary |
| [KAN-37](#kan-37) | Story | Done | Unassigned | Integrate the frontend with the deployed API |
| [KAN-38](#kan-38) | Story | To Do | Unassigned | Show why each opportunity ranked where it did |

## KAN-17: Project Governance and Delivery

8 of 21 items done.

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-5](#kan-5) | Task | Done | Sophia Kondos | Create User Stories |
| [KAN-6](#kan-6) | Task | Done | Anna Sekulic | Prepare for Client Meeting: Finalise a list of questions and what we want to present potentially - decisions and trade offs |
| [KAN-7](#kan-7) | Task | Done | Paige Varney | Motivational Models |
| [KAN-10](#kan-10) | Task | Done | Unassigned | Email client to confirm complete user cases and requirements |
| [KAN-39](#kan-39) | Task | To Do | Unassigned | Complete the terms-of-service and legal review |
| [KAN-40](#kan-40) | Task | Done | Unassigned | Set up CI and CD pipelines with branch protection |
| [KAN-41](#kan-41) | Task | Done | Unassigned | Produce the system design and UML diagram set |
| [KAN-42](#kan-42) | Task | To Do | Unassigned | Establish a regular client meeting cadence with the client |
| [KAN-43](#kan-43) | Task | Done | Anna Sekulic | Document coding standards, testing strategy and deployment in Confluence |
| [KAN-44](#kan-44) | Task | To Do | Unassigned | Publish ADR-002, ADR-003 and ADR-004 to Confluence |
| [KAN-45](#kan-45) | Task | To Do | Unassigned | Fix the use case diagram (Week 9 tutor feedback) |
| [KAN-46](#kan-46) | Task | To Do | Unassigned | Review the draft user stories and acceptance criteria |
| [KAN-47](#kan-47) | Task | To Do | Unassigned | Estimate user stories with planning poker and turn on Jira estimation |
| [KAN-48](#kan-48) | Task | To Do | Unassigned | Run acceptance test cases TC07 to TC09 and record the Sprint 3 test report |
| [KAN-50](#kan-50) | Task | Done | Anna Sekulic | Add a code coverage report to Backend CI |
| [KAN-51](#kan-51) | Task | To Do | Unassigned | Log every client contact since 20/08 on the Client Communication Log |
| [KAN-52](#kan-52) | Task | To Do | Unassigned | Close Sprint 3: client review, retrospective and v0.3.0 release (28/09) |
| [KAN-53](#kan-53) | Task | To Do | Unassigned | Everyone: add your GenAI use to the GenAI Usage Log |
| [KAN-54](#kan-54) | Task | To Do | Unassigned | Choose a repository licence after checking the IP agreement |
| [KAN-55](#kan-55) | Task | To Do | Unassigned | Write one or two researcher personas |
| [KAN-56](#kan-56) | Task | To Do | Unassigned | Finish the Confluence tidy-up (folder moves the API cannot do) |

## Not under an epic

| Key | Type | Status | Assignee | Summary |
| --- | --- | --- | --- | --- |
| [KAN-57](#kan-57) | Feature | To Do | Unassigned | Problem: clicking search changes website format. |
| [KAN-58](#kan-58) | Task | Done | Anna Sekulic | Add Playwright end-to-end tests and cover untested backend and frontend modules |
| [KAN-59](#kan-59) | Task | Done | Anna Sekulic | Fix "? Any" in filter dropdowns (regression of #23) |
| [KAN-60](#kan-60) | Task | Done | Anna Sekulic | Filter options: FoR divisions, citizenship, career stage and funding labels |
| [KAN-61](#kan-61) | Feature | To Do | Unassigned | Implement backend API integration |
| [KAN-62](#kan-62) | Feature | To Do | Unassigned | Configure API environment variables |
| [KAN-63](#kan-63) | Feature | In Review | Paige Varney | Redesign funding result cards |
| [KAN-64](#kan-64) | Task | In Progress | Anna Sekulic | Retire the illustrative mock data set and schedule the crawl, normalise and publish pipeline |
| [KAN-65](#kan-65) | Task | Done | Anna Sekulic | Tailor results to Australian opportunities and fix card summaries showing menu text |
| [KAN-66](#kan-66) | Task | Done | Anna Sekulic | Foreign funders show 100% eligible once any filter is applied |
| [KAN-67](#kan-67) | Task | Done | Anna Sekulic | AI summaries on every card, and show Gemini quota problems on screen |
| [KAN-68](#kan-68) | Task | Done | Anna Sekulic | Stale menu-text summaries on 468 live cards; rule summaries cut proper nouns ("(NESP) is...") |
| [KAN-69](#kan-69) | Task | Done | Anna Sekulic | Move the normaliser's LLM extractor from Gemini to OpenRouter with a small open-weight model |
| [KAN-70](#kan-70) | Task | Done | Anna Sekulic | Cap the LLM reply length so a runaway generation cannot stall the crawl |
| [KAN-71](#kan-71) | Task | Done | Anna Sekulic | Fetch sites and call the LLM in parallel during a refresh |

## Work item details

### KAN-4

**Dynamic web crawling/discovery rather than a fixed curated list of funding sites**

Story · Done · jummana alshimary · epic KAN-12 · labels: US07, backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-4)

### KAN-5

**Create User Stories**

Task · Done · Sophia Kondos · epic KAN-17 · labels: docs, requirements · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-5)

### KAN-6

**Prepare for Client Meeting: Finalise a list of questions and what we want to present potentially - decisions and trade offs**

Task · Done · Anna Sekulic · epic KAN-17 · labels: client · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-6)

### KAN-7

**Motivational Models**

Task · Done · Paige Varney · epic KAN-17 · labels: docs, requirements · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-7)

### KAN-8

**Front end Demo**

Story · Done · Andrew Rosen · epic KAN-16 · labels: frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-8)

### KAN-9

**Back End Team prototype model**

Story · Done · jummana alshimary · epic KAN-12 · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-9)

### KAN-10

**Email client to confirm complete user cases and requirements**

Task · Done · Unassigned · epic KAN-17 · labels: client · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-10)

### KAN-11

**Agree the API contract between front end and back end**

Story · In Review · Unassigned · epic KAN-16 · labels: backend, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-11)

### KAN-12

**Crawler and Discovery**

Epic · To Do · Unassigned · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-12)

Finding funding pages and fetching them politely.

Covers URL discovery from search profiles, the robots.txt permission gate, page fetching and field extraction, and the scheduler that re-crawls stale records.

**Code:** `backend/crawler/` — `discoverURL.py`, `queryBuilder.py`, `crawler.py`, `extract.py`, `robotCheck.py`, `scheduler.py`, `storage.py`, `config.py`

**Related:** [Architecture Overview](../confluence/architecture-overview-find-me-funding.md) · [Legal, Ethics and Data Handling](../confluence/legal-ethics-and-data-handling.md)

### KAN-13

**Normalisation and LLM Extraction**

Epic · To Do · Unassigned · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-13)

Turning a raw funding page into a structured, comparable record.

Deterministic rules run first and win on dates and amounts; the LLM fills only the prose-derived fields the rules cannot reach. Every field carries provenance saying which stage set it.

**Code:** `backend/normaliser/` — `pipeline.py`, `rules.py`, `llm.py`, `parsers.py`, `lexicon.py`, `models.py`, `run.py`

**Related:** ADR-003 (normaliser), currently in the repo at `docs/adr/`

### KAN-14

**Ranking Engine**

Epic · To Do · Unassigned · labels: backend, ranking · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-14)

Ordering opportunities by how attractive they are to a given researcher.

Four criteria are scored independently — eligibility, research match, funding value, deadline — then combined with configurable weights. All four scores travel with the result so the UI can show why something ranked where it did.

**Code:** `backend/ranking/` — `ranker.py`, `eligibility.py`, `research_match.py`, `funding_value.py`, `deadline.py`, `weights.py`, `models.py`

**Related:** ADR-002 (ranking engine) · [Ranking activity diagram](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/diagrams/activity-ranking.drawio)

### KAN-15

**Data and Persistence**

Epic · To Do · Unassigned · labels: backend, data · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-15)

Storing opportunities behind one interface so the store can change without the search path noticing.

`OpportunityRepository` exposes only `all()` and `get()`. The mock fixture, SQLite and Postgres are interchangeable behind it — this is the architectural seam the system is built around.

**Code:** `backend/data/` — `repository.py`, `sqlite_repository.py`, `postgres_repository.py`, `publish.py`

**Related:** [ER diagram](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/diagrams/er-diagram.drawio)

### KAN-16

**API and Frontend**

Epic · To Do · Unassigned · labels: backend, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-16)

The search experience a researcher actually uses, and the contract between the two halves of the team.

FastAPI serves ranked results; the React SPA collects search criteria and renders them.

**Code:** `backend/api/` — `main.py`, `schemas.py` · `frontend/src/` — `pages/`, `components/`, `services/fundingService.ts`

**Related:** [API Contract](../confluence/api-contract.md) · [Search sequence diagram](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/diagrams/sequence-search-funding.drawio)

### KAN-17

**Project Governance and Delivery**

Epic · To Do · Unassigned · labels: client, docs · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-17)

Everything that is not product code: client liaison, requirements, documentation, CI/CD, and the subject deliverables.

**Related:** [Web Crawler — Project Home](../confluence/web-crawler-project-home.md) · [Communication Plan](../confluence/communication-plan.md) · [Legal, Ethics and Data Handling](../confluence/legal-ethics-and-data-handling.md)

### KAN-18

**Discover candidate funding pages from a search profile**

Story · Done · Unassigned · epic KAN-12 · labels: US07, backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-18)

As the system, I want to build search queries from a researcher profile and turn them into candidate URLs, so that we find funding pages without maintaining a hand-curated list of sites.

**Acceptance criteria**

* Given a search profile, when discovery runs, then queries are built from the same enum vocabulary the frontend dropdowns use
* Given a set of queries, when discovery runs, then candidate URLs are returned for fetching
* Given a URL already in the store, when discovery runs again, then it is not duplicated

**Implementation:** `backend/crawler/discoverURL.py`, `backend/crawler/queryBuilder.py`

### KAN-19

**Gate every fetch on robots.txt**

Story · Done · Unassigned · epic KAN-12 · labels: US08, backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-19)

As a funder whose site we crawl, I want my robots.txt honoured, so that our crawler does not fetch pages I have asked automated clients to leave alone.

**Acceptance criteria**

* Given any candidate URL, when the crawler is about to fetch it, then `is_allowed(url)` is checked first
* Given robots.txt disallows the path, when the check runs, then the page is never fetched
* Given robots.txt is unreachable, when the check runs, then the outcome is recorded rather than silently treated as permission

**Implementation:** `backend/crawler/robotCheck.py`

**Related:** [Legal, Ethics and Data Handling](../confluence/legal-ethics-and-data-handling.md)

### KAN-20

**Fetch funding pages and extract raw fields**

Story · Done · Unassigned · epic KAN-12 · labels: US05, backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-20)

As the system, I want to fetch an allowed page and pull out the raw text and obvious fields, so that the normaliser has something to work with.

**Acceptance criteria**

* Given an allowed URL, when the crawler fetches it, then a row is written to the `opportunities` table keyed on url
* Given a page is fetched, when extraction runs, then title, raw text, deadline, funding amount and eligibility snippet are captured as raw strings
* Given a fetch fails, when the crawler handles it, then `fetch_failed` is incremented rather than the row being lost

**Implementation:** `backend/crawler/crawler.py`, `backend/crawler/extract.py`, `backend/crawler/storage.py`

### KAN-21

**Re-crawl opportunities once their data goes stale**

Story · Done · Unassigned · epic KAN-12 · labels: US06, backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-21)

As a researcher, I want the index kept current, so that a deadline I see has not already moved.

**Acceptance criteria**

* Given a stored opportunity older than `STALE_AFTER_DAYS`, when the scheduler polls, then that URL is re-fetched and re-extracted
* Given discovery has run before for a search profile, when the scheduler polls, then full discovery is periodically re-run so new pages are picked up
* Given the scheduler is running, when a user searches, then no crawl is triggered by that search

**Implementation:** `backend/crawler/scheduler.py`, `backend/crawler/config.py`

**Note:** the current implementation is a simple loop, which is adequate for the project. A production deployment would use cron or Celery beat — worth recording as a known limitation.

### KAN-22

**Identify our crawler with a descriptive User-Agent and contact URL**

Story · In Review · Anna Sekulic · epic KAN-12 · labels: US08, backend, crawler, tech-debt · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-22)

As a funder whose site we crawl, I want to know who is crawling me and how to reach them, so that I can contact the team rather than simply blocking the traffic.

**Acceptance criteria**

* Given any outbound fetch, when the request is sent, then the User-Agent names the project and carries a contact URL
* Given the User-Agent is set, when it is reviewed, then it matches what the Legal, Ethics and Data Handling page states

**Why:** raised as an open question during the terms-of-service review. Standard practice for any crawler operating against third-party sites.

**Related:** [Legal, Ethics and Data Handling](../confluence/legal-ethics-and-data-handling.md)

### KAN-23

**Parse dates and funding amounts with deterministic rules**

Story · Done · Unassigned · epic KAN-13 · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-23)

As the system, I want dates and amounts parsed by rules rather than by the model, so that the numbers a researcher acts on are reproducible and not subject to model drift.

**Acceptance criteria**

* Given a raw deadline string, when the parser runs, then a date is produced or the field is left empty — never guessed
* Given a raw funding amount, when the parser runs, then an AUD integer is produced where one can be read confidently
* Given both rules and the LLM produce a value for a date or amount, when they are merged, then the rule value wins

**Implementation:** `backend/normaliser/rules.py`, `parsers.py`, `lexicon.py`

### KAN-24

**Use Gemini to fill the prose fields rules cannot reach**

Story · Done · Unassigned · epic KAN-13 · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-24)

As the system, I want the model to read the wording a funder uses, so that funder name, summary and eligibility paraphrase are populated without hand-writing a parser per site.

**Acceptance criteria**

* Given a fetched page, when extraction runs, then only the listed prose fields may be set by the model
* Given the model returns an empty value, when merging, then the rule-built record keeps its own value
* Given the provider needs to change, when it does, then only the `Extractor` implementation changes — the pipeline is provider-agnostic

**Implementation:** `backend/normaliser/llm.py` — `gemini-2.5-flash`, chosen for the free tier rather than peak quality; overridable via `FMF_LLM_MODEL`

### KAN-25

**Record provenance for every extracted field**

Story · Done · Unassigned · epic KAN-13 · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-25)

As a developer debugging a wrong result, I want to know which stage set each field, so that I can tell a bad rule from a bad model output without re-running the pipeline.

**Acceptance criteria**

* Given a normalised record, when it is stored, then every Opportunity field maps to `rule`, `llm` or `missing`
* Given provenance is stored, when the record is read back, then the audit trail survives the round trip through JSONB

**Implementation:** `backend/normaliser/models.py` — `NormalisedRecord.provenance`; stored in `provenance_json`

### KAN-26

**Skip normalisation when a page has not changed**

Story · Done · Unassigned · epic KAN-13 · labels: backend, crawler · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-26)

As the team, I want unchanged pages to cost nothing beyond the fetch, so that re-crawling does not burn LLM quota on identical content.

**Acceptance criteria**

* Given a re-crawled page, when its SHA-256 of title plus raw text matches the stored `content_hash`, then normalisation is skipped entirely
* Given the hash differs, when the pipeline runs, then the record is re-normalised and the hash updated

**Implementation:** `backend/normaliser/models.py` — `content_hash`

### KAN-27

**Score eligibility as four states, never a yes or no**

Story · Done · Unassigned · epic KAN-14 · labels: US02, backend, ranking · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-27)

As a researcher, I want to see when I am _possibly_ eligible rather than being filtered out, so that I do not miss a scheme because the funder's wording was ambiguous.

**Acceptance criteria**

* Given an opportunity and a search, when eligibility is scored, then the result is one of eligible, potentially eligible, unknown, likely ineligible
* Given an empty restriction list on an opportunity, when scoring runs, then it is read as "no restriction stated", not as "nobody qualifies"
* Given a score is produced, when it is returned, then it carries reasons explaining the verdict

**Implementation:** `backend/ranking/eligibility.py`. Implements Confluence decision 4.

### KAN-28

**Score research match, funding value and deadline**

Story · Done · Unassigned · epic KAN-14 · labels: US04, backend, ranking · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-28)

As a researcher, I want opportunities rated on fit, money and urgency, so that the top of the list is worth my time.

**Acceptance criteria**

* Given FoR codes, ToA codes and a research description, when research match is scored, then a high/medium/low level is produced with reasons
* Given an amount, when funding value is scored, then it falls into one of the defined bands, or unknown
* Given a deadline and today's date, when the deadline is scored, then it falls into one of the client's named bands: over 60 days, 60–30, 30–15, under 15, closed, unknown

**Implementation:** `backend/ranking/research_match.py`, `funding_value.py`, `deadline.py`

### KAN-29

**Combine the four scores with configurable weights**

Story · Done · Unassigned · epic KAN-14 · labels: US02, backend, ranking · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-29)

As the team, I want the weighting to be a parameter rather than hard-coded, so that we can tune ranking after client feedback without changing the scorers.

**Acceptance criteria**

* Given the four scores, when they are combined, then the overall is the weighted sum divided by the weight total, rounded to 4 places
* Given a request supplies a partial weight override, when weights are resolved, then it merges onto the defaults
* Given all weights are zero, when validation runs, then it is rejected rather than dividing by zero
* Given results are returned, when the UI reads them, then all four criterion scores are still present alongside the overall

**Implementation:** `backend/ranking/weights.py`, `ranker.py`. Defaults: eligibility 0.4, research match 0.3, funding value 0.15, deadline 0.15. Implements Confluence decision 5.

### KAN-30

**Guard ranking quality with a golden-set eval harness in CI**

Story · Done · Unassigned · epic KAN-14 · labels: backend, ranking, testing · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-30)

As the team, I want ranking regressions to fail the build, so that a weight tweak cannot quietly make results worse.

**Acceptance criteria**

* Given a golden set of expected orderings, when `run_evals` executes, then it reports pass or fail per case
* Given the evals fail, when CI runs, then the build fails
* Given the evals run, when they do, then they exercise the same ranking path the API uses, not a copy

**Implementation:** `backend/evals/run_evals.py`, `backend/evals/golden.json`; wired into `backend-ci.yml`

### KAN-31

**Agree the final ranking weights with the client**

Story · To Do · Unassigned · epic KAN-14 · labels: client, ranking · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-31)

As the team, I want the weighting signed off rather than assumed, so that the ordering reflects what the Research Office actually values.

**Acceptance criteria**

* Given the current defaults, when they are reviewed with the client, then each weight is either confirmed or changed with a recorded reason
* Given the weights are agreed, when they are set, then the decision is written up as an ADR
* Given the weights change, when CI runs, then the golden set is updated to match the agreed intent

**Why this is open:** the current values are placeholders that put eligibility first because the client called it the top priority. The relative weighting has never been formally agreed — see `docs/ranking-discussion-points.md`.

### KAN-32

**Define the repository seam so the data store can be swapped**

Story · Done · Unassigned · epic KAN-15 · labels: backend, data · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-32)

As a developer, I want the search path to depend on one small interface, so that changing where data lives does not ripple through the codebase.

**Acceptance criteria**

* Given the API needs opportunities, when it asks, then it calls only `all()` and `get()`
* Given a new backing store is introduced, when it is added, then only one class changes
* Given the mock fixture is in use, when it is swapped for a database, then no API or ranking code changes

**Implementation:** `backend/data/repository.py`. Implements Confluence decision 7.

### KAN-33

**Serve ranked results from Supabase Postgres**

Story · Done · Unassigned · epic KAN-15 · labels: backend, data · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-33)

As a researcher, I want to search real crawled data rather than a fixture, so that the results mean something.

**Acceptance criteria**

* Given the deployed API, when `FMF_DATA_SOURCE=postgres`, then results come from Supabase rather than `mock_opportunities.json`
* Given a record is written twice, when the upsert runs, then `ON CONFLICT` updates rather than duplicating
* Given an Opportunity is stored, when it is read back, then the JSONB round trip preserves every field

**Implementation:** `backend/data/postgres_repository.py`, `publish.py`. Merged in PR #19.

**Note:** `FMF_DATABASE_URL` must be the Supavisor session-mode pooler URL — Render is IPv4-only and Supabase's direct string resolves to IPv6.

### KAN-34

**Soft-delete closed opportunities instead of removing them**

Story · Done · Unassigned · epic KAN-15 · labels: US06, backend, data · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-34)

As the team, I want a passed deadline to hide an opportunity rather than destroy it, so that we keep the history and can show closed schemes on request.

**Acceptance criteria**

* Given a deadline has passed, when the record is updated, then `status` becomes closed and the row is retained
* Given a search without `include_closed`, when ranking runs, then closed opportunities are filtered at read time
* Given a search with `include_closed`, when ranking runs, then they are returned

**Implementation:** `backend/ranking/ranker.py`, `OpportunityStatus`. Implements Confluence decision 9.

### KAN-35

**Serve ranked search results from POST /api/search**

Story · Done · Unassigned · epic KAN-16 · labels: US01, US03, backend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-35)

As the frontend, I want one endpoint that takes search criteria and returns a ranked page, so that the UI holds no ranking logic.

**Acceptance criteria**

* Given a SearchRequest, when POST /api/search is called, then a ranked, paged SearchResponse is returned with the weights used
* Given `limit` and `offset`, when paging, then the same ranked ordering is returned across pages
* Given the service is running, when GET /api/health is called, then status and version are returned
* Given the deployed frontend origin, when it calls the API, then CORS allows it

**Implementation:** `backend/api/main.py`, `schemas.py`. Interactive docs at `/docs` are the authoritative contract.

### KAN-36

**Build the search form with dropdowns matching the backend vocabulary**

Story · Done · Unassigned · epic KAN-16 · labels: US01, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-36)

As a researcher, I want to describe myself with a few dropdowns rather than free text, so that the system can match me accurately without me guessing its vocabulary.

**Acceptance criteria**

* Given the home page, when it loads, then dropdowns offer employer type, career stage and funding type
* Given a dropdown option is selected, when the request is sent, then its value matches the backend enum exactly
* Given the form is submitted, when the API responds, then the user is taken to the results page

**Implementation:** `frontend/src/pages/Home`, `components/Dropdown`. Merged in PR #22.

### KAN-37

**Integrate the frontend with the deployed API**

Story · Done · Unassigned · epic KAN-16 · labels: US03, backend, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-37)

As a researcher, I want the site to show real ranked results, so that the prototype does something rather than demonstrating a mock.

**Acceptance criteria**

* Given the deployed frontend, when a search is submitted, then it calls the deployed API base URL
* Given results return, when the page renders, then each result shows title, funder, amount and deadline
* Given the API is unreachable, when a search is submitted, then the user sees a clear error rather than a blank page

**Implementation:** `frontend/src/services/fundingService.ts`, `pages/Results`, `components/Result`

### KAN-38

**Show why each opportunity ranked where it did**

Story · To Do · Unassigned · epic KAN-16 · labels: US04, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-38)

As a researcher, I want to see the four criterion scores behind a result, so that I can judge whether the ranking agrees with my own view rather than trusting an unexplained number.

**Acceptance criteria**

* Given a result, when it is displayed, then the eligibility, research match, funding value and deadline ratings are visible
* Given eligibility is "potentially eligible" or "unknown", when it is shown, then it is visually distinct from "eligible"
* Given a criterion has reasons, when the user expands it, then the reasons are shown

**Why this matters:** the backend already returns all four scores with reasons — Confluence decision 5 exists precisely so the UI can do this. Until the frontend uses them, the design decision is invisible to a user.

### KAN-39

**Complete the terms-of-service and legal review**

Task · To Do · Unassigned · epic KAN-17 · labels: client, docs · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-39)

Requested directly by our supervisor. robots.txt is honoured in code, but we have never read the website terms of the sites we crawl, and several policy questions are unanswered.

**Acceptance criteria**

* Given the target funder list is confirmed with the client, when their terms are reviewed, then each is recorded as permitting or restricting automated access
* Given the review is done, when it is written up, then attribution, data retention and LLM data-flow positions are decided and recorded
* Given decisions are made, when they are recorded, then they become an ADR rather than living only on the wiki page

**Open questions:** seven are listed on the page below, unanswered.

**Related:** [Legal, Ethics and Data Handling](../confluence/legal-ethics-and-data-handling.md)

### KAN-40

**Set up CI and CD pipelines with branch protection**

Task · Done · Unassigned · epic KAN-17 · labels: backend, frontend, testing · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-40)

**Acceptance criteria**

* Given a pull request, when CI runs, then ruff lint and format, pytest on Python 3.11/3.12/3.13 against a real Postgres service container, the ranking evals, and a Docker build check all run
* Given a frontend pull request, when CI runs, then ESLint, Vitest and a TypeScript build run
* Given checks fail, when a merge to `main` is attempted, then it is blocked by required status checks
* Given `main` passes, when CD runs, then the backend deploys to Render and the frontend to GitHub Pages

**Implementation:** `.github/workflows/` — `backend-ci.yml`, `frontend-ci.yml`, `backend-cd.yml`, `frontend-cd.yml`

### KAN-41

**Produce the system design and UML diagram set**

Task · Done · Unassigned · epic KAN-17 · labels: architecture, docs · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-41)

Requested by our supervisor: "one overall system design diagram (better documentation)".

**Acceptance criteria**

* Given the diagrams are needed, when they are produced, then editable draw.io sources live in the repository, not only exported images
* Given a diagram changes, when it is updated, then the source is edited rather than the picture redrawn
* Given the architecture page is read, when a diagram is referenced, then it renders on the page

**Delivered:** eleven diagrams in `docs/diagrams/` — high level architecture, layered system architecture, component, deployment, ER, domain class, two sequence diagrams, activity, state, and use case.

**Related:** [Architecture Overview](../confluence/architecture-overview-find-me-funding.md)

### KAN-42

**Establish a regular client meeting cadence with the client**

Task · To Do · Unassigned · epic KAN-17 · labels: client · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-42)

Requested by our supervisor: "meet with the client more".

**Acceptance criteria**

* Given the team's availability, when a cadence is agreed with the client, then a recurring slot is in the calendar
* Given a meeting happens, when it ends, then notes are published to Confluence and logged on the Client Communication Log
* Given the log exists, when it is reviewed, then every touchpoint since project start is recorded

**Current state:** only the 20 August check-in is documented. [KAN-10](https://annaseku01.atlassian.net/browse/KAN-10) suggests a follow-up email was planned but is still To Do.

### KAN-43

**Document coding standards, testing strategy and deployment in Confluence**

Task · Done · Anna Sekulic · epic KAN-17 · labels: docs · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-43)

Three items on the COMP30022 progress checklist currently have no Confluence page to link, despite the practice existing in the repository.

**Acceptance criteria**

* Given the Coding checklist item, when it is answered, then a page documents ruff, ESLint, TypeScript strict, the branching strategy and code review expectations
* Given the Testing checklist item, when it is answered, then a page documents the test strategy, the 18 backend test modules, Vitest, and the golden-set eval methodology
* Given the Deployment checklist item, when it is answered, then a page documents the four pipelines, environments, secrets handling and the Render/Supabase setup
* Given each page exists, when the checklist is filled in, then each item has a single canonical link

**Why:** the work is done and enforced in CI — only the documentation is missing.

### KAN-44

**Publish ADR-002, ADR-003 and ADR-004 to Confluence**

Task · To Do · Unassigned · epic KAN-17 · labels: architecture, docs · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-44)

Two architecture decisions exist only in the repository, so anyone reading Confluence cannot see them. ADR-001 is on the wiki but is a pros-and-cons table rather than an ADR.

**Acceptance criteria**

* Given `docs/adr/ADR-002-ranking-engine.md` and `ADR-003-normaliser.md`, when they are published, then each has a Confluence page
* Given [ADR-001](../confluence/adr-001-technology-decisions.md), when it is rewritten, then it carries Status, Date, Context, Decision, Alternatives Considered and Consequences — keeping the existing comparison table as the Alternatives section
* Given hosting and persistence were chosen, when ADR-004 is written, then Render and Supabase Postgres are recorded with the reasoning, including why Render was rejected as the database host

**Known inconsistency to settle first:** `render.yaml` cites `docs/adr/ADR-003-deployment-architecture.md`, but the file on disk is `ADR-003-normaliser.md`. One of the two is wrong.

### KAN-45

**Fix the use case diagram (Week 9 tutor feedback)**

Task · To Do · Unassigned · epic KAN-17 · labels: requirements, tutor-feedback · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-45)

Week 9 tutor feedback: the use case diagram is incorrect; check it against the notation taught in SMD (actors outside the system boundary, use cases as verbs, include/extend used correctly).

**Done when:** `docs/09-architectural-design/diagrams/use-case-diagram.drawio` is corrected, the PNG re-exported, and the [Use Case Diagram](../confluence/use-case-diagram.md) page updated. Each use case should map to a user story (US01 to US10).

### KAN-46

**Review the draft user stories and acceptance criteria**

Task · To Do · Unassigned · epic KAN-17 · labels: requirements, tutor-feedback · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-46)

[User Stories and Acceptance Criteria](../confluence/user-stories-and-acceptance-criteria.md) was drafted on 24/09 from the requirements (FR-01 to FR-19) and the existing Jira stories, so each story has an ID (US01 to US10) that Jira cards (labelled `US01` etc.) and test cases can reference. This answers the Week 9 feedback that Jira tasks were hard to connect to user stories.

Check it against the original [User Story Board](../confluence/user-story-board-original-2408.md) and correct anything that drifted.

**Done when:** the page's Draft banner is removed and the stories are ready to send to the client for sign-off (KAN-10).

### KAN-47

**Estimate user stories with planning poker and turn on Jira estimation**

Task · To Do · Unassigned · epic KAN-17 · labels: agile, tutor-feedback · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-47)

Week 9 tutor feedback: estimate the size or effort of user stories. The Week 2 lecture suggests Fibonacci points and planning poker in the workshop.

Draft Fibonacci estimates are on [User Stories and Acceptance Criteria](../confluence/user-stories-and-acceptance-criteria.md), marked draft.

1. Run planning poker on each story at the next workshop (for example planningpokeronline.com) and replace the draft numbers.
2. Turn on estimation for the KAN project: Project settings, Features, Estimation (a project admin has to do this; the field does not exist yet).
3. Copy the agreed points onto the open stories and tasks.
4. From Sprint 3's review on, record planned vs completed points so velocity is visible.

### KAN-48

**Run acceptance test cases TC07 to TC09 and record the Sprint 3 test report**

Task · To Do · Unassigned · epic KAN-17 · labels: testing · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-48)

The Week 7 lecture requires test reports as well as a plan. Test cases are on [Test Cases and Reports](../confluence/test-cases-and-reports.md).

TC07 (discovery beyond seed list), TC08 (robots.txt gate) and TC09 (end-to-end on the live site) are manual. Run them before the Sprint 3 review, by someone other than the author of the code, and fill in the test report row: automated suite on main, acceptance results per case, bugs opened and closed.

### KAN-49

**Add an automated test for the robots.txt gate**

Task · To Do · Unassigned · epic KAN-12 · labels: US08, crawler, testing · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-49)

US08 AC1 (a URL disallowed by robots.txt is never fetched) is only covered by the manual test TC08; `backend/tests/` has no crawler tests. Add a test for `backend/crawler/robotCheck.py` with a fake robots.txt: disallowed path is rejected, allowed path passes, unreachable robots.txt is recorded rather than treated as permission (KAN-19's third criterion).

Note `crawler/` is currently excluded from ruff; check with Jummana before adding tests next to her rewrite.

### KAN-50

**Add a code coverage report to Backend CI**

Task · Done · Anna Sekulic · epic KAN-17 · labels: ci, testing · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-50)

The Week 7 testing lecture uses code coverage as the measure of how thorough a test plan is (function, statement, branch, line). We do not measure it yet. Add `pytest-cov` to `backend/requirements-dev.txt`, run `pytest --cov=backend` in the Backend CI test job, and publish the summary to the job output. Record the baseline in the Sprint 3 test report. Do not add a threshold that fails CI until the team agrees one.

### KAN-51

**Log every client contact since 20/08 on the Client Communication Log**

Task · To Do · Unassigned · epic KAN-17 · labels: client · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-51)

[Client Communication Log](../confluence/client-communication-log.md) only has the 20/08 meeting. Add every email, meeting and demo with the client since then (including the Sprint 2 review demo if it went ahead), with the outcome and the Jira card each produced. The Communication Plan and the Sprint 3 success metrics both depend on this page, and it is the evidence for Progress Checklist item 5.

### KAN-52

**Close Sprint 3: client review, retrospective and v0.3.0 release (28/09)**

Task · To Do · Unassigned · epic KAN-17 · labels: agile · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-52)

1. Sprint 3 review with the client (product): demo the integrated prototype, capture feedback on the Client Communication Log.
2. Sprint 3 retrospective (process): what we achieved, what we did not, what went well, what to improve. Carry actions into Sprint 4.
3. Tag the release: `gh release create v0.3.0 --target main --title "Sprint 3" --generate-notes` (see `docs/12-deployment/README.md`).
4. Link all three from [1. Agile Ceremonies](../confluence/README.md).

### KAN-53

**Everyone: add your GenAI use to the GenAI Usage Log**

Task · To Do · Unassigned · epic KAN-17 · labels: genai · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-53)

The Week 1 lecture: GenAI use is allowed but must be transparent and documented (summaries, code, test plans), and it will be discussed in the project reviews. [GenAI Usage Log](../confluence/genai-usage-log.md) is back-filled from git history for Anna's and Jummana's Claude-assisted commits. Each team member adds a row for any other tool used on project work (ChatGPT, Copilot, Figma AI and so on). From now on, answer the GenAI section in every PR.

### KAN-54

**Choose a repository licence after checking the IP agreement**

Task · To Do · Unassigned · epic KAN-17 · labels: coding · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-54)

The Week 7 lecture lists licensing as part of initial repository setup, and the repo has no LICENSE. The right licence depends on the project's IP agreement with the client and the University, so check that first (ask Chris or Leon if unclear), then add the LICENSE file in a PR.

### KAN-55

**Write one or two researcher personas**

Task · To Do · Unassigned · epic KAN-17 · labels: requirements · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-55)

The Week 3 lecture recommends personas alongside user stories and the motivational model. Write one or two (for example an early-career health researcher who is a permanent resident, and a senior academic chasing large equipment grants) and add them under [7. Requirements](../confluence/7-requirements.md). Use them in the UX test and the acceptance test profiles.

### KAN-56

**Finish the Confluence tidy-up (folder moves the API cannot do)**

Task · To Do · Unassigned · epic KAN-17 · labels: docs · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-56)

The space was reorganised on 24/09 into the 12 Progress Checklist sections (index on the space home). Folders cannot be moved, renamed or deleted through the API, so these are manual (drag in the sidebar):

1. Drag the three sprint folders under **1. Agile Ceremonies** and rename them "Sprint 1 (17/08 to 24/08)", "Sprint 2 (24/08 to 14/09)", "Sprint 3 (14/09 to 28/09)".
2. Drag **Web Crawler: System Design Brainstorm** (too large to move by API) under **9. Architectural Design**.
3. Delete the now-empty folders: 0. Project Information, 1. Requirements, 1a. Additional Features, 2. Architectural Design Records, - Meeting Notes.
4. Archive the empty stubs: "Sprint 2 - Planning Document" (blank template), "🤖 Crawler & LLM", "📚 Reference & Research".
5. Optional: rename "🏠 Web Crawler — Project Home" to "Progress Checklist" so its 12 children read as one section.
6. Optional: add a Bug issue type to KAN (Project settings, Issue types) so bugs stop being Tasks labelled `bug`.

### KAN-57

**Problem: clicking search changes website format.**

Feature · To Do · Unassigned · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-57)

### KAN-58

**Add Playwright end-to-end tests and cover untested backend and frontend modules**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-58)

## Why

Unit tests cover ranking, the normaliser, the API and both repositories, but nothing tests the full search flow a researcher uses: the real UI calling the real API and showing ranked results. A few modules also have no tests at all.

## Scope

* Playwright end-to-end suite in `frontend/e2e/`: the browser loads the site, submits a search, and the results page shows ranked opportunities served by a local FastAPI on the mock data set. Runs as a new job in Frontend CI.
* Unit tests for `backend/data/publish.py`, `backend/normaliser/run.py` and the `Navbar` component.
* How to run every suite: `docs/11-testing/README.md` (the test plan already links to it).

Out of scope: the crawler package (Jummana's, tracked separately in KAN-49).

## Done when

* The e2e job runs on every PR and fails if the search flow breaks.
* The new unit tests run in the existing Backend CI and Frontend CI jobs.
* Confluence page 11. Testing reflects the new suites.

Coverage reporting is KAN-50; both ship in the same PR.

### KAN-59

**Fix "? Any" in filter dropdowns (regression of #23)**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-59)

Every filter dropdown's blank option reads "Field of Research ? Any" on the live site instead of "Field of Research – Any".

Root cause: PR #23 replaced the corrupted "?" byte with an en dash, but merge commit 1d77ecf (part of PR #30) resolved Dropdown.tsx in favour of the corrupted line. No test covered the option text, so CI stayed green.

Fix: restore the en dash and add a regression test in Dropdown.test.tsx.

Rest of the app was checked end to end (local and live Pages + Render API): search, results, paging and deep links all work.

### KAN-60

**Filter options: FoR divisions, citizenship, career stage and funding labels**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-60)

Replace the 3 placeholder Field of Research options in frontend/src/data/filterOptions.ts with the full 23 ANZSRC 2020 FoR divisions (2-digit codes 30-52), taken from the ABS anzsrc2020_for.xlsx. The ranker scores an exact code match (full) and a same-division match (half), and opportunities carry division codes, so division picks score as exact matches.

### KAN-61

**Implement backend API integration**

Feature · To Do · Unassigned · labels: backend, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-61)

Connect the frontend to the backend search API and map UI filter values to the backend request format. Tasks

* Create \`frontend/src/services/fundingService.ts\`.
* Implement \`fetchResults(request: SearchRequest): Promise<SearchResponse>\`.
* POST requests to \`${import.meta.env.VITE_API_BASE_URL}/api/search\`.
* Create a helper mapping frontend filter state to \`SearchRequest\`.
* Handle network failures and non-successful HTTP responses

Replace the old mock-data result model with the real ranked funding opportunity response. Tasks

* Change \`Result.tsx\` to accept a \`RankedOpportunity\` prop.
* Display opportunity title, funder, summary and opportunity URL.
* Support all four ranking criteria and their labels, scores and reasons.
* Use Stage 1 display-label mappings for backend values.
* Update \`Result.test.tsx\` using a realistic \`RankedOpportunity\` fixture.

Replace mock search results with real backend results and support incremental pagination. Tasks

* Replace \`fetchMockResults\` with \`fetchResults\`.
* Construct \`SearchRequest\` from the search query and selected filters.
* Use \`response.total\` for the results count.
* Track \`offset\` and append additional results when requested.
* Hide or disable 'More results' when all results have loaded.
* Reset results and offset when a new search is performed.

### KAN-62

**Configure API environment variables**

Feature · To Do · Unassigned · labels: backend, deployment, frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-62)

Configure the frontend to connect to the correct API in local development and production. Tasks

* Add \`VITE_API_BASE_URL=http://localhost:8000\` to the local environment configuration.
* Configure the GitHub Actions deployment workflow to use the Render API URL.
* Verify that local and deployed builds use the correct API endpoint.
* Optionally implement \`pingHealth()\` for backend health checks.

### KAN-63

**Redesign funding result cards**

Feature · In Review · Paige Varney · labels: frontend · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-63)

Improve the results page visual hierarchy by replacing the current oversized information-heavy cards with compact, scannable cards based on the Figma design. Tasks

* Reduce default card height, spacing and displayed text.
* Show the funding title, short description and eligibility badge prominently.
* Display key information such as funding amount and deadline concisely.
* Move detailed ranking reasons and criteria into an expandable section or detail view.
* Add a clear 'View opportunity' link and responsive styling.

### KAN-64

**Retire the illustrative mock data set and schedule the crawl, normalise and publish pipeline**

Task · In Progress · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-64)

The deployed API still serves the 30 hand-written records from backend/data/mock_opportunities.json, and the backend defaults to that set whenever FMF_DATA_SOURCE is unset. For delivery the product must serve crawled data only.

Scope:

* Remove the mock data source from the product code path. FMF_DATA_SOURCE accepts sqlite or postgres only; unset means the crawler's SQLite database.
* Keep the 30 records as the evals corpus (backend/evals/) because golden.json is labelled against them, and as the fixture the tests and Playwright end-to-end run seed from.
* Drop `publish --source mock`.
* Eligibility reasons use human labels instead of enum values such as postdoc_0_2 (supersedes the frontend rewrite in PR #42).
* Add a scheduled GitHub Actions workflow that crawls a seed list of FoR divisions, normalises and publishes to Supabase Postgres, using repository secrets SERPAPI_API_KEY, GEMINI_API_KEY (optional) and FMF_DATABASE_URL. Architecture decision 2 (batch freshness).
* Update README, backend/README, docs/11-testing and docs/12-deployment.

Blocked on credentials for the production run: a SerpApi key, and the Supabase session-pooler URL, must be added as GitHub repository secrets before the first scheduled run can replace the mock rows in Postgres.

### KAN-65

**Tailor results to Australian opportunities and fix card summaries showing menu text**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-65)

Demo feedback (client requirement): results are mostly American and selecting Australian citizenship changes nothing; result card summaries show site menu text instead of body text.

Root causes:

* SerpApi discovery has no locale, so Google returns US-default results; nothing in ranking knows the researcher's institution is in Australia (`countries` empty on every live record).
* The extractor keeps nav/header/footer text and `summarise` takes the first 400 characters, which is the menu.

Fix: Google Australia locale and "Australia" in every query; institution-location eligibility check (request field `institution_country`, default AU); strip page chrome at extraction and skip leading menu text in summaries; re-crawl and re-publish.

### KAN-66

**Foreign funders show 100% eligible once any filter is applied**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-66)

Reported by Andrew from testing: with no filters the top results are mostly Australian, but applying any filter brings American and other foreign sites into the list at 100% eligibility.

Root cause: when a funder's location cannot be determined (generic .org/.com domain, no stated countries, no mention of Australia), the location check adds nothing. One passing filter check (e.g. career stage) then makes the state "eligible" (score 1.0).

Fix: an unconfirmed location caps eligibility at "potentially eligible" (0.7), with a reason saying the location could not be confirmed.

### KAN-67

**AI summaries on every card, and show Gemini quota problems on screen**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-67)

Cards still show menu text ("Skip to content ...") as the summary after KAN-65.

Root cause (crawl run 39112367229, 2026-10-18): Gemini's free tier allows 5 requests per minute for gemini-2.5-flash. The sixth call returns 429 with quotaId GenerateRequestsPerMinutePerProjectPerModel-FreeTier and a retry delay of about 9 seconds. The KAN-64 quota breaker treats any 429 as the daily quota being gone, so the rest of the run (164 rows) fell back to rule-built summaries. Cards from earlier runs also still carry pre-KAN-65 summaries.

Scope:

* Wait out per-minute 429s and retry; only a per-day quota (or a key/billing error) stops LLM use for the run.
* Record each run's LLM status (calls, failures, why it stopped) in Postgres.
* API exposes it; the frontend shows a notice when the last run hit a plan limit or a key/plan error, and how many results have rule-only summaries.

### KAN-68

**Stale menu-text summaries on 468 live cards; rule summaries cut proper nouns ("(NESP) is...")**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-68)

Reported 2026-10-18 after KAN-65 shipped: cards still show "Skip to main content Home ..." as the summary.

Root cause 1 (stale data): the KAN-65 extractor fix only applies to pages crawled after it merged (19:36). The one crawl run since (39112367229, 08:40 UTC) re-published 164 records; the other 468 of the 632 live records were normalised by the 01:03 and 02:17 runs with the old extractor and were never touched again. Every workflow run starts from an empty SQLite, and discovery returns different URLs each week, so old records are never re-normalised. Verified by re-fetching the worst pages (LAF, NSF, SICB, Creative Australia, FHRI) through the current extractor: all come out as body text.

Root cause 2 (code): `_prose_start` in backend/normaliser/parsers.py treats any run of three capitalised tokens as a menu, so a proper noun opening the first real sentence is cut: "The FHRI Fund releases..." becomes "Fund releases...", "The National Environmental Science Program (NESP) is..." becomes "(NESP) is...". Live on fresh records from the 08:40 run.

Fix:

* Keep a capitalised run that belongs to the first prose sentence; still skip share buttons, breadcrumbs and filter lists that sit inside `<main>`.
* Add a refetch mode to the weekly workflow: re-fetch every URL already in Postgres through the current extractor (plain HTTP, no SerpApi), re-normalise and re-publish. Run it once now and whenever extraction or summary rules change.

Not a ranking bug: "eligibility out of order" is the weighted overall (eligibility 0.4, match 0.3, value 0.15, deadline 0.15); only likely-ineligible results are forced to the bottom (ranking-discussion-points.md point 2).

### KAN-69

**Move the normaliser's LLM extractor from Gemini to OpenRouter with a small open-weight model**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-69)

Gemini's free tier (5 requests a minute on gemini-2.5-flash, see KAN-67) throttles every crawl. Swap the extractor to OpenRouter (OpenAI-compatible API, pay-as-you-go credits) and default to a small open-weight model that supports structured JSON output.

Scope:

* OpenRouterExtractor replaces GeminiExtractor; key is OPENROUTER_API_KEY; FMF_LLM_MODEL still overrides the model.
* Error handling: 429 waited out; 401/402/403 (bad key, out of credits) stop LLM use and show on screen.
* Crawl workflow, .env.example, READMEs, ADR-003, deployment docs, frontend notice wording.
* Repository secret OPENROUTER_API_KEY must be set by Anna (value never in the repo).

### KAN-70

**Cap the LLM reply length so a runaway generation cannot stall the crawl**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-70)

Refetch run 39157596776 (first OpenRouter run) never finished: it was cancelled at 5h28m. Log shows four pages where the model degenerated into an unbounded reply (790,360 / 519,028 / 21,843 lines / 775,754 characters) before failing as invalid JSON, each taking 20 to 90 minutes. The request sets no max_tokens, so nothing stops a runaway generation; the 60s client timeout never fires because tokens keep arriving.

Fix: set max_tokens on the OpenRouter request so a runaway fails in seconds and the row falls back to rules, with a regression test.

### KAN-71

**Fetch sites and call the LLM in parallel during a refresh**

Task · Done · Anna Sekulic · [open in Jira](https://annaseku01.atlassian.net/browse/KAN-71)

A serial refetch of 668 pages took about 1.5 hours, too slow to land AI summaries before the demo. PR #53 (https://github.com/annaseku/unimelb-find-me-funding/pull/53, merged 14b190f): refetch fetches up to 8 hosts at once (each host stays sequential, keeping the per-request delay per site) and the normaliser makes up to 8 extractor calls at once, results applied in row order, stop reasons still halting new calls. Refetch run 39186180456 started on the merged commit. The stuck scheduled crawl 39171202167 (pre-KAN-70 code) was cancelled to unblock it.
