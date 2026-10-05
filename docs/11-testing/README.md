# Running the tests

The test plan (objectives, scope, who tests what, bug reporting) is the Confluence page [11. Testing](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10780673). This page is only how to run each suite. Every command is run from the repository root unless it says otherwise.

## Setup, once

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
npm --prefix frontend ci
npx --prefix frontend playwright install chromium
```

## Suites

| Suite | Command | What it proves | In CI |
| --- | --- | --- | --- |
| Backend unit and integration | `.venv/bin/pytest backend -q` | Scorers, normaliser, repositories, API, CLIs | Backend CI, Test job |
| Postgres repository | `FMF_TEST_DATABASE_URL=postgresql://... .venv/bin/pytest backend -q` | JSONB round-trip and upsert against a real Postgres; skipped without the variable | Backend CI, Test job (Postgres 17 service) |
| Ranking evals | `.venv/bin/python -m backend.evals.run_evals` | Golden-set orderings still hold | Backend CI, Test job |
| Frontend unit | `npm --prefix frontend test` | Components, pages and the funding service with a mocked API | Frontend CI, Type-check and build job |
| End-to-end | `cd frontend && PYTHON="$PWD/../.venv/bin/python" npm run test:e2e` | A researcher's search through the real UI and the real API on the mock data set | Frontend CI, End-to-end (Playwright) job |
| Lint and format | `.venv/bin/ruff check backend && .venv/bin/ruff format --check backend`, `npm --prefix frontend run lint` | Style and import order | Both Lint jobs |

For the Postgres suite, any throwaway instance works, for example `docker run -d -e POSTGRES_PASSWORD=test -e POSTGRES_DB=fmf_test -p 55432:5432 postgres:17-alpine` with `FMF_TEST_DATABASE_URL=postgresql://postgres:test@localhost:55432/fmf_test`.

## End-to-end notes

Playwright starts both servers itself: the API on port 8001 with the mock data set, and Vite on 127.0.0.1:5173 pointed at it. It never reuses a server that is already running, so if either port is taken the run stops with an error rather than testing someone else's code. Stop your own dev server on 5173 first.

The tests compare what the UI shows with what the API returns for the same request, so they check the frontend and the API contract, not the ranking itself; ranking quality is the evals' job. The show-more test needs more than 10 open mock opportunities. When mock deadlines lapse (from about April 2027) it fails with a message saying so; refresh the deadlines in `backend/data/mock_opportunities.json`.

On failure in CI, the `playwright-report` artifact on the run has a trace of each failed test. Open it with `npx playwright show-report <unzipped folder>`.

## Coverage

```sh
.venv/bin/pytest backend -q --cov=backend --cov-config=backend/pyproject.toml --cov-report=term-missing:skip-covered
npm --prefix frontend run test:coverage
```

Both CI test jobs print the same report, and Backend CI adds a table to the run summary. Coverage is report only: no threshold fails the build until the team agrees one (KAN-50). Baseline on 5 October 2026, branch coverage included: backend 78% without the Postgres suite (most of the gap is the crawler package), frontend 90.7% of statements.
