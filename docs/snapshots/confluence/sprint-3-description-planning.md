# Sprint 3 Description + Planning

> Snapshot of the Confluence page [Sprint 3 Description + Planning](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/24969238), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

| **Product overview** |
| --- |
| **Target date** | 28 Sep 2026 |
| --- | --- |
| **Document status** | in progress |
| --- | --- |
| **Team members** |  |
| --- | --- |
| **Quick links** |
| --- |
| **Designs** | architecture-overview-find-me-funding.md |
| --- | --- |
| **Board** | [KAN Kanban board](https://annaseku01.atlassian.net/jira/software/projects/KAN/boards) |
| --- | --- |

## Objective

**Retraction —** 21 Sep 2026**.** An earlier version of this page announced that the team would switch from Jira to GitHub for delegating tasks. **That decision is withdrawn.**

Our supervisor's feedback asked us to use a Kanban board and Slack for communication. The [KAN Kanban board](https://annaseku01.atlassian.net/jira/software/projects/KAN/boards) is therefore the source of truth for task assignment and status from this point on. GitHub remains where the code and pull requests live; the two are linked by issue key, so a branch named `KAN-42-short-description` and commits referencing `KAN-42` surface on the Jira issue automatically.

For a file database we are using **Supabase** Postgres. Render was considered and rejected as the database host — see the hosting and persistence ADR for the reasoning.

1. Finish prototype to present to client

    1. Finalise front end
    2. Finalise back end
    3. Integrate front and back end
    
2. Apply suggested changes from the client demo

## Success metrics

| **Goal** | **Metric** |
| --- | --- |
| Finalise front end | All Sprint 3 frontend cards on the KAN board are Done, and `npm run lint`, `npm test` and `npm run build` pass in CI on `main` |
| Finalise back end | All Sprint 3 backend cards are Done, and pytest plus the ranking evals pass in CI on `main` across Python 3.11–3.13 |
| Integrate front and back end | The deployed frontend returns ranked results from the deployed API for at least three distinct search profiles, demonstrated live in the client demo |
| Apply suggested changes | Every item of the client's demo feedback is logged on the Client Communication Log with a named owner and a card on the board |

The previous version of this table measured success as "the team agrees they're satisfied". That cannot be assessed by anyone outside the team, so the metrics above were rewritten as conditions that can be checked. _Team: confirm these are the right bars before the sprint closes._

## Milestones

- [x] Finish prototype to present to client
- [ ] Finalise front end
- [ ] Finalise back end
- [ ] Integrate front and back end
- [ ] Apply suggested changes

## Out of scope

* User researcher profiles
* Finished project

## Design

* architecture-overview-find-me-funding.md — layered system design diagram, sequence diagrams and use case diagram
* Editable draw.io sources live in the repository under `docs/diagrams/`

## Related

* communication-plan.md
* legal-ethics-and-data-handling.md
