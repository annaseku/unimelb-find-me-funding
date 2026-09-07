# Find Me Funding: backend

Two packages live here. `crawler/` (Jummana) discovers and stores funding pages; its own README explains it. `ranking/`, `data/`, `api/` and `evals/` (Anna) score opportunities against a researcher's inputs and serve the results to the React frontend.

| Component | Status |
| --- | --- |
| Crawler (discovery, fetch, extract, store) | Built, see `crawler/README` |
| Ranking engine (four criterion scores, weighted overall) | Prototype built, scores structured mock data |
| FastAPI search endpoint for the frontend | Prototype built |
| Normalising crawler rows into structured opportunities | Prototype built, rules plus optional Gemini extractor, see Normaliser below |
| LLM or embedding research-match scorer | Not started, seam is in `ranking/research_match.py` |

## Setup

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
```

### Environment variables

Copy the template once: `cp backend/.env.example backend/.env`. A fresh clone runs with that file empty, or absent entirely. The API, `pytest backend` and the evals all work with no key; the only code that uses one is the normaliser's optional extractor (see Normaliser below), and it runs rules-only without it.

`GEMINI_API_KEY` is the only name listed. It enables the normaliser's extractor today and is reserved for the LLM research-match scorer that has not been started. Generate your own key in Google AI Studio and put it in your own `backend/.env`; the `google-genai` SDK reads that variable straight from the environment, so `genai.Client()` needs no arguments. You do not need a key to work on the crawler, the ranker, the API or the frontend. Rules that apply to everyone:

- Never commit a key. `.env` is gitignored, and if `git status` ever lists it, fix the ignore rule rather than committing it. A key committed once stays in the history even after you delete the line, so a leak means rotating the key, not just reverting the commit.
- Never paste a key into Slack, a Jira comment or a Confluence page. If one has to be shared, share it through a password manager.
- Never put a key in `frontend/`. Vite inlines anything prefixed `VITE_` into the browser bundle, so it would ship to every visitor. LLM calls go through the backend.
- In CI a key is a GitHub Actions repository secret referenced as `${{ secrets.GEMINI_API_KEY }}`, never a file. Better still, mock the LLM in tests so the suite stays deterministic and free.
- Keep the key backend-side. `backend/.env` is for secrets; if the frontend later needs configuration such as an API base URL, that belongs in a separate `frontend/.env` where a `VITE_` prefix is safe because the values are public.

## Running the API and tests

From the repository root, with the venv active:

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

`normaliser/` turns the crawler's raw rows (page text, a parsed deadline, a raw dollar string, an eligibility snippet) into the structured `Opportunity` records the ranker scores. Deterministic rules run first and stamp every field with where it came from; if `GEMINI_API_KEY` is set, a Gemini extractor fills the prose-derived fields (citizenship, career stage, research codes, funder name, summary) and never overrides a rule-parsed date or amount. Results land in a `normalised_opportunities` table in the same SQLite file; the crawler's own table is never written.

```bash
python -m backend.normaliser.run --db backend/funding_crawler.db            # rules, plus the model if a key is set
python -m backend.normaliser.run --db backend/funding_crawler.db --no-llm   # rules only
FMF_DATA_SOURCE=sqlite FMF_DB_PATH=backend/funding_crawler.db uvicorn backend.api.main:app --reload
```

| Variable | Effect |
| --- | --- |
| `FMF_DATA_SOURCE` | `mock` (default) serves `data/mock_opportunities.json`; `sqlite` serves the normalised table |
| `FMF_DB_PATH` | SQLite file for `sqlite` mode; defaults to the crawler's `DB_PATH` |
| `GEMINI_API_KEY` | Enables the extractor. Everything runs without it; the records are just sparser |
| `FMF_LLM_MODEL` | Gemini model for the extractor, default `gemini-2.5-flash` |
| `FMF_LLM` | Set to `off` to skip the extractor even when a key is present |

The extractor runs once per changed page: unchanged pages are skipped by content hash on later runs, so re-running the pipeline daily costs only what the crawler found new. Design record: `docs/adr/ADR-003-normaliser.md`.

## CI/CD

`.github/workflows/backend-ci.yml` runs on every pull request and push to main that touches `backend/`: ruff lint and format check, pytest plus the ranking evals on Python 3.11, 3.12 and 3.13, and a Docker build of `backend/Dockerfile`. Reproduce it locally from the repository root:

```bash
ruff check backend && ruff format --check backend
pytest backend -q && python -m backend.evals.run_evals
docker build -f backend/Dockerfile -t find-me-funding-backend .
docker run --rm -p 8000:8000 find-me-funding-backend
```

`ruff format backend` fixes formatting failures. `crawler/` is excluded from ruff until its rewrite on `feature/backend-crawler` lands; drop the `extend-exclude` line in `pyproject.toml` then.

`.github/workflows/backend-cd.yml` runs after CI passes on main and pushes the image to `ghcr.io/annaseku/unimelb-find-me-funding/backend`, tagged `latest` and `sha-<commit>`. Pulling a private package needs a GitHub token with `read:packages`.

## Hosting

The API runs on Render as a Docker web service defined in `render.yaml` at the repository root (decision record: `docs/adr/ADR-003-deployment-architecture.md`). Render builds `backend/Dockerfile` from the repository on every push to main, so a merge is a deploy; there is no separate release step. The service is `find-me-funding-api` in the Crawlers workspace, Singapore region, free plan, health-checked on `/api/health`, and the frontend on GitHub Pages is already in the CORS allow-list in `api/main.py`.

The free plan spins the service down after 15 minutes idle and takes about a minute to wake, so hit `/api/health` before a client demo. `GEMINI_API_KEY` is declared in `render.yaml` with `sync: false`, which means its value lives only in the Render dashboard; nothing reads it yet, so it can stay empty. Changing the service's shape (plan, region, env var names) is an edit to `render.yaml`, not a dashboard click, so the change is reviewed like any other.

## How the ranking works

Each opportunity gets four separate scores, each with a label and plain-English reasons the UI shows:

1. `ranking/eligibility.py`: citizenship, employer type, career stage and funding type checked against the researcher's inputs. Four states: eligible, potentially eligible, unknown, likely ineligible. A contradiction de-ranks the result but does not drop it unless the request sets `hide_ineligible`.
2. `ranking/research_match.py`: ANZSRC FoR and ToA code overlap plus keyword overlap between the free-text description and the opportunity. High, medium or low.
3. `ranking/funding_value.py`: amount banded under $1M, $1M to $2M, $2M to $5M, $5M and over.
4. `ranking/deadline.py`: days to deadline banded over 60, 60 to 30, 30 to 15, under 15. More lead time scores higher.

`ranking/ranker.py` combines them with the weights in `ranking/weights.py` (default eligibility 0.4, match 0.3, funding 0.15, deadline 0.15; any request can override) and filters closed opportunities unless `include_closed` is set. The API pages over the ranked list with `limit` and `offset`.

By default the ranker scores the illustrative opportunities in `data/mock_opportunities.json`. With `FMF_DATA_SOURCE=sqlite` it scores whatever the normaliser has produced from the crawler's rows (see Normaliser above). Design records: `docs/adr/ADR-002-ranking-engine.md` and `docs/adr/ADR-003-normaliser.md`. Decisions still needing client confirmation: `docs/ranking-discussion-points.md`.
