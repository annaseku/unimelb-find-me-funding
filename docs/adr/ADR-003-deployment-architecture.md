# ADR-003: Deployment and runtime architecture

| Field | Value |
| --- | --- |
| Decision ID | ADR-003 |
| Decision | Split hosting into three concerns with three different answers, adopted in stages rather than all at once. Application runtime: Render, as a Docker web service built from `backend/Dockerfile`. Data store: Supabase Postgres with pgvector, replacing the local SQLite file. Scheduling: Render's own cron or background worker first, with Inngest held in reserve. Frontend stays on GitHub Pages. Nothing is provisioned this sprint. |
| Status | ⚪ Proposed (no account created, no service deployed, not ratified with the team or the client) |
| Owner | Anna Sekulic |
| Date | 2026-09-07 |

## Context

`backend/Dockerfile` and `backend-cd.yml` publish an image to GHCR on every green merge to `main`, and the workflow comment says outright that no hosting target has been chosen. The image currently has no destination. This ADR chooses one, and records why the obvious alternatives were rejected, so the next person to ask does not have to re-derive it.

Three properties of the backend as it stands drive the whole decision, and each was checked against the code rather than assumed:

`backend/crawler/scheduler.py` is a long-lived polling loop built on `time`, waking hourly per `SCHEDULER_POLL_INTERVAL_SECONDS`. Its own docstring concedes that a real deployment would use cron or Celery beat rather than a long-lived Python process.

`backend/crawler/storage.py` writes SQLite to `funding_crawler.db` on local disk through `sqlite3.connect`. Local disk is state, and state is what makes or breaks every hosting option below.

The crawler and the ranker do not share a store. The crawler writes SQLite; the API reads `backend/data/mock_opportunities.json`. Connecting them is a prerequisite for any deployment being useful, and it is a data decision before it is a hosting one.

Nothing in the 4 September sprint needs a deployed backend. The deliverable is an interactive static UI for search and results, and `frontend/src` currently makes zero `fetch` calls: the mock search flow runs client-side. Deploying today would serve no user.

## Options considered

1. **Render, Docker web service (chosen for the application runtime).** Runs the existing container as a long-lived process, so the scheduler loop and SQLite both work unchanged on day one. The blueprint spec takes `dockerfilePath: ./backend/Dockerfile` with `dockerContext: .`, which preserves the repository-root build context that `backend.*` imports depend on, plus `healthCheckPath: /api/health` matching the Dockerfile's existing health check, and `envVars` with `sync: false` so `GEMINI_API_KEY` is entered in the dashboard instead of living in the repo.
2. **Vercel.** Rejected for the backend, not because of Python: FastAPI is a first-class runtime there, with the `app` object as the entrypoint and `maxDuration` set per file in `vercel.json`. It fails on this codebase's two stateful properties. Functions are request-scoped, so there is no process to host the scheduler loop, and no durable local disk for the SQLite file. It also does not deploy Dockerfiles for web services, so `backend/Dockerfile` and the GHCR pipeline would become dead weight. Worth revisiting once the store moves to Postgres, because its cold starts are roughly a second against Render's minute.
3. **Supabase as the application server.** Rejected. Edge Functions run on Deno, a JavaScript and TypeScript runtime; there is no Python. Hosting the API there means rewriting the ranking engine in TypeScript, which trades a working prototype for a port.
4. **Supabase as the data store (chosen, staged after Render).** Managed Postgres gives the crawler and the ranker one shared store, which is the actual gap. pgvector plus Postgres full-text search covers decision 7's hybrid keyword-and-semantic index in a single database rather than three, which matters because the system matches project prose against funding prose.
5. **Inngest.** Rejected for now, and it is not a host in any case: `inngest.fast_api.serve(app, client, [fn])` mounts into the existing FastAPI app, and Inngest's server sends an HTTP POST to that endpoint to run each function. It orchestrates code hosted elsewhere, so it would sit on top of Render rather than replace it. Its `TriggerCron` trigger, retries, concurrency limits and step-level observability are the right tools for a crawler fetching hundreds of pages, but Render's own cron and background workers cover the current need with one fewer vendor.
6. **Deploy nothing yet (chosen for this sprint).** No user is blocked by the absence of a hosted backend. Standing up three managed services on a project that gets handed over is three accounts, three sets of credentials and three things to explain.

