# Find Me Funding

A web tool that finds research funding opportunities for University of Melbourne researchers and returns them ranked by how attractive they are to that researcher. Built by a student team for a client in the UoM Research Office as a 2026 IT Project.

A researcher fills in a short form: field of research and type of activity (ANZSRC codes), citizenship, employer type, career stage, the kind of funding they need, and a few sentences about the project. The tool searches a continuously refreshed collection of funding pages gathered from across the web, not a fixed list of funders, and returns the top ten with more on request. Every result shows a link and a rating on four criteria: eligibility, match to the research, funding value, and time to deadline.

Live frontend: https://annaseku.github.io/unimelb-find-me-funding/, calling the API at https://find-me-funding-api.onrender.com. The deployed database holds whatever the weekly crawl last published (`.github/workflows/crawl.yml`).

## How it works

```text
funder websites
   -> crawler          discover pages via search, fetch politely, extract raw signals   backend/crawler
   -> normaliser       raw text -> structured Opportunity records, rules first,         backend/normaliser
                       optional LLM extractor (OpenRouter) for the prose-derived fields
   -> store            normalised_opportunities table: SQLite locally, Supabase Postgres  backend/data
                       when deployed (python -m backend.data.publish)
   -> ranker           four separate scores + weighted overall, plain-English reasons    backend/ranking
   -> API              POST /api/search, paging, weights echoed                          backend/api
   -> frontend         React search form and results page                               frontend
```

Each ranked result carries four scores between 0 and 1, each with a label and reasons the UI can show:

| Criterion | What it checks | Labels |
| --- | --- | --- |
| Eligibility | citizenship, employer type, career stage, funding type against the funder's stated rules | eligible, potentially eligible, unknown, likely ineligible |
| Research match | ANZSRC code overlap plus keyword overlap between the description and the funder's text | high, medium, low |
| Funding value | amount in AUD, banded | under $1M, $1M to $2M, $2M to $5M, $5M and over, unknown |
| Deadline | days remaining, banded; more lead time scores higher | over 60 days, 60 to 30, 30 to 15, under 15, closed, unknown |

Default weights are eligibility 0.4, research match 0.3, funding value 0.15, deadline 0.15. Any request can override them and the response echoes what was used. Likely-ineligible results always sort after everything the researcher could apply for. Six of these behaviours are still to be confirmed with the client; see `docs/07-requirements/ranking-discussion-points.md`.

## Status

| Component | Status | Owner |
| --- | --- | --- |
| Crawler: SerpApi discovery, robots.txt, fetch, extract, SQLite, scheduler loop | Built | Jummana |
| Normaliser: rules plus optional LLM extractor (OpenRouter), provenance per field | Prototype | Anna |
| Ranking engine: four criterion scores, weighted overall, golden-set evals | Prototype | Anna |
| FastAPI search endpoint | Deployed on Render, reading Supabase Postgres | Anna |
| Frontend: search form and results page, UoM design system | Built, calling the deployed API | Paige, Andrew, Sophia |
| LLM research-match scorer | Not started; seam in `backend/ranking/research_match.py` | |
| Scheduled crawl, normalise and publish to Postgres | Built and running: weekly GitHub Actions rotation over the 23 FoR divisions (`backend/data/refresh.py`) | Anna |
| Deduplication across sources, researcher profiles | Not started | |

## Repository layout

```text
backend/
  crawler/       discovery, fetch, extract, storage, scheduler (see backend/crawler/README)
  normaliser/    crawler rows -> Opportunity records; python -m backend.normaliser.run
  ranking/       models, four scorers, weights, ranker
  data/          repository seam, SQLite and Postgres repositories, publish step, scheduled refresh
  api/           FastAPI app: /api/health, /api/status, /api/search, /api/opportunities/{id}
  evals/         golden-set ranking evals and the 30-record corpus they are labelled against; python -m backend.evals.run_evals
  tests/         pytest, one file per module
  README.md      backend setup, environment variables, how the ranking works
frontend/        React 19 + TypeScript + Vite, Vitest tests beside the code
docs/            numbered by the COMP30022 Progress Checklist; docs/README.md maps all twelve items
  07-requirements/          ranking decisions awaiting client confirmation
  09-architectural-design/  ADRs, API contract (Jira KAN-11), design specs
  10-coding/                implementation plans
  11-testing/               how to run every test suite
  12-deployment/            pipeline, environments, releases, rollback
main.py          run the crawler from the repository root
render.yaml      Render blueprint for the API
CONTRIBUTING.md  workflow, coding standards, code review policy and checklist
.github/         CI/CD workflows, PR template, bug report template
```

## Quick start

Backend, from the repository root (Python 3.11 or newer):

```bash
python3 -m venv backend/.venv && source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
uvicorn backend.api.main:app --reload      # docs at http://localhost:8000/docs
pytest backend                             # 372 tests
python -m backend.evals.run_evals          # ranking evals and weight sensitivity
```

Frontend, in a second terminal:

```bash
cd frontend
npm ci
npm run dev                                # http://localhost:5173
npm test && npm run lint && npm run build  # what CI runs
```

The API serves the crawler's SQLite database by default and raises on the first search if none exists. To work without SerpApi or OpenRouter keys, seed one from the evals corpus; to run on real crawled data:

```bash
python -m backend.evals.seed_sqlite funding_crawler.db   # 30 illustrative records, no keys needed

export SERPAPI_API_KEY=...                 # free key from serpapi.com
python -m backend.data.refresh --all --no-llm --skip-publish   # crawl every seed research area, then normalise
uvicorn backend.api.main:app --reload      # serves funding_crawler.db
```

Set `OPENROUTER_API_KEY` (pay-as-you-go key from openrouter.ai) and drop `--no-llm` to let the extractor fill the fields the rules cannot read. Copy `backend/.env.example` to `backend/.env` for the full list of variables. Never commit a key; `.env` is gitignored.

## CI, hosting and branch rules

Five GitHub Actions workflows. `backend-ci` runs ruff, pytest on Python 3.11 to 3.13, the ranking evals and a Docker build; `frontend-ci` runs eslint, Vitest, type-check and build. Both run on every pull request. On main, `backend-cd` publishes the API image to GHCR and `frontend-cd` deploys the site to GitHub Pages. `crawl` runs the weekly crawl, normalise and publish.

Main is protected: changes land by pull request only, all seven CI jobs must pass, one teammate must approve, and nobody can push directly. See `CONTRIBUTING.md` for the workflow and review checklist.

The API runs on Render as the web service in `render.yaml`, built from `backend/Dockerfile` on every push to main. Environments, releases and rollback: `docs/12-deployment/README.md`.

## Where the decisions live

Confluence space "Crawlers" is the source of truth for requirements and meeting notes; Jira project KAN tracks the work. In this repo, `docs/09-architectural-design/adr/` records the architecture decisions, `docs/09-architectural-design/api-contract.md` is the contract the frontend builds against, and `docs/07-requirements/ranking-discussion-points.md` lists what still needs the client's answer.
