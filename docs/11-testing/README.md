# Testing

The test plan, test cases and test reports are in Confluence under [11. Testing](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10780673). This page is how to run each suite.

| Suite | Command | Where | In CI |
| --- | --- | --- | --- |
| Backend unit and integration | `pytest backend` | `backend/tests/`, one file per module | Python 3.11, 3.12 and 3.13, against Postgres 17 |
| Postgres repository | `FMF_TEST_DATABASE_URL=postgresql://... pytest backend/tests/test_postgres_repository.py` | Skipped locally unless the variable is set | Yes |
| Ranking evals | `python -m backend.evals.run_evals` | `backend/evals/golden.json` | Yes |
| Backend lint and format | `ruff check backend && ruff format --check backend` | | Yes |
| Frontend unit and page tests | `cd frontend && npm test` | `*.test.ts(x)` beside the code | Yes |
| Frontend lint, types, build | `npm run lint && npm run build` | | Yes |

Every pull request runs all of these, and main is protected so a PR cannot merge until all seven CI jobs pass. Each run's results are the automated test report: [GitHub Actions](https://github.com/annaseku/unimelb-find-me-funding/actions).

## Writing tests

- Write the test in the same PR as the change, and check it fails without the change.
- A bug fix comes with a test that reproduces the bug.
- Name tests after the behaviour they prove, for example `test_ineligible_never_outranks_an_eligible_result_even_with_a_better_overall`.
- When a test covers an acceptance criterion, add it to the test case table on the Confluence Test Cases and Reports page.
