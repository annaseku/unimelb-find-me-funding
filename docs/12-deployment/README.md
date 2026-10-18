# Deployment

A merge to main is a deploy. There is no manual step.

| Part | Host | Triggered by | Defined in |
| --- | --- | --- | --- |
| Frontend | GitHub Pages: https://annaseku.github.io/unimelb-find-me-funding/ | Frontend CI passing on main | `.github/workflows/frontend-cd.yml` |
| API | Render web service `find-me-funding-api`: https://find-me-funding-api.onrender.com | Any push to main (Render auto-deploy) | `render.yaml`, `backend/Dockerfile` |
| API image | `ghcr.io/annaseku/unimelb-find-me-funding/backend`, tagged `latest` and `sha-<commit>` | Backend CI passing on main | `.github/workflows/backend-cd.yml` |
| Database | Supabase Postgres | `CREATE TABLE IF NOT EXISTS` in `backend/data/postgres_repository.py` | `backend/data/` |
| Crawl, normalise and publish | GitHub Actions `Crawl and publish`, weekly | schedule or manual dispatch | `.github/workflows/crawl.yml`, `backend/data/refresh.py` |

Decision record: `docs/09-architectural-design/adr/ADR-004-deployment-architecture.md`.

## Pipeline

1. Pull request opened: Backend CI (ruff, pytest on 3.11 to 3.13 against Postgres, ranking evals, Docker build) and Frontend CI (ESLint, Vitest, type-check and build) run.
2. The main ruleset blocks merge until all seven jobs pass and one reviewer approves.
3. Merge: Render rebuilds the API, `frontend-cd` publishes the site, `backend-cd` pushes the image.

## Configuration and secrets

- Frontend build: `VITE_API_BASE_URL` (repository variable; defaults to the Render URL).
- API: `FMF_DATA_SOURCE`, `FMF_DATABASE_URL` and `GEMINI_API_KEY` are declared in `render.yaml`; API configuration and secret values live in the Render dashboard. The crawl workflow reads `SERPAPI_API_KEY`, `FMF_DATABASE_URL` and optional `GEMINI_API_KEY` from GitHub repository secrets. Never commit them. See `backend/.env.example` for the full list.

## Scheduled crawl

GitHub Actions `Crawl and publish` runs every Sunday at 20:00 UTC (Monday morning in Melbourne), or on manual dispatch. From the repository root, `backend.data.refresh` crawls a rotating slice of research areas with the crawler, normalises the SQLite rows, then publishes them to Supabase Postgres for the deployed API. The workflow retains `funding_crawler.db` as an artifact for seven days, including after a failed run when a database was created. Until the first successful run, the deployed table still holds the 30-record evals corpus.

Set these GitHub repository secrets using the interactive prompts:

```bash
gh secret set SERPAPI_API_KEY
gh secret set FMF_DATABASE_URL
# Optional: enables the Gemini extractor during normalisation.
gh secret set GEMINI_API_KEY
```

`FMF_DATABASE_URL` must be the Supabase session-mode pooler URL on port 5432, with the same value as the Render dashboard. `SERPAPI_API_KEY` enables discovery; without `GEMINI_API_KEY`, the normaliser uses its rules alone. With it, Gemini's free tier covers about 20 pages a day and the run continues rules-only once that quota answers 429, so a paid Gemini key is what makes the extractor cover a whole slice.

The seed file contains all 23 ANZSRC 2020 divisions, matching the frontend names. Each week selects ten profiles starting at `(ISO week * 10) % 23`, wrapping at the end. Each profile generates four SerpApi searches: 40 per weekly run, about 175 per month. SerpApi's free plan (serpapi.com/pricing, checked 18 October 2026) allows 250 searches a month at no more than 50 an hour, so the weekly slice fits and the rotation reaches every area within three consecutive runs. A full `--all` run is 92 searches in a few minutes, which exceeds the hourly cap: on the free plan the queries past the cap fail and are logged, so cover everything with three dispatches at least an hour apart using the `week` input (0, 1 and 2) instead. On a paid plan `all=true` is fine.

Once the secrets are configured, run the first full coverage as three dispatches an hour apart (free plan), or one `all=true` dispatch on a paid plan:

```bash
gh workflow run crawl.yml -f week=0
gh workflow run crawl.yml -f week=1   # an hour later
gh workflow run crawl.yml -f week=2   # an hour after that
```

To run the same pipeline by hand, export `SERPAPI_API_KEY`, `FMF_DATABASE_URL` and optional `GEMINI_API_KEY` in your shell and run from the repository root:

```bash
python -m backend.data.refresh --all
```

Every run also fetches the Australian scheme pages listed in `backend/data/seed_urls.json` directly, which costs no searches. `--refetch` (the workflow's `refetch` input) skips searching altogether: it re-downloads every page already published plus the seed list, re-normalises and republishes them. Use it after a change to extraction or the relevance filter, since it needs no SerpApi key and spends none of the monthly searches.

Omit `--all` for this week's ten-profile slice, add `--no-llm` to skip Gemini, add `--skip-publish` to keep the result in the local SQLite database instead of Postgres, or use `--dry-run` to print the profiles and search count without credentials or pipeline calls. The crawler writes `backend.crawler.config.DB_PATH` (`funding_crawler.db`) relative to the current directory; `--db-path` changes only the database normalised and published, so keep its default for the normal crawl path.

## Before a demo

Render's free plan sleeps after 15 minutes idle and takes about a minute to wake. Open `/api/health` first, and expect the first search to be slow.

## Releases

Tag a GitHub release at the end of each sprint so the client demo maps to exact code:

```bash
gh release create v0.3.0 --target main --title "Sprint 3" --generate-notes
```

Minor version = sprint number until the final handover, which is `v1.0.0`.

## Rollback

- API: in the Render dashboard, redeploy the previous successful deploy, then revert the bad commit on main through a PR.
- Frontend: revert the bad commit through a PR; `frontend-cd` republishes the previous version once CI passes.
