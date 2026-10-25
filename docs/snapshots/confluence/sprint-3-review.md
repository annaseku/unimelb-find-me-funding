# Sprint 3 Review

> Snapshot of the Confluence page [Sprint 3 Review](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46727169), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

#### **Sprint dates:** \[14/09 - 28/09\]

---

## 1. Sprint Goal

> **Goal:** Finish an integrated prototype (frontend calling the deployed backend) to present to the client, then apply the client's feedback. See [Sprint 3 Description + Planning](sprint-3-description-planning.md).

### Success Criteria

| Goal | Metric / Success Criteria | Outcome |
| --- | --- | --- |
| Finalise front end | All Sprint 3 frontend cards Done; `npm run lint`, `npm test` and `npm run build` pass in CI on main | Partially complete. The search form with dropdowns matching the backend vocabulary was merged on 15/09 (PR #22), and Frontend CI was green on main. Paige opened four follow-up issues on 21/09 (GitHub #24 to #27); these were finished in Sprint 4. |
| Finalise back end | All Sprint 3 backend cards Done; pytest and ranking evals pass in CI on Python 3.11 to 3.13 | Complete. The crawler merged on 14/09 (PR #17), and the API began serving ranked results from Supabase Postgres on 15/09 (PR #19). Backend CI was green on all three Python versions. |
| Integrate front and back end | The deployed frontend returns ranked results from the deployed API for at least three search profiles, shown live in the client demo | Integration complete on 15/09: the frontend search calls the ranked API (KAN-37). On 17/09 Anna showed the client our initial prototype at a Zoom progress check-in with the client and the leads of the other teams on this project. |
| Apply suggested changes | Every item of client demo feedback is logged with an owner and a card | Not complete. The client gave feedback at the 17/09 check-in, but it wasn't written up at the time, so no cards came from it. Feedback from the 19/10 demo is still pending. |

---

## 2. Planned Work

At the beginning of the sprint, we planned to:

1. Finish the prototype to present to the client
    1. Finalise front end (Andrew, Paige, Sophia)
    2. Finalise back end (Anna, Jummana)
    3. Integrate front and back end
2. Apply suggested changes from the client demo

Supervisor feedback from the week 8 tutorial added: one high-level architecture diagram, and code review before merging to main ([Standup Notes 14/09](standup-notes-1409.md)).

---

## 3. Completed Work + Demonstration

### Completed

- ✅ Backend serving ranked search results from Supabase Postgres (PR #19, KAN-33, KAN-35)
- ✅ Crawler merged into main (PR #17, KAN-18 to KAN-21)
- ✅ Frontend search form wired to the ranked API (PR #22, KAN-36, KAN-37). Built at an integration session held by Andrew, Paige and Jummana on 15/09.
- ✅ Initial prototype shown to the client at the 17/09 progress check-in (Zoom; Anna, with the other teams' leads)
- ✅ Architecture diagram set, including the high-level diagram the supervisor asked for (21/09, [Architecture Overview](architecture-overview-find-me-funding.md), KAN-41)
- ✅ Backlog rebuilt in Jira as six epics, with stories and acceptance criteria (21/09)
- ✅ User stories with IDs and acceptance criteria, and test cases traced to them (24/09, [User Stories and Acceptance Criteria](user-stories-and-acceptance-criteria.md), [Test Cases and Reports](test-cases-and-reports.md))
- ✅ PR template, a Communication Plan, and a Legal, Ethics and Data Handling page
- ✅ Supervisor access fixed on 17/09: Progress Report 1 links didn't open for our supervisor, so we added our supervisor to the Confluence workspace and the GitHub repo

### Partially Completed

- 🟡 Frontend filter behaviour (citizenship, FoR codes, funding types). Issues #24 to #27 carried into Sprint 4.

### Not Completed

- ❌ Writing up the client's 17/09 feedback and turning it into cards
- ❌ Acceptance test cases TC07 to TC09 (KAN-48)
- ❌ Planning poker estimates (KAN-47)

### Demonstration

The integrated prototype ran end to end on the deployed site from 15/09, and Anna showed the initial prototype to the client at the 17/09 check-in. The full product was demoed at our final presentation on 19/10; the client's feedback on that demo is still to come and will be logged on the [Client Communication Log](client-communication-log.md).

---

## 4. Issues / Blockers

| Issue | Impact | Resolution / Next Step |
| --- | --- | --- |
| No merges to main between 16/09 and 05/10 | Frontend follow-ups waited until Sprint 4 | Sprint 4 merged weekly (PRs #30, #33, #37, #40) |
| Our supervisor couldn't open the Progress Report 1 links, draw.io files or repo (17/09) | Our evidence was invisible to the marker | Same day: supervisor added to the workspace and repo. For Progress Report 2, the repo is public and Confluence and Jira are copied into it. |
| The client's 17/09 feedback wasn't written down | We can't show what we changed in response to it | Log every client contact the same day (Sprint 3 retrospective action) |
| The Atlassian free plan doesn't allow public links | Confluence can't be shared outside the team | Snapshots in the repository (docs/snapshots) |
| Sprint 3 PRs merged without a review | Agreed workflow not followed | Every Sprint 4 PR had a teammate review |

---

## 5. Sprint Outcome

**Sprint goal:** 🟡 Partially achieved

**Summary:**

The integration goal was met early: within two days of the sprint starting, the deployed frontend was returning ranked results from the deployed backend, and the client saw the initial prototype at the 17/09 check-in. The team also produced the architecture diagrams, user stories and test cases the supervisor asked for. The client's feedback wasn't written down or turned into cards, and merging stalled after 15/09. Both are picked up in the [Sprint 3 Retrospective](sprint-3-retrospective.md) actions.
