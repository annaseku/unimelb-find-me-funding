# Standup Summaries

> Snapshot of the Confluence page [Standup Summaries](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/21331973), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

### Standup week 2:

- further clarified requirements of author’s workbench
- discussed swapping projects from author’s workbench to web crawler

### Standup week 3:

- successful switch to web crawler project
- consulted other groups for information we missed from first client meeting
- established group roles
    - Andrew Rosen - Product Owner
    - Jummana Al Shimary - Scrum Master
- started sprint 1 - creating some design artefacts

### Standup week 4:

- rough drafts of system architecture, data flow, user flow, and relevance diagrams
- organised to meet client on the thursday
- started discussing team roles for coding phrase - potentially Andrew, Paige, Sophia for frontend, Anna and Jummana for backend

### Standup week 5:

- discussed information gathered from client during meeting
- developed user stories
- refined product requirements
- research into crawling systems and potential LLM usage for free text search field

### Standup week 6:

- Sprint 2 started
- frontend mockup created on figma
- static frontend created - used unimelb styling and formatting
- backend r&d - crawler prototyping

### Standup week 7:

- Fixed crawler: discovery was silently returning 0 results (DuckDuckGo blocking bot requests) → switched to SerpAPI
- ranking system created
- issues with API key leaked to GitHub - being resolved
- added results and dynamic filtering to frontend (mock data)
- currently no integration between back and front end - normalising system not complete
- introduced CI/CD pipeline
- planning meeting with client next week (thursday likely)
- sprint ends next monday - would like an integrated prototype by then to take to the client
- Regarding Progress Checklist:
    - Create List links and short descriptions of any important points
- RE. Testing: If you want to merge to github make sure it pasts the tests before.


**Week 8 Tutorial notes:**

Sprint 2 Retrospective  
Oral Review  
Sprint 3 begins today: [Sprint 3 Description + Planning](sprint-3-description-planning.md)

##### - 📣📣We will now be switching from Jura to Github for delegating tasks. Please assign all tasks that you plan on doing, and you want others to do accordingly📣📣

- We will be using **supabase**

- Create one high-level architecture diagram showing components and how they communicate; use backend layers: API, business logic, and database access.
- Move project tracking from Jira to GitHub Projects Kanban, with work progressing from backlog through review to done.
- Use GitHub issues for work outside someone’s scope; use pull requests and at least one code review before merging to `main`.
- The GitHub board and PR workflow support the assessment’s industry-level requirements.
- Supabase is the current database option; Render was suggested as a free hosting alternative. A relational database is the fit for the project.
- The new two-week sprint focuses on integrating the frontend and backend, demoing the prototype to the client, then applying feedback.
- Complete the Sprint 2 retrospective today.


**Week 9 Tutorial Notes:**

Feedback notes

- Product meets or exceeds expectations (not the best one) maybe ¾
- Good documentation habits
- team communicates well
- brainstorming - everything is recorded. good.
- ADR used, really common in industry
    - Arcateccutre decision recofrds
- Need to improve
    - Jira tasks
    - hard to find connection between jira tasks and user stories
    - Use case diagram incorrect. see SMD.
    - Estimate size or effort of user stories
    - Add high level architecture diagram. show main components and how they connect. showed her <http://draw.io> 
    - Oral checkin. you can add more detailed technical diagrams

---

### Weeks 10 to 12: activity record (reconstructed)

**Reconstructed on 25/10/2026, not written at the time.** No standup or tutorial notes were taken in weeks 10 to 12. This record was put together afterwards from Slack #all-student, the GitHub pull requests and the Jira KAN board. It lists only what those records show, with dates. It is not meeting minutes: attendance and what was said in calls were not recorded, so they are not listed here. The missing notes are named as a gap in the Sprint 3 to 5 retrospectives.

### Week 10 (05/10 to 11/10): Sprint 4 starts

- 05/10: Andrew created [Sprint 4 Description + Planning](sprint-4-description-planning.md) (05/10 to 12/10).
- 05/10: Anna posted the Sprint 3 retrospective questions in Slack (13 questions, answer in thread). No replies were recorded.
- 05/10 to 06/10: PR #30 (Andrew, frontend dropdowns) merged after Sophia's review; PR #33 (Sophia, format fixes) merged after Andrew's review.
- 05/10: Anna opened PR #37 (Playwright end-to-end tests, coverage in CI, FoR divisions, dropdown dash fix; KAN-50, KAN-58 to KAN-60). Andrew logged KAN-57 (clicking search changes the page format). KAN-10 (email the client to confirm requirements) closed.
- 06/10: Paige worked on the citizenship and FoR dropdowns (PR #38, later replaced by PR #39).

### Week 11 (12/10 to 18/10): Sprint 4 closes, presentation preparation

- 12/10: PR #37 merged after Sophia's review; PR #40 (Andrew, duplicate logo removed) merged after Paige's review. Paige created the [Handover Meeting](handover-meeting.md) page from the week 11 lecture checklist, and KAN-61 to KAN-63.
- 12/10: Paige resolved merge conflicts across the open PRs and asked Anna to review before merging, because she had changed tests for the nested FoR and multi-select citizenship dropdowns.
- 12/10: Jummana scheduled a team Zoom for 13/10 at 10am to discuss the presentation and repository fixes, and asked everyone to bring ideas for making the presentation engaging.
- 13/10: The 10am Zoom ran until about 10:46, when the free plan's 40-minute limit ended it. During it Sophia asked Kerr whether to include all of our diagrams and models, and Paige shared the Canva deck. At 11:04 Jummana posted the [Presentation](presentation.md) page with the part allocation: parts due Friday 16/10, then a run-through on Sunday.
- 17/10: PR #39 (Paige, citizenship and FoR dropdowns) and PR #41 (Paige, search result card UI) merged after Anna's reviews.
- 18/10: The run-through was set for 5pm and moved to 6pm; Andrew posted the Zoom link at 6:06pm and shared the presentation rubric. The team looked at an example presentation and agreed to simplify the slides around the decisions made and why.
- 18/10, 7:21pm and 7:45pm: Andrew tested the live site before the demo and reported that results were mostly American, choosing Australian citizenship changed nothing, card summaries came from menu bars, and foreign funders showed 100% eligible once a filter was applied. Anna fixed these that evening (KAN-65 to KAN-68, PRs #46 to #50; "fixed!" at 8:42pm). These PRs merged without a teammate review.
- 18/10, 9:06pm: Jummana raised an ethics point for the presentation: funder sites do not block the crawler, but they have not explicitly given permission to be crawled either.

### Week 12 (19/10 to 25/10): final presentation and close-out

- 19/10: Final presentation, including the live demo to the client. The same day Anna moved the LLM extractor to OpenRouter and made the refresh faster and safer (KAN-69 to KAN-71, PRs #52 and #53). The client's feedback on the demo has not arrived yet.
- 22/10: Kerr asked whether we had the client's consent to use his photo in AI-generated images. Andrew posted the client's emailed approval at 2:56pm, and Kerr confirmed at 4:12pm.
- 23/10: Repository made public, with read-only copies of Confluence and Jira (PRs #54, #55), and code quality passes on the backend and frontend (PRs #56, #57; KAN-49, KAN-72).
- 25/10: Sprint 3 to 5 reviews and retrospectives, the Supervisor Feedback Log and the ADR-002 to 004 summary published; use case diagram redrawn (KAN-45, PR #59).
