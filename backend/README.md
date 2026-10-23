# Find Me Funding: backend

Two packages live here. `crawler/` (Jummana) discovers and stores funding pages; its own README explains it. `ranking/`, `data/`, `api/` and `evals/` (Anna) score opportunities against a researcher's inputs and serve the results to the React frontend.

| Component | Status |
| --- | --- |
| Crawler (discovery, fetch, extract, store) | Built, see `crawler/README.md` |
| Ranking engine (four criterion scores, weighted overall) | Prototype built; ranks normalised crawler records from SQLite by default or Supabase Postgres in deployment; evals use a separate corpus |
| FastAPI search endpoint for the frontend | Deployed on Render with Postgres; locally defaults to the crawler SQLite database |
| Normalising crawler rows into structured opportunities | Prototype built, rules plus optional LLM extractor (OpenRouter), see Normaliser below |
| LLM or embedding research-match scorer | Not started, seam is in `ranking/research_match.py` |

## Setup

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
```

### Environment variables

Copy the template once: `cp backend/.env.example backend/.env`. The file can be empty or absent for local SQLite development, tests and evals. The API needs a normalised SQLite database (see below) or a Postgres connection. These local workflows need no key; the only code that uses one is the normaliser's optional extractor (see Normaliser below), and it runs rules-only without it.

The template lists `OPENROUTER_API_KEY` and `FMF_DATABASE_URL`. `OPENROUTER_API_KEY` enables the normaliser's extractor today and is reserved for the LLM research-match scorer that has not been started. Create a key at openrouter.ai and put it in your own `backend/.env`; `backend/normaliser/llm.py` reads it from the environment. You do not need a key to work on the crawler, the ranker, the API or the frontend. Rules that apply to everyone:

- Never commit a key. `.env` is gitignored, and if `git status` ever lists it, fix the ignore rule rather than committing it. A key committed once stays in the history even after you delete the line, so a leak means rotating the key, not just reverting the commit.
- Never paste a key into Slack, a Jira comment or a Confluence page. If one has to be shared, share it through a password manager.
- Never put a key in `frontend/`. Vite inlines anything prefixed `VITE_` into the browser bundle, so it would ship to every visitor. LLM calls go through the backend.
- In CI a key is a GitHub Actions repository secret referenced as `${{ secrets.OPENROUTER_API_KEY }}`, never a file. Better still, mock the LLM in tests so the suite stays deterministic and free.
- Keep the key backend-side. `backend/.env` is for secrets; if the frontend later needs configuration such as an API base URL, that belongs in a separate `frontend/.env` where a `VITE_` prefix is safe because the values are public.

## Running the API and tests

From the repository root, with the venv active, first crawl and normalise a local database or seed an illustrative development fixture with `python -m backend.evals.seed_sqlite funding_crawler.db`. The evals corpus lives in `backend/evals/corpus.json`, with researcher profiles in `backend/evals/profiles.json`; tests seed temporary SQLite databases from it, and the product never selects it as a data source.

```bash
uvicorn backend.api.main:app --reload      # interactive docs at http://localhost:8000/docs
pytest backend                             # unit, API and golden-set tests
python -m backend.evals.run_evals          # ranking eval report and weight sensitivity
```

Try a search:

```bash
curl -s -X POST localhost:8000/api/search -H 'content-type: application/json' \
  -d '{"citizenships":["AU"],"career_stage":"postdoc_2_5","for_codes":["3103"],"research_description":"coral reef resilience"}'
