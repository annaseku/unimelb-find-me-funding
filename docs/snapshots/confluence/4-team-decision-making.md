# 4. Team Decision Making

> Snapshot of the Confluence page [4. Team Decision Making](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33062913), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 4 (Process).** How the team makes and records decisions. The rule from the [Communication Plan](communication-plan.md): if it changes what the team knows, it goes in Confluence. Decisions that affect architecture or long-term direction get an Architecture Decision Record (ADR); smaller ones stay as notes on the relevant page.

## Decision records

| Record | What it decides | Where |
| --- | --- | --- |
| Crawler Architecture Decisions | Ten proposed decisions: hybrid crawling, daily freshness, rules plus LLM, four-state eligibility, four separate ranking scores, index-first search, three stores, dedupe, soft delete, researcher profile | [Confluence](crawler-architecture-decisions.md) |
| ADR-001: Technology Decisions | Stack choice | [Confluence](adr-001-technology-decisions.md) |
| ADR-002: Ranking engine | Four scores, configurable weights, ineligible results sort last | [GitHub docs](https://github.com/annaseku/unimelb-find-me-funding/tree/main/docs) |
| ADR-003: Normaliser | Rules first, LLM fills prose-only fields, provenance per field | [GitHub docs](https://github.com/annaseku/unimelb-find-me-funding/tree/main/docs) |
| Legal, Ethics and Data Handling | Crawling etiquette, terms of service, data kept | [Confluence](legal-ethics-and-data-handling.md) |
| Jira vs GitHub for task tracking | Stay on the KAN board (21/09 retraction) | [Sprint 3 Description + Planning](sprint-3-description-planning.md) |
| Decisions awaiting the client | Six ranking behaviours to confirm with the client | [GitHub: ranking discussion points](https://github.com/annaseku/unimelb-find-me-funding/tree/main/docs) |

## How a decision is made

1. Raised in a standup, on Slack, or in a PR review.
2. Options and trade-offs written down, on the relevant Confluence page or as an ADR draft.
3. Decided at the next standup or sprint planning. Anything that changes client-visible behaviour is marked Proposed until the client confirms it.
4. Recorded, then linked from the Jira card that implements it.

## Still to do

- [ ] Publish ADR-002 and ADR-003 to Confluence (KAN-44)
- [ ] Confirm the ten Crawler Architecture Decisions with the client; they are all still marked Proposed
