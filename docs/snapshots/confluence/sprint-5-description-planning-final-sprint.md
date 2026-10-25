# Sprint 5 Description + Planning (final sprint)

> Snapshot of the Confluence page [Sprint 5 Description + Planning (final sprint)](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/46891027), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Written up on 25/10/2026 from the planning records, not at the time.** Sprint 5 was planned at the team meeting on 13/10 and on the [Presentation](presentation.md) page, but no planning page was made then. This page collects that plan from Slack (12/10 and 13/10), the Presentation page and the KAN board. How it went is in the [Sprint 5 Review](sprint-5-review-final-sprint.md) and [Sprint 5 Retrospective](sprint-5-retrospective-final-sprint.md).

| **Product overview** |  |
| --- | --- |
| **Sprint dates** | 13/10 to 25/10 (weeks 11 and 12) |
| **Planned at** | Team meeting on Zoom, 13/10 at 10am, called by Jummana on Slack on 12/10 "to discuss the presentation and revisit some repository fixes" |
| **Team members** | Andrew Rosen (Product Owner), Jummana Alshimary (Scrum Master), Anna Sekulic, Sophia Kondos, Paige Varney |
| **Board** | [KAN board](https://annaseku01.atlassian.net/jira/software/projects/KAN/boards) |

## Objective

1. Deliver the final presentation on 19/10, with a live demo of the integrated product to the client
2. Finish the repository fixes: the citizenship and FoR dropdowns and the result card UI on the frontend, and the backend running on real crawled data instead of mock data
3. Submit Progress Report 2 by 25/10

## Success metrics

| **Goal** | **Metric** |
| --- | --- |
| Final presentation | Every part has an owner and is ready for the run-through; the presentation fits in 15 minutes |
| Client demo | The integrated product is demoed live to the client on 19/10 |
| Real data | The deployed site serves opportunities from a real crawl, refreshed on a schedule |
| Frontend finished | The dropdown rework and result card UI are merged with CI green |
| Evidence visible to markers | Every Progress Report 2 link opens without a login |

## Milestones

| **Date** | **Milestone** |
| --- | --- |
| 13/10 | Team meeting: presentation parts allocated on the Presentation page |
| 16/10 | Each person's presentation part ready (Friday) |
| 18/10 | Run-through on Zoom (Sunday), and pre-demo testing of the live site |
| 19/10 | Final presentation and live demo to the client |
| 25/10 | Progress Report 2 submitted |

## Owners

| **Work** | **Owner** |
| --- | --- |
| Presentation parts | As allocated on the [Presentation](presentation.md) page |
| Citizenship and FoR dropdowns; result card UI | Paige (PRs #39 and #41; KAN-63) |
| Frontend polish (background image) | Andrew (PR #45) |
| Backend on real data: scheduled crawl, normalise and publish | Anna (KAN-64) |
| Testing the live site before the demo | Andrew |

## Not in this sprint

- Researcher profiles (US09) and expert- or project-specific search (US10). These are could-have stories and were not built.
- Agreeing the final ranking weights with the client (KAN-31). The weights stay at the documented defaults until the client confirms them.

## Related

- [Agile Ceremonies](1-agile-ceremonies.md)
- [Sprint 4 Description + Planning](sprint-4-description-planning.md)
- [Standup Summaries](standup-summaries.md) (weeks 10 to 12 record)
