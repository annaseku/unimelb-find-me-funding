# Test Cases and Reports

> Snapshot of the Confluence page [Test Cases and Reports](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33456129), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

Test cases are written from the acceptance criteria on [User Stories and Acceptance Criteria](user-stories-and-acceptance-criteria.md), following the Week 7 lecture's chain: user story, then acceptance criteria, then test cases. Automated cases name the test that covers them; manual cases are run on the deployed site by someone other than the author before each sprint review.

## Test cases

| ID | Story / AC | Type | Execution | Covered by, or steps | Expected result |
| --- | --- | --- | --- | --- | --- |
| TC01 | US01 AC1 | Functional, UI | Automated | `Home.test.tsx`: carries picked filter values in state and leaves the rest default | Picked values reach the results page |
| TC02 | US01 AC2 | Functional, API | Automated | `test_api.py`: `test_empty_search_returns_first_ten_and_total_of_open_set`; `Home.test.tsx`: navigates with default filters when nothing is picked | No filter means no restriction |
| TC03 | US02 AC1, AC2 | Functional, ranking | Automated | `test_ranker.py`: `test_ineligible_never_outranks_an_eligible_result_even_with_a_better_overall`, `test_ineligible_is_shown_and_ranked_last_by_default`; `test_eligibility.py`: `test_restriction_stated_but_nothing_supplied_is_unknown` | Ineligible sorts last; unknown is kept and labelled |
| TC04 | US03 AC1, AC2 | Functional, UI and API | Automated | `test_api.py`: `test_empty_search_returns_first_ten_and_total_of_open_set`; `Results.test.tsx`: appends pages using the submitted filters | Ten first, total shown, later pages appended |
| TC05 | US04 AC1, US05 AC1 | Functional, UI and API | Automated | `test_api.py`: `test_every_result_has_four_scores_labels_and_reasons`; `Result.test.tsx`: renders all four criteria, reasons, labels and the funder link | Four labelled criteria with reasons, and a link |
| TC06 | US06 AC1, AC2 | Functional, API | Automated | `test_ranker.py`: `test_closed_status_is_hidden_even_with_a_future_deadline`; `test_api.py`: `test_include_closed_adds_the_soft_deleted_records` | Closed hidden by default, shown on request |
| TC07 | US07 AC1 | Functional, crawler | Manual | Run `python3 main.py` with a test profile; list discovered domains; compare with the seed list | At least one discovered funder is not in the seed list |
| TC08 | US08 AC1 | Functional, crawler | Manual (no automated test yet) | Point the crawler at a page disallowed by robots.txt | The page is not fetched; the log records the skip |
| TC09 | US01 to US05 end to end | Acceptance | Manual | On the live site: open it, wait for the API to wake, search as a health researcher (Australian citizen, university, early career), open the first result's link, load more | Ten ranked results with four ratings each; link opens the funder; more results load |

## Manual test case template

From the Week 7 lecture:

| Field | Content |
| --- | --- |
| Test case | TCnn: name |
| User story | USnn, as written |
| Type / execution | Functional, UX or performance / manual or automated |
| Objective | What this proves |
| Pre-conditions | State before the test |
| Steps | Numbered actions |
| Expected result | What passes |
| Post-conditions | State after the test |
| Tester, date, result | Who ran it, when, pass or fail |

## Test reports

| Date | Build | Automated suite | Acceptance cases | Bugs opened / closed | Notes |
| --- | --- | --- | --- | --- | --- |
| 24/09 (Sprint 3, mid-sprint) | main at d4d8470 | All seven CI jobs green on the latest main run: [Actions](https://github.com/annaseku/unimelb-find-me-funding/actions) | Not yet run | 0 / 0 logged in Jira | Baseline. TC07 to TC09 to be run before the Sprint 3 review |

## Gaps

- [ ] No automated test for the robots.txt gate (TC08): add one with the crawler test suite
- [ ] No code coverage report: add one to Backend CI
- [ ] Run TC07 to TC09 before the Sprint 3 review and record the results above
