# 12. Deployment

> Snapshot of the Confluence page [12. Deployment](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/33193985), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

**Progress Checklist item 12 (Artefacts).** The Week 9 lecture expects, for web apps, an automated pipeline that deploys stable releases from main to production without manual steps. We have one for both halves of the system, plus a scheduled pipeline that refreshes the data.

## Environments

| Part | Host | URL | Deploys when |
| --- | --- | --- | --- |
| Frontend | GitHub Pages | [annaseku.github.io/unimelb-find-me-funding](https://annaseku.github.io/unimelb-find-me-funding/) | Frontend CI passes on main, then `frontend-cd` builds and publishes |
| API | Render (Docker web service, free plan) | [find-me-funding-api.onrender.com/api/health](https://find-me-funding-api.onrender.com/api/health) | Every push to main; Render rebuilds `backend/Dockerfile` from `render.yaml` |
| API image | GitHub Container Registry | `ghcr.io/annaseku/unimelb-find-me-funding/backend` | Backend CI passes on main, then `backend-cd` pushes `latest` and `sha-<commit>` |
| Database | Supabase Postgres | Supabase dashboard | Schema is created by the repository layer |
| Data refresh | GitHub Actions workflow `Crawl and publish` | Actions tab | Every Sunday 20:00 UTC (Monday morning Melbourne), or by manual dispatch |

## Pipeline

1. Branch from main, open a pull request.
2. CI runs on every PR: ruff, pytest on Python 3.11 to 3.13 against a real Postgres, ranking evals, Docker build, ESLint, Vitest, type-check and build. All seven jobs must pass.
3. A teammate reviews and approves (see [10. Coding](10-coding.md)).
4. Merge to main. That merge is the deploy: no manual step.

main is protected by a GitHub ruleset: no direct pushes, no force pushes, all CI jobs required.

## Scheduled crawl (added 18 October 2026, PR #43)

The data the API serves comes from the crawler, not from hand-written records. Architecture decision 2 asked for a batch refresh; it runs as the GitHub Actions workflow `Crawl and publish` (`.github/workflows/crawl.yml`), which calls `python -m backend.data.refresh` from the repository root: crawl a slice of research areas with the crawler, normalise the rows, publish them to Supabase Postgres.

* Seed list: the 23 ANZSRC 2020 Field of Research divisions (`backend/data/seed_profiles.json`). Each weekly run takes ten of them in rotation, so every division is crawled within three weeks.
* Budget: each division costs four SerpApi searches, so a weekly run is 40 searches and about 175 a month. SerpApi's free plan (serpapi.com/pricing, checked 18 October 2026) allows 250 searches a month and 50 an hour, so the weekly slice fits. A full run of all 23 divisions (`all=true`) is 92 searches in a few minutes and exceeds the hourly cap on the free plan; cover everything with three dispatches an hour apart using the `week` input (0, 1, 2) instead. Weekly replaces the daily cadence in decision 2 for budget reasons; a paid SerpApi plan would allow daily.
* Secrets: `SERPAPI_API_KEY` and `FMF_DATABASE_URL` (the Supabase session-mode pooler URL, the same value the Render dashboard holds) are GitHub repository secrets, plus optional `GEMINI_API_KEY` for the normaliser's extractor. The workflow stops with a clear message if either required secret is missing.
* Until the first successful run with those secrets, the deployed database still holds the 30-record illustrative corpus seeded during development. The product no longer has a mock data source: the backend serves the crawler's SQLite database locally and Postgres when deployed, and the corpus is used only by the ranking evals and the test suites.

## Deployment model

The lecture compares SaaS, PaaS and IaaS and recommends PaaS. We use PaaS throughout: GitHub Pages, Render and Supabase manage the infrastructure, GitHub Actions runs the scheduled crawl, and we manage the application and its data.

## Known limits

* Render's free plan sleeps after 15 minutes idle and takes about a minute to wake. Open `/api/health` before any demo.
* Secrets (SerpApi, Gemini, database URL) live in the Render dashboard and GitHub secrets, never in the repo.
* Rows already in Postgres that no later crawl refreshes are never removed; stale handling (decision 9) is not built yet.

## Releases

Each sprint ends with a tagged GitHub release (v0.3.0 for Sprint 3, and so on) so the client demo can be tied to exact code. The release process is in the repo's `CONTRIBUTING.md`.

Full technical detail, including rollback and the exact secret-setting commands, is in the repo under `docs/12-deployment/`.
