"""FastAPI search service for the React frontend.

Run from the repository root:  uvicorn backend.api.main:app --reload
Interactive docs at http://localhost:8000/docs are the authoritative API
agreement (Jira KAN-11); docs/09-architectural-design/api-contract.md is the human summary.

Decision 6: a search ranks what is already indexed and "more results" pages
over the same ranked set. Nothing here triggers a crawl.
"""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import ranking
from backend.api.schemas import DataStatus, HealthResponse, SearchResponse
from backend.data.repository import get_repository
from backend.ranking.models import Opportunity, SearchRequest
from backend.ranking.ranker import rank
from backend.ranking.weights import resolve_weights

app = FastAPI(title="Find Me Funding API", version=ranking.__version__)

# The Vite dev server plus the GitHub Pages frontend (see frontend-cd.yml).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://annaseku.github.io",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=ranking.__version__)


@app.get("/api/status", response_model=DataStatus)
def status() -> DataStatus:
    """How the data behind the results was produced, so the frontend can warn
    when the LLM hit a plan limit and summaries are rule-built."""
    repository = get_repository()
    return DataStatus(
        last_run=repository.last_run,
        opportunities=len(repository.all()),
        rule_only_summaries=repository.rule_only_summaries,
    )


@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    weights = resolve_weights(request.weights)
    ranked = rank(get_repository().all(), request, weights, date.today())
    page = ranked[request.offset : request.offset + request.limit]
    return SearchResponse(
        results=page,
        total=len(ranked),
        limit=request.limit,
        offset=request.offset,
        weights=weights.as_dict(),
    )


@app.get("/api/opportunities/{opportunity_id}", response_model=Opportunity)
def get_opportunity(opportunity_id: str) -> Opportunity:
    # Closed records are returned too: they are soft-deleted, not gone (decision 9).
    opportunity = get_repository().get(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return opportunity
