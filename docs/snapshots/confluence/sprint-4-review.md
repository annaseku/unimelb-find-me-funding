# Sprint 4 Review

> Snapshot of the Confluence page [Sprint 4 Review](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46759937), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

#### **Sprint dates:** \[05/10 - 12/10\]

---

## 1. Sprint Goal

> **Goal:** Implement Find an Expert, and carry Sprint 3's goals over the line: finalise the front end and back end, integrate them, and apply client feedback. See [Sprint 4 Description + Planning](sprint-4-description-planning.md).

### Success Criteria

| Goal | Metric / Success Criteria | Outcome |
| --- | --- | --- |
| Implement Find an Expert | Researcher profile search from a Find an Expert page (US10) | Not started. It's a could-have story, and it wasn't broken into cards at planning. |
| Finalise front end | All frontend cards Done; lint, tests and build pass in CI on main | Mostly complete. Dropdowns and formatting fixes merged (PRs #30, #33), and Frontend CI stayed green. The citizenship and FoR dropdown rework (PR #39) merged on 17/10, just after the sprint. |
| Finalise back end | pytest and ranking evals pass in CI on Python 3.11 to 3.13 | Complete. Backend CI stayed green, and a coverage report was added (KAN-50). |
| Integrate front and back end | The deployed frontend returns ranked results from the deployed API | Complete, and now guarded by a Playwright end-to-end test against the real API (KAN-58). |
| Apply suggested changes | Client feedback logged with owners and cards | Not complete. There was no client check-in this sprint. |

---

## 2. Planned Work

1. Implement Find an Expert
2. Finish the Sprint 3 milestones: finalise front end, finalise back end, integrate, apply suggested changes

---

## 3. Completed Work + Demonstration

### Completed

* ✅ Frontend dropdowns using the backend's value and label options (PR #30, Andrew)
* ✅ Formatting fixes (PR #33, Sophia)
* ✅ Playwright end-to-end tests of the search flow against the real API, and coverage reports in both CI pipelines (PR #37, KAN-58, KAN-50)
* ✅ Field of Research dropdown with all 23 ANZSRC 2020 divisions (KAN-60)
* ✅ Dropdown label regression fixed, with a regression test (KAN-59)
* ✅ Documentation organised by the Progress Checklist, plus a CONTRIBUTING guide (KAN-43)
* ✅ Duplicate logo removed (PR #40, Andrew)
* ✅ Every PR merged this sprint had a teammate review (PRs #30, #33, #37, #40)

### Partially Completed

* 🟡 Citizenship and FoR dropdown rework. Paige resolved merge conflicts across the open PRs on 12/10, and the work merged on 17/10 (PR #39).

### Not Completed

* ❌ Find an Expert (US10)
* ❌ Client check-in and feedback

---

## 4. Issues / Blockers

| Issue | Impact | Resolution / Next Step |
| --- | --- | --- |
| Merge conflicts between long-running branches | Resolving one conflict silently reintroduced an old dropdown bug | Fixed with a regression test (KAN-59). Lesson: review the merge result itself. |
| Find an Expert not broken into tasks | No progress on the objective | Moved to future work at handover |

---

## 5. Sprint Outcome

**Sprint goal:** 🟡 Partially achieved

**Summary:**

The team got merging moving again, and every PR had a review. End-to-end tests now prove the frontend and backend work together on every pull request. The Find an Expert objective wasn't started, and client contact is still outstanding; both carry into the final sprint and handover.
