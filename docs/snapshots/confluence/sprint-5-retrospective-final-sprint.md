# Sprint 5 Retrospective (final sprint)

> Snapshot of the Confluence page [Sprint 5 Retrospective (final sprint)](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46923804), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Sprint dates:** \[13/10 - 25/10\]

> **Purpose:** Reflect on how the team worked during the sprint and identify improvements for handover and future work.

---

## 1. What Went Well? 👍

* We ran the crawler on real data and put it on a weekly schedule. 668 real opportunities are live. (KAN-64; /api/status)
* We acted on testing feedback within a day. Andrew's 18/10 testing found mostly US results, 100% eligibility for foreign funders and summaries taken from menus; all three were fixed before the demo. (Slack 18/10; KAN-65, KAN-66, KAN-68)
* We demoed the integrated product to the client at the final presentation on 19/10.
* We checked ethics when asked. Our supervisor asked on 22/10 whether we had the client's consent to use his photo in AI images, and Andrew showed it the same afternoon. (Slack 22/10)
* The repo went public, and Confluence and Jira were copied into it, so markers can see our evidence. Code quality was tightened in CI. (PRs #54 to #57)

---

## 2. What Didn't Go Well? 👎

| Issue | Impact on Sprint |
| --- | --- |
| The first real crawl published 0 of 257 pages | Mock data had hidden quota limits, NUL bytes and messy amounts and deadlines. (Final presentation, "challenges faced") |
| Fixes before the presentation merged without review | 14 PRs between 18/10 and 23/10 skipped review to make the deadline (within PRs #43 to #57) |
| Meetings still weren't recorded | Open client questions (ranking weights, a permanent resident option) kept coming back. (Presentation lessons) |
| Client feedback from 19/10 is still pending | We can't confirm the open ranking decisions yet (KAN-31) |

---

## 3. What Should We Improve? 💡

* Test against real data from the first sprint.
* Record and transcribe every meeting (with the client's permission) and post the summary to Confluence the same day.
* Keep review on even under deadline pressure: a quick review beats none.

---

## 4. Action Items (for handover)

| Action | Owner | Priority | Status |
| --- | --- | --- | --- |
| Log the client's feedback on the 19/10 demo and turn it into cards | Andrew (Product Owner) | High | To do |
| Agree the final ranking weights with the client | Andrew (Product Owner) | High | To do (KAN-31) |
| Choose a licence after checking the IP agreement | Team | Medium | To do (KAN-54) |

See also: [Sprint 5 Review](sprint-5-review-final-sprint.md).
