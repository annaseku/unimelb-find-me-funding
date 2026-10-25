# Presentation

> Snapshot of the Confluence page [Presentation](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/42106882), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

### Canva Link

https://canva.link/6053t0masp5cfeh 

### Entertainment

* Have a clip of phd students from unimelb complaining about not being able to find funding for their research

    * Ask them whats ur name where do you study and whats ur phd in!
    
* Make short-form video to present the problem \~45s-1min

### Part Allocation

| # | Part | Presenter(s) | Time | Rubric component | What the slides and talk cover |
| --- | --- | --- | --- | --- | --- |
| 1 | **Intro + hook video** | Jummana | 1:30 | Team | Title and agenda listing the parts. The PhD students video (name, where they study, PhD topic, funding complaint). Team and roles slide. Handover: "Those students are who we built this for." |
| 2a | **Client and Requirements (project brief)** | Andrew | 1:00 | Client & Requirements | The client and the "Google for funding" vision. The client rejected a fixed site list because it "defeats the purpose", so dynamic discovery is required. The inputs, the four ranking criteria, the top 10 output with links and ratings. Eligibility is the top priority. Assumptions where the brief was silent (ranking weights, "eligibility unknown", showing ineligible results). |
| 2b | **User stories** | Sophia | 0:45 | Client & Requirements | 3-4 short stories tied to app features (e.g. a postdoc who only wants eligible funding, or someone searching a colleague's profile). Links back to the students in the video. |
| 3a | **Technologies: frontend** | Paige | 0:45 | Technologies | Framework choice and why. The input form (dropdowns, multi-select, free text). The results page (top 10, load more, links, four visible ratings). (Collaboration tools moved to 3b, Anna, with 15 s of time.) |
| 3b | **Technologies: backend + collaboration** | Anna | 1:30 | Technologies, Collaboration tools, Justifications | Architecture diagram (crawler → database/index → eligibility and ranking → frontend). Database and schema. Crawler: scheduled crawl plus index instead of live crawling or a fixed list. Eligibility classification and the weighting of the four criteria. For every choice: chosen, rejected, why. Collaboration tools (from 3a): Slack for day-to-day chat, the Jira KAN board for tasks, Confluence for decisions and meeting records, GitHub pull requests for code review. Git and branching: everyone works on their own branch, named for the change or its KAN ticket (feat/, fix/, ci/, docs/, KAN-64-...). How merges are handled: main is protected, so every change goes through a PR with one approving review and all seven CI checks green, with no force pushes. CI/CD: Backend CI (ruff, pytest on Python 3.11 to 3.13, Docker build) and Frontend CI (eslint, type-check and build, Playwright end to end) run on every PR; merging to main deploys the frontend to GitHub Pages and publishes the backend image; a weekly Crawl and publish workflow refreshes the database. |
| 4 | **Live demo** | Sophia | 1:30 | Content (beyond required) | A realistic profile run end to end: fill the form, see the top 10, point out the four ratings, click a link, load more. Show one extra feature. Have a recorded backup. |
| 5 | **Challenges faced and lessons learned** | One presenter (to be decided) | 1:30  
i think this should be much longer | Key Challenges, Lessons Learned | Challenges: crawling at scale as the headline, then merge conflicts, mock data, vague eligibility rules, with what you did about each. Lessons: **everyone** writes 2-3 items (what happened, what we learned, what we'd do differently), and the presenter picks the best 5-6, credited by name. |
| 6 | **End** | Jummana | 0:45 | Structure / Clarity | What we're most proud of, future direction (mobile app, saved profiles, better eligibility, fresher data, etc), where the project goes next, questions. |

### Part 5: lessons learned (everyone adds 2-3)

**Anna**

* **Real pages give messy data.** After the first real crawl, the amount rule took the largest dollar figure on a page, so whole programme budgets showed up as grant amounts, and most pages had no deadline we could parse. Learned: eligibility, amount and deadline are often vague or missing, which is why we use four eligibility states (eligible / potentially eligible / unknown / likely ineligible) instead of yes/no. Next time: test against real crawled pages early instead of relying on hand-written mock data.
* **Record and transcribe every meeting.** In the Sprint 2 retro we agreed to record important meetings and keep transcripts and summary notes, but it never happened. We lost track of where everyone was, and client answers (ranking weights, a separate permanent resident option) kept coming back as open questions. Next time: use a transcription tool for every internal and client meeting from week 1 (asking the client first), and paste the summary and action items into Confluence the same day.
