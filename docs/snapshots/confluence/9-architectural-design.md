# 9. Architectural Design

> Snapshot of the Confluence page [9. Architectural Design](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/10682389), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 9 (Artefacts).** The Week 4 lecture uses Kruchten's 4+1 model: logical, process, development and physical views, tied together by scenarios. Start with the [Architecture Overview](architecture-overview-find-me-funding.md) and the [High Level Architecture](high-level-architecture.md) diagram (the one overall diagram the supervisor asked for). Every diagram's editable draw.io source is in the repo under `docs/09-architectural-design/diagrams/`.

## Diagrams by 4+1 view

| View | Question it answers | Diagrams |
| --- | --- | --- |
| Logical | What are the parts and how do they relate? | [Domain Class Diagram](domain-class-diagram.md), [Database ER Diagram](database-er-diagram.md) |
| Process | What happens at runtime? | [Sequence: Search for Funding](sequence-diagram-search-for-funding.md), [Sequence: Discover and Ingest](sequence-diagram-discover-and-ingest.md), [Ranking Activity Diagram](ranking-activity-diagram.md), [Opportunity Lifecycle](opportunity-lifecycle-state-diagram.md) |
| Development | How is the code organised? | [System Architecture (Layered)](system-architecture-layered.md), [Component Diagram](component-diagram.md), [API Contract](api-contract.md), goals and constraints below |
| Physical | Where does it run? | [Deployment Diagram](deployment-diagram.md) |
| Scenarios (+1) | Which use cases drive it? | [Use Case Diagram](use-case-diagram.md) |

## Architecture goals and constraints

The Week 4 lecture's What / Why / How table for the requirements that shape the architecture.

| Requirement | What | Why | How |
| --- | --- | --- | --- |
| Eligibility accuracy | Never rule a researcher in or out on a guess | Eligibility is the client's top priority (20/08 meeting) | Four states (eligible, potentially eligible, unknown, likely ineligible); deterministic rules decide simple yes/no checks, never the LLM alone |
| Explainability | Every result shows why it ranked where it did | Researchers must trust the ranking (FR-17) | Four separate scores, each with a label and reasons, combined by configurable weights |
| Coverage | Find funders beyond a fixed list | The brief rules out a hardcoded list (FR-02) | Search-based discovery (SerpApi) plus seeded sources |
| Freshness | Deadlines and amounts stay current | Funding data is time-sensitive | Daily crawl, re-crawl when data goes stale, soft delete when a deadline passes |
| Politeness and legality | Crawl without breaching site rules | Ethical and terms-of-service obligations | robots.txt gate on every fetch; descriptive User-Agent (KAN-22); see Legal, Ethics and Data Handling |
| Confidentiality | No secrets or personal data exposed | Leaked API key incident in week 7 | Keys only in GitHub secrets and the Render dashboard; `.env` gitignored; no personal researcher data stored in this release |
| Data persistence | Opportunities survive restarts and redeploys | The index is the product | Supabase Postgres behind a repository interface, so the store can be swapped |
| Maintainability | The team can change one part without breaking another | Five developers, two sub-teams | Layered backend (API, logic, data access), typed models, one test file per module, CI on every PR |
| Cost | Runs for free | Student project, no budget | PaaS free tiers: GitHub Pages, Render, Supabase |

## Decision records

See [4. Team Decision Making](4-team-decision-making.md) for the ADRs behind these choices. Early design work: [System Design Brainstorm](web-crawler-system-design-brainstorm.md), [General Crawler Architecture](general-crawler-architecture.md).