```

## Normaliser

`normaliser/` turns the crawler's raw rows (page text, a parsed deadline, a raw dollar string, an eligibility snippet) into the structured `Opportunity` records the ranker scores. Deterministic rules run first and stamp every field with where it came from; if `OPENROUTER_API_KEY` is set, an LLM extractor fills the prose-derived fields (citizenship, career stage, research codes, funder name, summary) and never overrides a rule-parsed date or amount. Results land in a `normalised_opportunities` table in the same SQLite file; the crawler's own table is never written.

```bash
python -m backend.normaliser.run --db funding_crawler.db            # rules, plus the model if a key is set
python -m backend.normaliser.run --db funding_crawler.db --no-llm   # rules only
FMF_DATA_SOURCE=sqlite FMF_DB_PATH=funding_crawler.db uvicorn backend.api.main:app --reload
```

| Variable | Effect |
| --- | --- |
| `FMF_DATA_SOURCE` | `sqlite` (default) serves the normalised crawler table; `postgres` serves Supabase for the deployed API (see Supabase Postgres below). Other values are rejected |
| `FMF_DB_PATH` | SQLite file for `sqlite` mode; defaults to the crawler's `DB_PATH` |
| `FMF_DATABASE_URL` | Postgres connection string for `postgres` mode. Required in that mode; the API raises rather than quietly falling back to another data source |
| `OPENROUTER_API_KEY` | Enables the extractor. Everything runs without it; the records are just sparser |
| `FMF_LLM_MODEL` | OpenRouter model id for the extractor, default `qwen/qwen3-30b-a3b-instruct-2507`. It must support structured outputs |
| `FMF_LLM` | Set to `off` to skip the extractor even when a key is present |

The extractor runs once per changed page: unchanged pages are skipped by content hash on later runs, so re-running the pipeline costs only what the crawler found new. The extractor calls OpenRouter with pay-as-you-go credits (KAN-69 replaced Gemini, whose free tier capped it at 5 requests a minute). A 429 is waited out using the Retry-After header; a 401 (bad key) or 402 (out of credits) stops LLM use for the rest of the run, which finishes rules-only, and the Results page says so. Crawled text is stripped of NUL bytes on read, because Postgres rejects them inside JSON. Design record: `docs/09-architectural-design/adr/ADR-003-normaliser.md`.

## Supabase Postgres

SQLite is a file on whoever ran the crawler. The deployed API cannot read it, because Render's free plan has no persistent disk, so the container filesystem resets on every deploy. `data/postgres_repository.py` serves the same `normalised_opportunities` table out of Supabase Postgres instead, behind the same repository interface, so the API code is unchanged.

`data/publish.py` is what puts records there. It copies a normalised crawler SQLite database and creates the Postgres table on first run. Only publish crawled records to the deployed store; the evals corpus is for evals and local test fixtures.

To seed a local database for development without keys, run `python -m backend.evals.seed_sqlite funding_crawler.db` and use the default SQLite data source. This fixture is illustrative and must not be published to the deployed store.

Put `FMF_DATABASE_URL` in `backend/.env` (copy the name from `.env.example`); `postgres_repository.py` loads that file on import, so there is nothing to export. Then, from the repository root:

```bash
python -m backend.data.publish --db-path funding_crawler.db
FMF_DATA_SOURCE=postgres uvicorn backend.api.main:app --reload
```

**Use the Supavisor session-mode pooler URL, port 5432, not the direct connection string.** Supabase's direct endpoint (`db.<ref>.supabase.co`) publishes only an IPv6 `AAAA` record on the free plan, and Render is IPv4-only, so a direct URL fails from the deployed service while working fine from a laptop. Transaction mode (port 6543) is also wrong here: it does not support the prepared statements psycopg uses. Copy the exact string from the Supabase dashboard's **Connect** button, session mode.

Free-plan projects pause after seven days of low database activity; the weekly crawl keeps the project active. If it does pause, `/api/search` returns HTTP 500 while `/api/health` still returns 200; restore it from the Supabase dashboard.

## CI/CD

`.github/workflows/backend-ci.yml` runs on every pull request and push to main that touches `backend/`: ruff lint and format check, pytest plus the ranking evals on Python 3.11, 3.12 and 3.13, and a Docker build of `backend/Dockerfile`. Reproduce it locally from the repository root:

```bash
ruff check backend && ruff format --check backend
pytest backend -q && python -m backend.evals.run_evals
docker build -f backend/Dockerfile -t find-me-funding-backend .
docker run --rm -p 8000:8000 find-me-funding-backend
```

`ruff format backend` fixes formatting failures. `crawler/` is excluded from ruff; drop the `extend-exclude` line in `pyproject.toml` once it passes the lint rules.

`.github/workflows/backend-cd.yml` runs after CI passes on main and pushes the image to `ghcr.io/annaseku/unimelb-find-me-funding/backend`, tagged `latest` and `sha-<commit>`. Pulling a private package needs a GitHub token with `read:packages`.

## Hosting

The API runs on Render as a Docker web service defined in `render.yaml` at the repository root (decision record: `docs/09-architectural-design/adr/ADR-004-deployment-architecture.md`). Render builds `backend/Dockerfile` from the repository on every push to main, so a merge is a deploy; there is no separate release step. The service is `find-me-funding-api` in the Crawlers workspace, Singapore region, free plan, health-checked on `/api/health`, and the frontend on GitHub Pages is already in the CORS allow-list in `api/main.py`.

The free plan spins the service down after 15 minutes idle and takes about a minute to wake, so hit `/api/health` before a client demo. `GEMINI_API_KEY` is declared in `render.yaml` with `sync: false`, which means its value lives only in the Render dashboard; nothing reads it yet, so it can stay empty. Changing the service's shape (plan, region, env var names) is an edit to `render.yaml`, not a dashboard click, so the change is reviewed like any other.

## How the ranking works

Each opportunity gets four separate scores, each with a label and plain-English reasons the UI shows:

1. `ranking/eligibility.py`: citizenship, employer type, career stage and funding type checked against the researcher's inputs. Four states: eligible, potentially eligible, unknown, likely ineligible. A contradiction de-ranks the result but does not drop it unless the request sets `hide_ineligible`.
2. `ranking/research_match.py`: ANZSRC FoR and ToA code overlap plus keyword overlap between the free-text description and the opportunity. High, medium or low.
3. `ranking/funding_value.py`: amount banded under $1M, $1M to $2M, $2M to $5M, $5M and over.
4. `ranking/deadline.py`: days to deadline banded over 60, 60 to 30, 30 to 15, under 15. More lead time scores higher.

`ranking/ranker.py` combines them with the weights in `ranking/weights.py` (default eligibility 0.4, match 0.3, funding 0.15, deadline 0.15; any request can override) and filters closed opportunities unless `include_closed` is set. The API pages over the ranked list with `limit` and `offset`.

Locally the ranker scores the normalised crawler records in SQLite by default (see Normaliser above), and the deployed API uses `postgres`. A missing local database raises a clear error without creating an empty file. The hand-written corpus is loaded explicitly for evals and seeded test fixtures only. Design records: `docs/09-architectural-design/adr/ADR-002-ranking-engine.md` and `docs/09-architectural-design/adr/ADR-003-normaliser.md`. Decisions still needing client confirmation: `docs/07-requirements/ranking-discussion-points.md`.
