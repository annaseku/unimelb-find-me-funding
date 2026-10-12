# ADR-004: Deployment and runtime architecture

| Field | Value |
| --- | --- |
| Decision ID | ADR-004 |
| Decision | Host the FastAPI service on Render as a Docker web service built from `backend/Dockerfile`, keep structured opportunity data in Supabase Postgres, and keep the frontend on GitHub Pages. Scheduling the daily crawl is still open. |
| Status | 🟢 Implemented for runtime and data store (not yet ratified with the client); scheduling open |
| Owner | Anna Sekulic |
| Date | 2026-09-07, updated 2026-10-05 |

## Context

The backend has three concerns that need a home: the API process, the store the API reads, and something that runs the crawl once a day (Confluence decision 2). The crawler writes SQLite to local disk and `backend/crawler/scheduler.py` is a long-lived polling loop, so any host that resets its filesystem or only runs request-scoped functions cannot hold either as they stand. The frontend is a static Vite build and already deploys to GitHub Pages.

This record was first written as ADR-003 on 2026-09-07, when nothing was deployed. `ADR-003-normaliser.md` landed on main the same day, so it is renumbered here and updated to what was built.

## Options considered

1. **Render, Docker web service (chosen for the API).** Runs the existing container unchanged. The blueprint uses `dockerfilePath: ./backend/Dockerfile` with `dockerContext: .`, which keeps the repository-root build context the `backend.*` imports need, and `healthCheckPath: /api/health`.
2. **Vercel.** Rejected for the backend. Functions are request-scoped, so there is no process for the scheduler loop and no durable disk, and it does not deploy a Dockerfile as a web service. Revisit once the API pushes its filtering into SQL.
3. **Supabase as the application server.** Rejected. Edge Functions run on Deno, so the Python ranking engine would have to be rewritten in TypeScript.
4. **Render Postgres as the data store.** Rejected. Free Render Postgres databases expire 30 days after creation and support no backups (Render free-tier docs, checked 2026-10-05), which does not survive a semester.
5. **Supabase Postgres as the data store (chosen).** One managed store the crawler pipeline publishes to and the API reads. pgvector and Postgres full-text search can cover decision 7's keyword plus semantic search in the same database later.
6. **Inngest for scheduling.** Not adopted. It orchestrates code hosted elsewhere rather than hosting it, so it would add a vendor on top of Render rather than replace anything.

## Decision details

| Concern | Answer | State |
| --- | --- | --- |
| Where the API runs | Render web service `find-me-funding-api`, Singapore, free plan, `render.yaml` | Live since 2026-09-07 |
| Where data lives | Supabase Postgres, project in ap-southeast-1, table `normalised_opportunities` | Live since PR #19 (2026-09-15) |
| What runs the daily crawl | Not decided: Render cron job or a scheduled GitHub Actions workflow are the candidates | Open |
| Where the frontend is served | GitHub Pages via `frontend-cd.yml` | Live |

The API connects through Supabase's Supavisor session-mode pooler on port 5432. Supabase's direct endpoint is IPv6-only on the free plan and Render is IPv4-only, and transaction mode (port 6543) does not support the prepared statements psycopg uses. Render has no Australian region, so the API runs in Singapore, and the Supabase project is in Singapore too so the API and database sit in the same region.

Records reach Postgres through `python -m backend.data.publish`, run by hand. Today the deployed table holds the 30 illustrative records from `--source mock`, not crawled data.

## Consequences

Benefits: the existing container runs as-is, every merge to main is a deploy, and the API and the publish step share one store.

Costs: Render's free plan sleeps after 15 minutes idle and takes about a minute to wake, so warm `/api/health` before a demo. Supabase's free plan pauses a project after seven days of low activity; while paused, `/api/search` returns HTTP 500 (seen 2026-10-05) and `/api/health` still returns 200, because health does not touch the database. A scheduled crawl would both keep the data fresh and keep the project awake. With Render building from the repository, the GHCR image that `backend-cd.yml` publishes is not used by any host.

## Evidence

`render.yaml`; `backend/Dockerfile`; `backend/data/postgres_repository.py`; `backend/data/publish.py`; Render service logs on 2026-10-05 (`tenant/user ... not found` from the pooler while the project was paused); Render free-tier documentation (render.com/docs/free); Confluence, Project Crawler Architecture: Our Decisions (decisions 2 and 7).

Related: ADR-002 (ranking engine), ADR-003 (normaliser).
