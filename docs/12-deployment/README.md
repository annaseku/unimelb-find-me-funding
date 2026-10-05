# Deployment

A merge to main is a deploy. There is no manual step.

| Part | Host | Triggered by | Defined in |
| --- | --- | --- | --- |
| Frontend | GitHub Pages: https://annaseku.github.io/unimelb-find-me-funding/ | Frontend CI passing on main | `.github/workflows/frontend-cd.yml` |
| API | Render web service `find-me-funding-api`: https://find-me-funding-api.onrender.com | Any push to main (Render auto-deploy) | `render.yaml`, `backend/Dockerfile` |
| API image | `ghcr.io/annaseku/unimelb-find-me-funding/backend`, tagged `latest` and `sha-<commit>` | Backend CI passing on main | `.github/workflows/backend-cd.yml` |
| Database | Supabase Postgres | `CREATE TABLE IF NOT EXISTS` in `backend/data/postgres_repository.py` | `backend/data/` |

Decision record: `docs/09-architectural-design/adr/ADR-004-deployment-architecture.md`.

## Pipeline

1. Pull request opened: Backend CI (ruff, pytest on 3.11 to 3.13 against Postgres, ranking evals, Docker build) and Frontend CI (ESLint, Vitest, type-check and build) run.
2. The main ruleset blocks merge until all seven jobs pass and one reviewer approves.
3. Merge: Render rebuilds the API, `frontend-cd` publishes the site, `backend-cd` pushes the image.

## Configuration and secrets

- Frontend build: `VITE_API_BASE_URL` (repository variable; defaults to the Render URL).
- API: `FMF_DATA_SOURCE`, `FMF_DATABASE_URL` and `GEMINI_API_KEY` are declared in `render.yaml`; secret values are set in the Render dashboard. Never commit them. See `backend/.env.example` for the full list.

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
