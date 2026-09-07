# Find Me Funding: backend

Two packages live here. `crawler/` (Jummana) discovers and stores funding pages; its own README explains it. `ranking/`, `data/`, `api/` and `evals/` (Anna) score opportunities against a researcher's inputs and serve the results to the React frontend.

| Component | Status |
| --- | --- |
| Crawler (discovery, fetch, extract, store) | Built, see `crawler/README` |
| Ranking engine (four criterion scores, weighted overall) | Prototype built, scores structured mock data |
| FastAPI search endpoint for the frontend | Prototype built |
| Normalising crawler rows into structured opportunities | Not started |
| LLM or embedding research-match scorer | Not started, seam is in `ranking/research_match.py` |

## Setup

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
```

## Running the API and tests

From the repository root, with the venv active:

```bash
uvicorn backend.api.main:app --reload      # interactive docs at http://localhost:8000/docs
pytest backend                             # unit, API and golden-set tests
python -m backend.evals.run_evals          # ranking eval report and weight sensitivity
```

Try a search:

```bash
curl -s -X POST localhost:8000/api/search -H 'content-type: application/json' \
  -d '{"citizenships":["AU"],"career_stage":"postdoc_2_5","for_codes":["3103"],"research_description":"coral reef resilience"}'
```

## CI/CD

`.github/workflows/backend-ci.yml` runs on every pull request and push to main that touches `backend/`: ruff lint and format check, pytest plus the ranking evals on Python 3.11, 3.12 and 3.13, and a Docker build of `backend/Dockerfile`. Reproduce it locally from the repository root:

```bash
ruff check backend && ruff format --check backend
pytest backend -q && python -m backend.evals.run_evals
docker build -f backend/Dockerfile -t find-me-funding-backend .
docker run --rm -p 8000:8000 find-me-funding-backend
```

`ruff format backend` fixes formatting failures. `crawler/` is excluded from ruff until its rewrite on `feature/backend-crawler` lands; drop the `extend-exclude` line in `pyproject.toml` then.

`.github/workflows/backend-cd.yml` runs after CI passes on main and pushes the image to `ghcr.io/annaseku/unimelb-find-me-funding/backend`, tagged `latest` and `sha-<commit>`. No hosting target is chosen yet; whichever host the team picks pulls that image. Pulling a private package needs a GitHub token with `read:packages`.

## How the ranking works

Each opportunity gets four separate scores, each with a label and plain-English reasons the UI shows:

1. `ranking/eligibility.py`: citizenship, employer type, career stage and funding type checked against the researcher's inputs. Four states: eligible, potentially eligible, unknown, likely ineligible. A contradiction de-ranks the result but does not drop it unless the request sets `hide_ineligible`.
2. `ranking/research_match.py`: ANZSRC FoR and ToA code overlap plus keyword overlap between the free-text description and the opportunity. High, medium or low.
3. `ranking/funding_value.py`: amount banded under $1M, $1M to $2M, $2M to $5M, $5M and over.
4. `ranking/deadline.py`: days to deadline banded over 60, 60 to 30, 30 to 15, under 15. More lead time scores higher.

`ranking/ranker.py` combines them with the weights in `ranking/weights.py` (default eligibility 0.4, match 0.3, funding 0.15, deadline 0.15; any request can override) and filters closed opportunities unless `include_closed` is set. The API pages over the ranked list with `limit` and `offset`.

The ranker currently scores the illustrative opportunities in `data/mock_opportunities.json`. Wiring it to the crawler's SQLite rows needs a normalisation step that turns raw page text into the structured `Opportunity` fields in `ranking/models.py`; `data/repository.py` is the one class to replace. Design record: `docs/adr/ADR-002-ranking-engine.md`. Decisions still needing client confirmation: `docs/ranking-discussion-points.md`.
