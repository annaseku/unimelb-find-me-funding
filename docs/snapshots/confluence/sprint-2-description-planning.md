# Sprint 2 Description + Planning

> Snapshot of the Confluence page [Sprint 2 Description + Planning](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/11632651), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

| **Product overview** |
| --- |
| **Target date** | 14th of September 2026 |
| --- | --- |
| **Document status** | IN PROGRESS |
| --- | --- |
| **Team members** |  |
| --- | --- |
| **Quick links** |
| --- |
| **Designs** | https://www.figma.com/design/tPui5s6mrlITrowJEwu3GG/Find-Me-Funding---UI-Plan-1?t=CK3v4BZur3T8BRXr-1  |
| --- | --- |
| **Work tracker** | https://annaseku01.atlassian.net/jira/software/projects/KAN/boards/2?filter=&groupBy=none&atlOrigin=eyJpIjoiNTBlZDg1NTI5ZjI2NDlkMzk3YjAwYjc3ZTg0MWUzOTgiLCJwIjoiaiJ9  |
| --- | --- |

## Objective

1. Clean and finalize requirements.

* Behaviour Diagram
* User Stories
* Base List + added requirements after discussion  

2. Create the Front-end Prototype for the website. 
    * All search options
    * UI - links to settings, profile
    
3. Make backend prototypes

    1. Ranker 
    2. Crawler 
    
4. Integrate backend with frontend  

## Success metrics

Front End:

| **Goal** | **Metric** |
| --- | --- |
| Using React create a webpage with interactable icons | Functional React webpage created with 100% of planned icons implemented and each icon performs its intended interaction when clicked/hovered. |
| Create rough prototype (mockup) of web page in Figma/Canva, to understand components required in UI (Menu, Navigation, Search Bar, Dropdown Menus etc.) | 1 completed mockup per page covering the main UI components: navigation/menu, search bar, dropdown menus, icons and results area. Prototype reviewed by the frontend team. |
| Implement components with mock up data to display functionality | All planned core components implemented in React using mock data, with dropdowns, search/input fields and buttons demonstrating their intended behaviour. |
| Create storyboards for next client meeting, to verify decisions made in the front end | Completed storyboard/presentation showing the user's journey through the webpage and documenting key frontend design decisions/questions for client feedback. |
| Integrate frontend with backend for basic static crawling | React frontend successfully makes at least 1 request to the backend and displays the returned crawling data correctly on the webpage using the agreed data format. |

Back End:

| **Goal** | **Metric** |
| --- | --- |
|  |  |
|  |  |

## Assumptions

* Do we Display results that are not perfectly eligible?

    * Assumption: We’ll include a tick box next to each bubble result allowing the researcher to make certain options Mandatory vs Preferred.
    * Assumption: We won’t require any bubbles to be filled in, each 
    

## Requirements

| **Requirement** | **User Story** | **Importance** | **Team Members** | **Notes** |  |
| --- | --- | --- | --- | --- | --- |
| Implement home page and search page layout and routing | I want an easy-to-use interface to input my search specifics. So that I can feel confident and motivated about my searching for funding for my product | HIGH   |  |  |  |
| Implement dynamic drop-down selectors for FoR, ToA, Citizenship, Employer Type, and Career Stage | I want to select my specific research classifications (FoR, ToA) and personal attributes (citizenship, employer type, career stage) using structured drop-down menus. So that I can filter out funding opportunities that don't apply to my background | HIGH  |  |  |  |
| Develop a ranking algorithm evaluating eligibility, match, value, and deadline, defaulting to display top 10 results |  I want to view a list of top 10 funding opportunities ranked by overall appeal. So that I can immediately prioritize applying for the most relevant and profitable grants  | HIGH |   |   |  |
| Display clickable source links next to badge indicators showing the four core metric ratings for each card item | I want to view direct links alongside a breakdown of scores (Eligibility, Match, Value, Time to Deadline) for each grant. So that I can quickly navigate to the source page and understand why a specific grant got its ranking | HIGH |  |  |  |
| Build an automated web crawler and parser that extracts grant parameters into a structured database | I want to the platform to display up to date opportunities without manual data entry | HIGH   |  |  |  |

## Out of Scope

* profiles
* LLM implementation
* A working project/profile feature - could be within scope
* finalised dynamic crawler

‌

## Design

_(Image not included in this snapshot; see the live Confluence page.)_

_(Image not included in this snapshot; see the live Confluence page.)_
‌

‌

## Open questions

| **Question** | **Answer** | **Date Answered** |
| --- | --- | --- |
| What functionality should the search/filter components support? | Ability to select up to as many search criteria in one search. Many selections will lead to broader selection of results, but autonomy lies with user to decide how selective to be | 8/31/2026 |
| What information should be displayed for each funding opportunity? | Brief funding description, relevant selection criteria (i.e. show user what corresponding search lead to the result being shown), eligibility ranking (likely eligible, somewhat eligible, unlikely eligible) | 8/31/2026   |
| Is current UI consistent with client vision? | TBC  Storyboards to demonstrate intended front end relevant to user stories in next **Sprint Review** with client. | TBC |

## Reference Links


‌
