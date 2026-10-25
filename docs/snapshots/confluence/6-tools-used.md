# 6. Tools Used

> Snapshot of the Confluence page [6. Tools Used](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33128449), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 6 (Process).** The Week 1 lecture asks for professional tools that the mentor can access. Our supervisor, Kerr Yuan, has access to the Confluence space, the KAN Jira project and the GitHub repository.

| Purpose | Tool | Where |
| --- | --- | --- |
| Communication | Slack | Team workspace |
| Teamwork and documentation | Confluence | This space |
| Project management | Jira (KAN) | [KAN board](https://annaseku01.atlassian.net/jira/software/projects/KAN/boards) |
| Requirements | AMMBER motivational modeller, draw.io | [Motivational Modelling](motivational-modelling.md) |
| Architecture design | draw.io | Sources in the repo under `docs/09-architectural-design/diagrams/`, rendered in [9. Architectural Design](9-architectural-design.md) |
| Front-end design | Figma | [UI mockups](https://www.figma.com/design/tPui5s6mrlITrowJEwu3GG/Find-Me-Funding---UI-Plan-1) |
| Repository and code review | GitHub (pull requests, protected main) | [unimelb-find-me-funding](https://github.com/annaseku/unimelb-find-me-funding) |
| Linting | ruff (Python), ESLint (TypeScript) | Run in CI on every PR |
| Testing | pytest, Vitest with Testing Library, golden-set ranking evals | [11. Testing](11-testing.md) |
| CI/CD | GitHub Actions | [Actions](https://github.com/annaseku/unimelb-find-me-funding/actions) |
| Hosting | GitHub Pages (frontend), Render (API), Supabase Postgres (database), GitHub Container Registry (API image) | [12. Deployment](12-deployment.md) |
| Product services | SerpApi (search discovery), Google Gemini (field extraction) | Keys held as secrets, never committed |
| Generative AI | Claude Code (Anthropic), plus anything teammates add to the log | [GenAI Usage Log](genai-usage-log.md) |

## Generative AI

The Week 1 lecture requires transparency: any GenAI use must be documented, including summaries, code and test plans. The [GenAI Usage Log](genai-usage-log.md) records what was used, for what, and who checked it. Every PR also states whether AI assistance was used.
