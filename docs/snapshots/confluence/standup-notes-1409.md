# Standup Notes 14/09

> Snapshot of the Confluence page [Standup Notes 14/09](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/26378243), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

Architecture Documentation

* One overall system design diagram needed for better documentation

    * Chris asked for a single document covering all architecture, classes, and communication
    * High-level architecture diagram sufficient at the top level
    * No class diagrams needed (not using OOP)
    
* Backend layered structure recommended:

    1. API layer (links to frontend)
    2. Function/logic layer (main business logic)
    3. Database access layer
    

# Project Workflow and GitHub Kanban

* Switching from Jira to GitHub Projects Kanban board

    * GitHub board integrates naturally with PRs and merging
    * Industry workflow: backlog → self-assign → to-do → in progress → in review → done → merge to main
    
* Git issues used when a problem is noticed but outside one’s own scope, assigned to the relevant person
* All team members added to the GitHub repo project board:

    * Cello, Rosin, Sophia (Scondos13), Jumana (Jal Shimari)
    
* PR template created; GitHub auto-prefills description on any PR opened against main

# Code Review Practice

* Code review required before merging to main (industry standard)

    * At least one reviewer must approve before merge
    * Noted as a significant part of the assessment rubric (industry-level column, 4-point section)
    
* PR and Git issue templates recommended with consistent format across the team

# Database and Hosting

* Currently using Supabase (free tier: 2 projects per org)

    * Paused projects don’t lose data but stop accepting changes after 30 days inactive
    * Need a team member with a free Supabase slot if current limit is hit
    
* Render flagged as a free alternative for hosting frontend, backend, and database together

    * Caveat: process sleeps after 15 minutes of inactivity, \~1 minute to wake
    
* Relational database (tables and rows) confirmed as the right fit for this project

# Sprint Planning

* New sprint starts today; 2-week duration proposed
* Two main sprint objectives:

    1. Finish and integrate the prototype (frontend + backend) to present to the client
    2. Incorporate client feedback and apply changes
    
* Sprint 2 retrospective to be done today
* Use Kanban board and Slack for team comms going forward
* Still need to meet with the client more regularly

# Next Steps

* **Create one overall system architecture diagram.** Covers all components and how they communicate, to address Chris's documentation feedback.
* **Migrate project tracking to GitHub Kanban and adopt PR-based code review workflow.** All team members added to the repo; enforce PR template and code review before merging to main.
* **Complete sprint 2 retrospective.** To be done today.
* **Finish prototype integration and schedule client demo.** Frontend and backend largely done; need to integrate and present to the client this sprint.
