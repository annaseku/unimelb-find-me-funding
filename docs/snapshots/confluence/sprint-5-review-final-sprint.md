# Sprint 5 Review (final sprint)

> Snapshot of the Confluence page [Sprint 5 Review (final sprint)](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46792705), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

#### **Sprint dates:** \[13/10 - 25/10\]

---

## 1. Sprint Goal

> **Goal:** Get the product ready for the final presentation and handover: real crawled data instead of mock data, the remaining frontend fixes merged, a live demo for the client, and our evidence visible to markers.

Planned at the team meeting on 13/10, which Jummana called on Slack on 12/10 "to discuss the presentation and revisit some repository fixes". Parts and owners are on the [Presentation](presentation.md) page.

### Success Criteria

| Goal | Metric / Success Criteria | Outcome |
| --- | --- | --- |
| Real data | The deployed site serves opportunities from a real crawl, refreshed on a schedule | Complete. 668 crawled opportunities live; the weekly crawl and publish workflow is running (KAN-64) |
| Frontend finished | Dropdown rework and result card UI merged, with CI green | Complete (PRs #39, #41, #45, each reviewed) |
| Client demo | Live demo of the integrated product to the client | Complete. Demoed at the final presentation on 19/10; feedback pending |
| Evidence visible to markers | Every Progress Report 2 link opens without a login | Complete. Repo public, Confluence and Jira copied into it (PRs #54, #55); every link checked while logged out |

---

## 2. Planned Work

1. Final presentation (parts and presenters on the Presentation page)
2. Repository fixes: frontend dropdowns and result cards (Paige, Andrew), backend on real data (Anna)
3. Progress Report 2 checklist

---

## 3. Completed Work + Demonstration

### Completed

* ✅ First real crawl, with the crawl, normalise and publish pipeline put on a weekly schedule; mock data retired (KAN-64)
* ✅ Fixes from Andrew's pre-demo testing on 18/10: results tailored to Australia, overseas funders no longer shown as 100% eligible, summaries taken from page body text instead of menus (KAN-65, KAN-66, KAN-68)
* ✅ AI summaries on every card, and the LLM moved to OpenRouter with timeouts and output caps (KAN-67, KAN-69, KAN-70); refresh made parallel (KAN-71)
* ✅ Citizenship and FoR dropdowns, result card UI and background (PRs #39, #41, #45)
* ✅ Final presentation and live demo to the client (19/10)
* ✅ Supervisor's question on 22/10 about the client's consent to use his photo answered the same day, with evidence (Slack)
* ✅ Repo made public after a secrets scan; Confluence and Jira snapshots added (PRs #54, #55)
* ✅ Code quality pass: three crawler bugs fixed, the crawler tested and linted, the frontend formatted with typed lint, and accessibility fixes (PRs #56, #57; KAN-49, KAN-72)

### Not Completed

* ❌ Client feedback on the 19/10 demo (pending)
* ❌ Final ranking weights agreed with the client (KAN-31)
* ❌ Find an Expert (US10, could-have)

### Demonstration

Live at [annaseku.github.io/unimelb-find-me-funding](https://annaseku.github.io/unimelb-find-me-funding/), shown to the client at the final presentation on 19/10.

---

## 4. Issues / Blockers

| Issue | Impact | Resolution / Next Step |
| --- | --- | --- |
| The first real crawl published 0 of 257 pages | Problems the mock data had hidden: search and LLM quotas, NUL bytes, messy amounts | Quota breaker, NUL stripping and a 3-run weekly schedule; 258 records published on the rerun |
| PRs merged without review before the presentation deadline | 14 PRs from 18/10 to 23/10 had no teammate review | Recorded in the Sprint 5 Retrospective |
| Merge conflicts across the frontend PRs | Paige resolved them on 12/10 before merging | Shorter branches |

---

## 5. Sprint Outcome

**Sprint goal:** 🟢 Achieved

**Summary:**

The product runs on real, weekly refreshed funding data and was demoed live to the client. The remaining frontend work merged with reviews, and every piece of project evidence is now visible to markers. Open items for handover: the client's feedback, the final ranking weights and Find an Expert.
