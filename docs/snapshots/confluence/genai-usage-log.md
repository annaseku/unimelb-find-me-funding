# GenAI Usage Log

> Snapshot of the Confluence page [GenAI Usage Log](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33488897), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

The Week 1 lecture: COMP30022 is neither for nor against GenAI, but any use must be transparent and documented, including summaries, code and test plans, and the team is responsible for everything it submits. Week 2 suggests the Scrum Master track what is AI-produced and what is manual, and the risk profile of each.

**Everyone: add a row whenever you use a GenAI tool on project work.** From 24/09 every pull request also answers "GenAI use" in the PR template.

## How we use it

* A human asks for the change, reviews every line before it is committed, and is accountable for it. The committer is the reviewer of record for AI-drafted code.
* AI-assisted commits carry a `Co-Authored-By` trailer naming the model, so the git history shows exactly which commits had AI help.
* All code, AI-assisted or not, goes through the same gates: CI (lint, 218 backend tests on three Python versions, frontend tests, type-check, build) and pull request review.
* We do not paste secrets, client confidential material or personal data into GenAI tools.

## Log

| Date | Who | Tool | Used for | Artefacts | Checked by |
| --- | --- | --- | --- | --- | --- |
| 06/09 to 15/09 | Anna Sekulic | Claude Code (Anthropic) | Ranking engine, search API, evals, normaliser, CI/CD workflows, frontend test suite, Supabase repository, README, ADR-002 and ADR-003, API contract, PR template | 38 commits on main with a Claude `Co-Authored-By` trailer; see `git log --grep` or the trailers on GitHub | Anna Sekulic (review before commit); CI; PR review |
| 15/09 | Jummana Alshimary | Claude | Fix for mangled dash characters in the Result and Dropdown components (PR #23) | 1 commit | Jummana Alshimary; CI |
| 21/09 | Anna Sekulic | Claude Code | Draft architecture diagram set (draw.io), Architecture Overview page, Communication Plan, Legal, Ethics and Data Handling page, Sprint 3 page edits | Confluence pages under 3, 4 and 9 | Anna to confirm the exact list; team to review the diagrams |
| 24/09 | Anna Sekulic | Claude Code | Extracted the COMP30022 lecture requirements; reorganised Confluence into the 12 Progress Checklist sections; drafted the test plan, test cases, user stories with acceptance criteria, this log, CONTRIBUTING.md and draft story points | Pages 1 to 12, the repo PR of 24/09, Jira story points labelled `estimate-draft` | Anna Sekulic; team to review the drafts |
|  | Paige, Sophia, Andrew, Jummana |  | Add your own uses here (for example ChatGPT, Copilot, Figma AI) |  |  |

## Risk profile

| Area | Share AI-assisted | Risk | Mitigation |
| --- | --- | --- | --- |
| Backend ranking, normaliser, API | High | Plausible but wrong logic | Golden-set evals, 218 unit and integration tests, client-facing behaviours listed for confirmation rather than assumed |
| Crawler | Low |  |  |
| Frontend components | Low; tests AI-assisted | Tests that pass without proving much | Reviewer checks each test would fail if the behaviour broke |
| Documentation | Medium | Confident statements that are not true | Every page marked Draft until a teammate confirms it |
