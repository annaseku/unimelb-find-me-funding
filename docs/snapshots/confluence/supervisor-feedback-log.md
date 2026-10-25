# Supervisor Feedback Log

> Snapshot of the Confluence page [Supervisor Feedback Log](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46825473), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

Every piece of feedback from our supervisor and tutors, what we changed in response, and where to see it. Sources: [Standup Summaries](standup-summaries.md) (tutorial notes), [Standup Notes 14/09](standup-notes-1409.md) and the team Slack.

| Date | Feedback | What we did | Evidence | Status |
| --- | --- | --- | --- | --- |
| Week 7 | Make sure changes pass the tests before merging to GitHub | All seven CI checks became required status checks on main; nothing merges red | Ruleset "Protect main"; [CONTRIBUTING.md](https://github.com/annaseku/unimelb-find-me-funding/blob/main/CONTRIBUTING.md) | ✅ Done |
| Week 8 (14/09) | One overall system architecture diagram showing components and how they communicate, with a layered backend (API, logic, data access) | High-level and layered architecture diagrams plus the full UML set, published 21/09 | [Architecture Overview](architecture-overview-find-me-funding.md), KAN-41 | ✅ Done |
| Week 8 (14/09) | Use a Kanban board, and Slack for team communication | Tracking stayed on the Jira KAN board (21/09 decision recorded); Slack #all-student for team communication | [Sprint 3 Description + Planning](sprint-3-description-planning.md), [Communication Plan](communication-plan.md) | ✅ Done |
| Week 8 (14/09) | At least one code review before merging to main; PR and issue templates | PR template (14/09), bug report template; main requires one approving review. Every Sprint 4 PR was reviewed (#30, #33, #37, #40). | PR #16; [.github](https://github.com/annaseku/unimelb-find-me-funding/tree/main/.github) | 🟡 In place; skipped under deadline 18/10 to 23/10 |
| Week 8 (14/09) | Supabase as the database, and Render as a free host | Supabase Postgres serves the API (PR #19); API hosted on Render | ADR-004 Deployment architecture | ✅ Done |
| Week 9 | Hard to connect Jira tasks to user stories | User stories given IDs (US01 to US10), each story mapped to its Jira cards and test cases, and cards labelled with their story ID | [User Stories and Acceptance Criteria](user-stories-and-acceptance-criteria.md) | ✅ Done |
| Week 9 | Estimate the size or effort of user stories | Draft Fibonacci estimates for every story; planning poker to confirm them not yet held | User Stories and Acceptance Criteria; KAN-47 | 🟡 Partly done |
| Week 9 | Use case diagram incorrect | Logged as KAN-45 | KAN-45 | ❌ Open |
| Week 9 | Add a high-level architecture diagram | As week 8 above | Architecture Overview | ✅ Done |
| Week 9 | More detailed technical diagrams for the oral check-in | Final presentation used the architecture, decisions, collaboration and sequence diagrams | [Presentation](presentation.md) | ✅ Done |
| 17/09 (Slack) | Progress Report 1 links don't open for the supervisor; draw.io files empty; no access to the GitHub repo | Same day: supervisor added to the Confluence workspace and the GitHub repo. For Progress Report 2: repo made public, and Confluence and Jira copied into it so every link opens without a login | [docs/snapshots](https://github.com/annaseku/unimelb-find-me-funding/tree/main/docs/snapshots), PRs #54, #55 | ✅ Done |
| 22/10 (Slack) | Check we had the client's consent before using his photo to generate AI images | Andrew shared the consent evidence the same afternoon; supervisor confirmed | Slack #all-student 22/10 | ✅ Done |

## Feedback from inside the team

| Date | Feedback | What we did | Evidence |
| --- | --- | --- | --- |
| 18/10 | Andrew's pre-demo testing: results not tailored to Australia, foreign funders shown 100% eligible, summaries taken from menu bars | All three fixed before the demo | KAN-65, KAN-66, KAN-68 |
| 12/10 | Paige asked for a review of her PR before merging, because she had changed tests | Reviewed and merged with an approving review | PR #39 |
