# Find Me Funding: frontend

## Funding API integration

The frontend sends searches to `POST /api/search` and renders the four ranked criteria and their reasons. It uses `https://find-me-funding-api.onrender.com` by default.

For a local backend, copy `.env.example` to `.env.local` and set `VITE_API_BASE_URL=http://localhost:8000`. Restart Vite after changing it. Vite embeds this public URL at build time; never place secrets in a `VITE_` variable. The Pages workflow reads the optional repository variable `VITE_API_BASE_URL`, falling back to the deployed API.

Filter labels and API values live together in `src/data/filterOptions.ts`. Empty selections send no restriction. The current list preserves the dropdown branch's selected FoR codes and countries; it is not an exhaustive classification list. Keep new values aligned with `backend/ranking/models.py` and `docs/09-architectural-design/api-contract.md`.

Results use the server's total and load further pages against the last submitted search. Editing controls takes effect on Search. Requests are cancelled when superseded or the page is left, and have a two-minute timeout to accommodate service cold starts. Failures offer a retry without falling back to placeholder data.

Run `npm test`, `npm run lint`, and `npm run build` before submitting changes. Tests stub the HTTP boundary, so they do not depend on the live service or its data.
