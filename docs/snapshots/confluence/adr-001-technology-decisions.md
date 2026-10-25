# ADR-001: Technology Decisions

> Snapshot of the Confluence page [ADR-001: Technology Decisions](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/13598721), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

# Backend

# Pros and Cons Table

| Criteria | Next.js (full-stack) | React + Python API |
| --- | --- | --- |
| Language | TypeScript across FE + API | TypeScript (FE) + Python (BE) |
| Setup speed | Fast — routing, API routes, deploy built in | Slower — two codebases, two pipelines |
| Crawler fit | API routes are request/response; still needs a separate worker/cron for real crawling | Natural — crawler is just another Python process alongside the API |
| Scraping ecosystem | Playwright, Cheerio, Crawlee — decent but less mature than Python's | Scrapy, BeautifulSoup — strongest option for this project |
| Future ML/eligibility NLP | Weaker — Python has the stronger libraries | Strong — pandas, spaCy, full Python data/ML stack |
| Team fit (2 FE / 3 BE) | Blurs the split — one shared codebase/language | Matches naturally — each team owns its own codebase |
| Mobile app later | Workable, but API routes weren't designed as a standalone service | Easy — API is decoupled from any client |
| Setup overhead | Low — one repo, one deploy pipeline | Higher — more initial config, two languages to coordinate |

Given how much of this project hinges on crawling and eligibility logic, **React + Python API** is the stronger fit on balance
