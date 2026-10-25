# Sprint 3 Retrospective

> Snapshot of the Confluence page [Sprint 3 Retrospective](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/47022088), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Sprint dates:** \[14/09 - 28/09\]

> **Purpose:** Reflect on how the team worked during the sprint and identify improvements for the next sprint.

---

## 1. What Went Well? 👍

- We integrated early. Andrew, Paige and Jummana held an integration session on 15/09, and the frontend was calling the ranked search API the same day. The backend moved onto Supabase Postgres in the same week. (Slack 15/09; PRs #19 and #22)
- We showed the client our initial prototype two days after integrating, at a Zoom progress check-in on 17/09 (Anna, with the leads of the other teams on this project). ([Client Communication Log](client-communication-log.md))
- We followed through on the Sprint 2 retro's top action item: a full set of architecture diagrams went up on Confluence on 21/09. ([Sprint 2 Retrospective](sprint-2-retrospective.md) action items; [Architecture Overview](architecture-overview-find-me-funding.md))
- We turned the backlog into something traceable: six epics in Jira, stories with acceptance criteria, user stories with IDs, and test cases linked to them. (Jira KAN-12 to KAN-41; [User Stories and Acceptance Criteria](user-stories-and-acceptance-criteria.md); [Test Cases and Reports](test-cases-and-reports.md))
- We responded to our supervisor quickly. When Kerr couldn't open our Progress Report 1 links, draw.io files or repo on 17/09, the team gave Kerr access to the workspace and repo that afternoon. (Slack 17/09)
- We added a PR template so every pull request is described the same way. (PR #16)

---

## 2. What Didn't Go Well? 👎

| Issue | Impact on Sprint |
| --- | --- |
| Nothing was merged between 16/09 and 05/10 | After a strong first two days, progress on main stalled for almost three weeks. (GitHub PR history) |
| The client's feedback from the 17/09 check-in wasn't written down | Nothing from it reached the board, so we can't show what we changed in response. The next full demo was at our final presentation on 19/10, and that feedback is still pending. ([Client Communication Log](client-communication-log.md)) |
| Pull requests were merged without a review | None of the six Sprint 3 PRs had an approving review, even though we agreed in Sprint 2 to review before merging. (GitHub PRs #16 to #23) |
| We switched task tracking from Jira to GitHub, then back to Jira within a week | Tasks lived in two places, and most Jira cards stayed unassigned. (Standup Summaries week 8; Sprint 3 planning retraction 21/09) |
| Meetings weren't recorded or summarised, although the Sprint 2 retro agreed to do this | Decisions from the integration session and client questions weren't written down. (Sprint 2 retro action items) |
| We developed and tested against mock data only | The first real crawl later exposed problems the mock data had hidden: 257 pages crawled, 0 published. (Final presentation, "challenges faced") |
| The sprint review and retrospective weren't held when the sprint closed | Retro questions posted on Slack on 05/10 got no replies. (KAN-52; Slack 05/10) |

---

## 3. What Should We Improve? 💡

- Merge at least once a week, so work doesn't sit on local branches.
- Every pull request gets one teammate's review before it merges.
- Test against real crawled pages from the start, not only mock data.
- When two branches touch the same file, review the merge itself, and turn every bug fix into a test. (Final presentation, "green CI only proves what you test")
- Keep one source of truth for tasks (Jira), and have everyone assign their own cards at planning.
- Agree a fixed check-in rhythm with the client, and log every contact and its feedback the same day.

---

## 4. Key Learnings

- Green CI only proves what you test. A fix we merged on 15/09 was silently undone in a merge conflict on 05/10, and only an end-to-end check caught it.
- Mock data hides real-world problems: programme budgets read as grant amounts, unparseable deadlines, NUL bytes, API quotas.
- Integration is faster when the people building each side work on it together in one session, as on 15/09.

---

## 5. Action Items

| Action | Owner | Priority | Status |
| --- | --- | --- | --- |
| One approving review before every merge to main | Team | High | Done in Sprint 4 (PRs #30, #33, #37 and #40 each reviewed); slipped again from 18/10, when the backend fixes before the presentation merged without review |
| Run the crawler on real data and fix what breaks | Anna | High | Done (weekly crawl live 19/10; KAN-64 to KAN-71) |
| Add a regression test for every bug fix | Team | High | Done (KAN-59 and later fixes) |
| Hold a fixed client check-in and log every contact | Andrew (Product Owner) | High | To do (KAN-42, KAN-51) |
| Estimate stories with planning poker | Jummana (Scrum Master) | Medium | To do (KAN-47) |
| Everyone assigns their own cards at sprint planning | Team | Medium | To do |
| Summarise each meeting on Confluence the same day | Jummana (Scrum Master) | Medium | To do |

---

## 6. Focus for Next Sprint

Demo the integrated product to the client, act on his feedback, and run the product on real crawled data.

See also: [Sprint 3 Review](sprint-3-review.md).