## Decision details

The three concerns and what fills each:

| Concern | Answer | Adopt when |
| --- | --- | --- |
| Where the FastAPI process runs | Render, Docker web service | The frontend needs a live API |
| Where data lives | Supabase Postgres with pgvector | The crawler has to feed the ranker for real |
| What triggers the daily crawl | Render cron or background worker | The crawl has to run unattended |
| Where the frontend is served | GitHub Pages, unchanged | Already in place |

Adoption order is Supabase, then Render, then scheduling. Supabase comes first because it removes the SQLite constraint that rules out half the hosting options, and because it is the only one that closes the crawler-to-ranker gap. Render is cheap to add once there is something worth serving. Scheduling is last and may never need Inngest.

Two prerequisites block any of it from working end to end, and both live in this repository rather than in a vendor:

`backend/api/main.py` hard-codes `allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]`. A frontend served from GitHub Pages has origin `https://annaseku.github.io`, so every browser request fails on CORS until that origin is added. The comment on the line above already anticipates this.

`frontend/src` makes no API calls at all. Wiring the frontend to the API is a separate ticket, and it is the one that makes hosting worth doing.

If Render builds from the repository on push, the GHCR publishing in `backend-cd.yml` is redundant and should be deleted rather than left running. The alternative, pointing Render at the GHCR image through `registryCredential`, keeps CD as the builder but adds a registry credential to manage for no gain at this scale.

## Consequences

Benefits: the existing container runs as-is on Render, with no rewrite of the scheduler or the storage layer to get a first deployment. Postgres with pgvector implements decision 7 in one store instead of three. Each concern can be adopted on its own, so nothing has to be decided before it is needed. Rejecting Vercel and Inngest now does not foreclose either; both become sensible once the store moves off local disk.

Costs: Render's free tier spins a web service down after 15 minutes of idle and takes roughly a minute to wake, which is poor for a cold client demo and argues for warming it before a check-in or paying for demo weeks. Free workspaces get 750 instance hours a month. Moving off SQLite is a migration the crawler has to absorb, not a configuration change. Three vendors, even adopted in stages, is real overhead on a project that gets handed over. And every option here was assessed against a backend that scores mock data, so the shape may change once real crawler rows flow through the ranker.

## Evidence

Code, checked in this repository: `backend/crawler/scheduler.py` (long-lived `time` loop), `backend/crawler/storage.py` (`sqlite3` to a local file), `backend/api/main.py:30` (hard-coded CORS origins), `backend/Dockerfile` (repository-root build context, non-root user, health check on `/api/health`), `.github/workflows/backend-cd.yml` (GHCR publish, "no hosting target is chosen yet"), `frontend/src` (no `fetch` calls).

Vendor documentation, checked 2026-09-07: Render blueprint spec (`runtime: docker`, `dockerfilePath`, `dockerContext`, `healthCheckPath`, `envVars` with `sync: false`) and free instance behaviour (15-minute spin-down, roughly one minute to wake, 750 free instance hours a month). Vercel FastAPI runtime and per-file `maxDuration` in `vercel.json`. Supabase architecture guide, which lists Deno as the Edge Functions runtime, and the pgvector extension guide. Inngest Python SDK: `inngest.fast_api.serve` and the Inngest server's `POST /api/inngest` request lifecycle, plus `TriggerCron`.

Confluence: Project Crawler Architecture, Our Decisions (decision 2, once-per-day batch crawl; decision 7, three stores and hybrid keyword plus semantic search). Sprint Description (31 Aug): the sprint deliverable is an interactive static UI, not a running service.

Related: ADR-002 (ranking engine). ADR-001 is unassigned and reserved for the tech stack decision that `CLAUDE.md` flags as still open.
