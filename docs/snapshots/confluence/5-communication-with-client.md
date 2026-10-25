# 5. Communication with Client

> Snapshot of the Confluence page [5. Communication with Client](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33095681), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 5 (Process).** Every contact with the client (UoM Research Office): what was asked, what was agreed, and what changed as a result. The Week 3 lecture expects requirements to be approved by the client and client interactions to be positive, productive and lightweight.

## Meetings and demos

| Date | Meeting | Notes |
| --- | --- | --- |
| 20/08 | Client check-in | [Questions and answers](client-meeting-2008-questions-and-answers.md), [post-meeting notes](client-meeting-2008-post-meeting-notes.md) |
| 17/09 | Progress check-in on Zoom (Anna, with the client and the leads of the other teams on this project): our initial prototype shown | The client's feedback wasn't written up at the time. [Client Communication Log](client-communication-log.md) |
| 19/10 | Final presentation with a live demo of the integrated product | Feedback pending. [Client Communication Log](client-communication-log.md) |

Every email, meeting and demo is logged on the [Client Communication Log](client-communication-log.md), with the outcome and the Jira card it produced.

## How the client's requirements shaped the product

| Client requirement (20/08) | Where it shows up |
| --- | --- |
| Eligibility is the top priority | Eligibility has the highest default weight (0.4), and likely-ineligible results always sort last (ADR-002) |
| Uncertain results stay in | Four eligibility states, including "unknown", instead of yes or no |
| Longer lead time to a deadline is better | The deadline score rises with days remaining |
| Results tailored to Australian opportunities | Location check and Australian search settings (KAN-65), verified in testing before the 19/10 demo |
| Discovery across the web, not a fixed list | Search-driven discovery in the crawler (US07) |

## Still to do

* [ ] Log the client's feedback on the 19/10 demo, with an owner and a card for each item (KAN-51)
* [ ] Take the six open ranking decisions to the client (KAN-31)
* [ ] Agree a regular check-in rhythm for any further work (KAN-42)
