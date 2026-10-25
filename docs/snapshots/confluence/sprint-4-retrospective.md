# Sprint 4 Retrospective

> Snapshot of the Confluence page [Sprint 4 Retrospective](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46727204), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Sprint dates:** \[05/10 - 12/10\]

> **Purpose:** Reflect on how the team worked during the sprint and identify improvements for the next sprint.

---

## 1. What Went Well? 👍

* We merged regularly again: four PRs in one week, after nothing merged for almost three weeks. (PRs #30, #33, #37, #40)
* Every PR had a teammate review before it merged, which was the main fix from Sprint 3. (PRs #30, #33, #37 and #40 each have an approving review)
* We added a Playwright end-to-end test of the search flow against the real API, plus coverage reports in CI. (KAN-58, KAN-50, PR #37)
* The Field of Research dropdown now offers all 23 ANZSRC divisions, matching the backend. (KAN-60)

---

## 2. What Didn't Go Well? 👎

| Issue | Impact on Sprint |
| --- | --- |
| The sprint objective "Implement Find an Expert" wasn't started | It's a could-have story (US10), so it was always at risk; the sprint planning page never broke it into tasks. ([Sprint 4 Description + Planning](sprint-4-description-planning.md)) |
| Merge conflicts between long-running branches | Paige spent 12/10 resolving conflicts across PRs, and resolving one conflict silently brought back an old bug (the dropdown dash fix, KAN-59). (Slack 12/10; final presentation, "green CI only proves what you test") |
| The citizenship and FoR dropdown work missed the sprint | It merged on 17/10 instead (PR #39) |
| Still no client check-in | No feedback to apply. ([Client Communication Log](client-communication-log.md)) |

---

## 3. What Should We Improve? 💡

* Keep branches short and merge often, so conflicts stay small.
* Break each sprint objective into cards at planning, so we can see whether it's on track.

---

## 4. Action Items

| Action | Owner | Priority | Status |
| --- | --- | --- | --- |
| Rebase onto main before opening a PR, and review the merge result | Team | High | Ongoing |
| Break sprint objectives into Jira cards at planning | Andrew (Product Owner) | Medium | To do |
| Book the client demo | Andrew (Product Owner) | High | Done (final presentation, 19/10) |

See also: [Sprint 4 Review](sprint-4-review.md).
