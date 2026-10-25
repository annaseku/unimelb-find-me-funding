# 4. Team Decision Making

> Snapshot of the Confluence page [4. Team Decision Making](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33062913), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 4 (Process).** How the team makes and records decisions. The rule from the [Communication Plan](communication-plan.md): if it changes what the team knows, it goes in Confluence. Decisions that affect architecture or long-term direction get an Architecture Decision Record (ADR); smaller ones stay as notes on the relevant page.

## Decision records

| Record | What it decides | Where |
| --- | --- | --- |
| Crawler Architecture Decisions | Ten proposed decisions: hybrid crawling, daily freshness, rules plus LLM, four-state eligibility, four separate ranking scores, index-first search, three stores, dedupe, soft delete, researcher profile | [Confluence](crawler-architecture-decisions.md) |
| ADR-001: Technology Decisions | Stack choice | [Confluence](adr-001-technology-decisions.md) |
| ADR-002: Ranking engine | Four scores, configurable weights, ineligible results sort last | [Confluence summary](adr-002-to-adr-004-ranking-normaliser-and-deployment.md); [full ADR](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/09-architectural-design/adr/ADR-002-ranking-engine.md) |
| ADR-003: Normaliser | Rules first, LLM fills prose-only fields, provenance per field | [Confluence summary](adr-002-to-adr-004-ranking-normaliser-and-deployment.md); [full ADR](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/09-architectural-design/adr/ADR-003-normaliser.md) |
| ADR-004: Deployment architecture | Render for the API, Supabase Postgres, GitHub Pages, weekly crawl in GitHub Actions | [Confluence summary](adr-002-to-adr-004-ranking-normaliser-and-deployment.md); [full ADR](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/09-architectural-design/adr/ADR-004-deployment-architecture.md) |
| Legal, Ethics and Data Handling | Crawling etiquette, terms of service, data kept | [Confluence](legal-ethics-and-data-handling.md) |
| Jira vs GitHub for task tracking | Stay on the KAN board (21/09 retraction) | [Sprint 3 Description + Planning](sprint-3-description-planning.md) |
| Decisions awaiting the client | Six ranking behaviours to confirm with the client | [Ranking discussion points](https://github.com/annaseku/unimelb-find-me-funding/blob/main/docs/07-requirements/ranking-discussion-points.md) |

## Decisions made this semester, and how

| Date | Decision | How it was made | Record |
| --- | --- | --- | --- |
| 14/09 | Move task tracking to GitHub Projects | Raised by the tutor at the week 8 standup and agreed by the team | [Standup Notes 14/09](standup-notes-1409.md) |
| 21/09 | Reverse that: stay on Jira | The supervisor's feedback asked for a Kanban board plus Slack. The decision and its reason were recorded as a retraction instead of silently changing course | Sprint 3 Description + Planning |
| October | Weekly crawl instead of daily | The free search plan allows 250 searches a month and 50 an hour; the costs of each option were written up in the ADR before choosing | ADR-004 |
| 13/10 to 18/10 | Final presentation structure and who presents each part | Team meeting on 13/10, called on Slack; parts allocated on the Presentation page; diagrams and challenges discussed on Slack on 18/10, with teammates giving their votes | [Presentation](presentation.md) |
| 18/10 | Move the LLM extractor from Gemini to OpenRouter | The free Gemini quota (20 requests a day) blocked the first real crawl | KAN-69, PR #51 |
| 22/10 | Make the repository public | Proposed to the whole team on Slack with a deadline for objections, after a secrets scan; no objections were raised | PRs #54, #55 |

## How a decision is made

1. Raised in a standup, on Slack, or in a PR review.
2. Options and trade-offs written down, on the relevant Confluence page or as an ADR draft.
3. Decided at the next standup or sprint planning. Anything that changes client-visible behaviour is marked Proposed until the client confirms it.
4. Recorded, then linked from the Jira card that implements it.

## Still to do

- [x] Publish ADR-002 to ADR-004 to Confluence (KAN-44)
- [ ] Confirm the ten Crawler Architecture Decisions and the ranking weights with the client (KAN-31)
