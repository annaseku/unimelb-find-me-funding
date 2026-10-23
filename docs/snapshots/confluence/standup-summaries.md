# Standup Summaries

> Snapshot of the Confluence page [Standup Summaries](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/21331973), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

### Standup week 2:

* further clarified requirements of author’s workbench
* discussed swapping projects from author’s workbench to web crawler

### Standup week 3:

* successful switch to web crawler project
* consulted other groups for information we missed from first client meeting
* established group roles

    * Andrew Rosen - Product Owner
    * Jummana Al Shimary - Scrum Master
    
* started sprint 1 - creating some design artefacts

### Standup week 4:

* rough drafts of system architecture, data flow, user flow, and relevance diagrams
* organised to meet client on the thursday
* started discussing team roles for coding phrase - potentially Andrew, Paige, Sophia for frontend, Anna and Jummana for backend

### Standup week 5:

* discussed information gathered from client during meeting
* developed user stories
* refined product requirements
* research into crawling systems and potential LLM usage for free text search field

### Standup week 6:

* Sprint 2 started
* frontend mockup created on figma
* static frontend created - used unimelb styling and formatting
* backend r&d - crawler prototyping

### Standup week 7:

* Fixed crawler: discovery was silently returning 0 results (DuckDuckGo blocking bot requests) → switched to SerpAPI
* ranking system created
* issues with API key leaked to GitHub - being resolved
* added results and dynamic filtering to frontend (mock data)
* currently no integration between back and front end - normalising system not complete
* introduced CI/CD pipeline
* planning meeting with client next week (thursday likely)
* sprint ends next monday - would like an integrated prototype by then to take to the client
* Regarding Progress Checklist:

    * Create List links and short descriptions of any important points
    
* RE. Testing: If you want to merge to github make sure it pasts the tests before.

‌

**Week 8 Tutorial notes:**

Sprint 2 Retrospective  
Oral Review  
Sprint 3 begins today: sprint-3-description-planning.md 

##### - 📣📣We will now be switching from Jura to Github for delegating tasks. Please assign all tasks that you plan on doing, and you want others to do accordingly📣📣

* We will be using **supabase**

* Create one high-level architecture diagram showing components and how they communicate; use backend layers: API, business logic, and database access.
* Move project tracking from Jira to GitHub Projects Kanban, with work progressing from backlog through review to done.
* Use GitHub issues for work outside someone’s scope; use pull requests and at least one code review before merging to `main`.
* The GitHub board and PR workflow support the assessment’s industry-level requirements.
* Supabase is the current database option; Render was suggested as a free hosting alternative. A relational database is the fit for the project.
* The new two-week sprint focuses on integrating the frontend and backend, demoing the prototype to the client, then applying feedback.
* Complete the Sprint 2 retrospective today.

‌

**Week 9 Tutorial Notes:**

Feedback notes

* Product meets or exceeds expectations (not the best one) maybe ¾
* Good documentation habits
* team communicates well
* brainstorming - everything is recorded. good.
* ADR used, really common in industry

    * Arcateccutre decision recofrds
    
* Need to improve

    * Jira tasks
    * hard to find connection between jira tasks and user stories
    * Use case diagram incorrect. see SMD.
    * Estimate size or effort of user stories
    * Add high level architecture diagram. show main components and how they connect. showed her http://draw.io 
    * Oral checkin. you can add more detailed technical diagrams
