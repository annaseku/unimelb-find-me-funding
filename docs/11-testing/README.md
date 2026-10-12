# Testing

The test plan, test cases and test reports are in Confluence under [11. Testing](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10780673). This page is how to run each suite. Every command is run from the repository root unless it says otherwise.

## Setup, once

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
npm --prefix frontend ci
npx --prefix frontend playwright install chromium
```

## Suites

| Suite | Command | Where | In CI |
| --- | --- | --- | --- |
| Backend unit and integration | `.venv/bin/pytest backend -q` | `backend/tests/`, one file per module | Python 3.11, 3.12 and 3.13, against Postgres 17 |
| Postgres repository | `FMF_TEST_DATABASE_URL=postgresql://... .venv/bin/pytest backend/tests/test_postgres_repository.py` | Skipped locally unless the variable is set | Yes |
| Ranking evals | `.venv/bin/python -m backend.evals.run_evals` | `backend/evals/golden.json` | Yes |
| Backend lint and format | `.venv/bin/ruff check backend && .venv/bin/ruff format --check backend` | | Yes |
| Frontend unit and page tests | `npm --prefix frontend test` | `*.test.ts(x)` beside the code | Yes |
| Frontend lint, types, build | `cd frontend && npm run lint && npm run build` | | Yes |
| End-to-end | `cd frontend && PYTHON="$PWD/../.venv/bin/python" npm run test:e2e` | `frontend/e2e/` | Yes, not yet a required check |

For the Postgres suite, any throwaway instance works, for example `docker run -d -e POSTGRES_PASSWORD=test -e POSTGRES_DB=fmf_test -p 55432:5432 postgres:17-alpine` with `FMF_TEST_DATABASE_URL=postgresql://postgres:test@localhost:55432/fmf_test`.

Every pull request runs all of these. Main is protected, so a PR cannot merge until the seven required CI jobs pass and a teammate approves it. Each run's results are the automated test report: [GitHub Actions](https://github.com/annaseku/unimelb-find-me-funding/actions).

## End-to-end notes

Playwright starts both servers itself: the API on port 8001 with the mock data set, and Vite on 127.0.0.1:5173 pointed at it. It never reuses a server that is already running, so if either port is taken the run stops with an error rather than testing someone else's code. Stop your own dev server on 5173 first.

The tests compare what the UI shows with what the API returns for the same request, so they check the frontend and the API contract, not the ranking itself; ranking quality is the evals' job. The show-more test needs more than 10 open mock opportunities. The API ranks against the real date, so as mock deadlines lapse the count drops: 20 are open on 5 October 2026 and 10 or fewer from 2 December 2026. From then the test fails with a message saying so until someone moves the deadlines in `backend/data/mock_opportunities.json` forward.

On failure in CI, the `playwright-report` artifact on the run has a trace of each failed test. Open it with `npx playwright show-report <unzipped folder>`.

## Coverage

```sh
.venv/bin/pytest backend -q --cov=backend --cov-config=backend/pyproject.toml --cov-report=term-missing:skip-covered
npm --prefix frontend run test:coverage
```

Both CI test jobs print the same report, and Backend CI adds a table to the run summary. Coverage is report only: no threshold fails the build until the team agrees one (KAN-50). Baseline on 5 October 2026, branch coverage included: backend 80% in CI (78% locally without the Postgres suite; most of the gap is the crawler package), frontend 90.7% of statements.

## Writing tests

- Write the test in the same PR as the change, and check it fails without the change.
- A bug fix comes with a test that reproduces the bug.
- Name tests after the behaviour they prove, for example `test_ineligible_never_outranks_an_eligible_result_even_with_a_better_overall`.
- When a test covers an acceptance criterion, add it to the test case table on the Confluence Test Cases and Reports page.
