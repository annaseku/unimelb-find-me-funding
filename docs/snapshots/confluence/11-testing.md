# 11. Testing

> Snapshot of the Confluence page [11. Testing](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10780673), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 11 (Artefacts).** The Week 7 testing lecture asks for four things: a test plan, acceptance criteria that guide test cases, test cases, and test reports. This page is the test plan. Test cases and reports: [Test Cases and Reports](test-cases-and-reports.md). Acceptance criteria: [User Stories and Acceptance Criteria](user-stories-and-acceptance-criteria.md). How to run each suite: `docs/11-testing/README.md` in the repo.

**Owner:** Anna Sekulic (testing and QA). **Status:** Draft for team review, 24/09. Updated 05/10: end-to-end tests and coverage reporting added in [PR #37](https://github.com/annaseku/unimelb-find-me-funding/pull/37) (KAN-50, KAN-58), awaiting review.

## 1. Objectives

1. Researchers only see opportunities they can plausibly apply for, ranked in an order they can understand. Eligibility is the client's top priority.
2. Every functional requirement (FR-01 to FR-19) has at least one test that would fail if it broke.
3. Nothing reaches main, and so production, without passing the automated suite.
4. The client confirms, by acceptance testing, that the product does what they asked.

## 2. Tools

| Level | Backend | Frontend |
| --- | --- | --- |
| Unit | pytest (251 tests across 19 files, one file per module) | Vitest with Testing Library (7 test files) |
| Integration | FastAPI TestClient for the API; the Postgres repository against a real Postgres 17 in CI; normaliser pipeline against a SQLite fixture | Page tests through the router with a mocked funding service |
| End-to-end | Playwright (4 tests): the real UI in Chromium against the real API on the mock data set. Checks that a search shows the API's ranking in order, each result rates all four criteria and links out, Show more loads the next page, and refining a search sends the new criteria |  |
| Ranking quality | Golden-set evals (`python -m backend.evals.run_evals`) with a weight-sensitivity report |  |
| Coverage | pytest-cov with branch coverage: 80% in CI. Most of the gap is the crawler package | @vitest/coverage-v8: 90.7% of statements, 86.8% of branches |
| Static checks | ruff lint and format | ESLint, TypeScript type-check |
| Automation | GitHub Actions on every pull request. Merge needs all seven required jobs green plus one teammate's approval. The end-to-end job runs on every PR but is not yet a required check |  |

## 3. Scope

**In scope:** eligibility, research match, funding value and deadline scoring; weighting and ordering; the search API and its contract; the normaliser's parsers and extractor fallbacks; the publish and normaliser command-line tools; the crawler's robots.txt gate; the search form and results pages; the frontend-to-API search flow end to end; the deployed frontend-to-API integration.

**Out of scope for this release:** researcher profiles and saved searches (not built); the LLM research-match scorer (not started); load beyond a handful of concurrent users (Render free tier); third-party sites' availability.

## 4. Types of testing, who and when

| Type | What | Who | When |
| --- | --- | --- | --- |
| Unit | Each scorer, parser and component on its own | The developer writing the code | In the same PR as the code (Week 7: write tests in parallel with development) |
| Integration | API to repository to database; frontend pages to service | The developer; the reviewer checks they exist | Same PR; CI on every PR |
| End-to-end | A researcher's search through the real UI and the real API | CI | Every PR |
| Regression | The full automated suite | CI | Every PR and every push to main |
| Coverage | Which lines and branches the suite never runs | CI reports it; the developer checks their change is covered | Every PR |
| Ranking evaluation | Golden set of known-good orderings | Backend team | Any ranking or normaliser change; report attached to the PR |
| Acceptance | Test cases written from each user story's acceptance criteria | Someone other than the author, then the client | End of each sprint, before the sprint review demo |
| User experience | A researcher attempts real tasks unaided | Run by the front-end team, with the client or a researcher the client nominates | Once before the final presentation |
| Performance (light) | Cold start and response time of the deployed API | Anna | Before each client demo |

## 5. Entry and exit criteria

A story is Done when its acceptance test cases pass, the automated suite is green on main, and the reviewer has approved the PR.

## 6. Bug reporting

1. Found in your own PR: fix it there.
2. Found anywhere else: create a Task on the KAN board labelled `bug`, with steps to reproduce, expected result, actual result, environment (local or deployed, browser) and a screenshot or log. If it is in someone else's area, assign them and mention it in Slack. (KAN has no Bug issue type; a project admin can add one in the project settings, and then bugs use that instead.)
3. The fix PR names the KAN key in its title and adds a test that fails without the fix.
4. The task closes when that PR merges.

## 7. Test reports

Every CI run is a test report: [GitHub Actions](https://github.com/annaseku/unimelb-find-me-funding/actions). The Backend CI run summary includes a coverage table, and a failed end-to-end run uploads a Playwright report with a trace of each failure. At the end of each sprint we add a summary to [Test Cases and Reports](test-cases-and-reports.md): automated suite results on main, acceptance test results per case, coverage, bugs opened and closed.

## 8. Risks

* Keyword overlap is a weak proxy for research fit until the semantic scorer lands; the golden set guards the ordering in the meantime.
* Crawled pages change without notice; parser tests use saved real-world fixtures so a site change shows up as a failing fixture, not silent bad data.
* Coverage is measured but has no pass mark yet. The team needs to agree a threshold before CI enforces one (KAN-50). The crawler package is the largest untested area (KAN-49).
* The end-to-end Show more test needs more than 10 open mock opportunities, and the API ranks against the real date. From 2 December 2026 it fails until someone moves the deadlines in `backend/data/mock_opportunities.json` forward.
