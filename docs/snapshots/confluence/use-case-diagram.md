# Use Case Diagram

> Snapshot of the Confluence page [Use Case Diagram](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/31883265), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Version 2, 25/10/2026.** Redrawn in response to week 9 tutor feedback (KAN-45) and Progress Report 1 feedback, which said the earlier diagram did not follow use case notation. It now uses the UML notation taught in SMD: actors outside the system boundary, use cases named as verbs, solid associations between actors and use cases, and dashed «include» and «extend» relationships. Each use case is tagged with the user story it delivers (US01 to US08).

![use case diagram](images/use-case-diagram.png)

## Actors

- **Researcher** (primary): searches, reads the ratings, loads more results and opens the funder's page.
- **Scheduler** (timer): starts the weekly refresh of the funding index.
- **Funder website** (external system): the pages that are discovered and checked against robots.txt.
- **LLM service** (external system): extracts fields that only appear in prose.

## What changed from version 1

- Removed "Adjust ranking weights": weights are set in configuration, not by the researcher.
- Removed the Research Office Administrator and "Review indexed opportunities": not built.
- Folded "Filter by eligibility and career stage" into "Search for funding opportunities", since filters are part of the search form.
- Added "Load more results" as an «extend» of search, "View a result's ratings", "Open the funder's page", and the LLM service as a secondary actor.
- US09 (researcher profile) and US10 (expert- and project-specific search) are could-have stories that were not built, so they are not shown.

Editable source: `docs/09-architectural-design/diagrams/use-case-diagram.drawio` in the repository, with the PNG beside it. Where this page and the repository disagree, the repository wins.

Part of the architecture set: start at [Architecture Overview — Find Me Funding](architecture-overview-find-me-funding.md).
