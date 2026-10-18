"""The API is the seam with the React frontend (Jira KAN-11). These tests pin
the contract rules in docs/09-architectural-design/api-contract.md."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.data.repository import get_repository
from backend.ranking.models import SearchRequest
from backend.ranking.ranker import rank
from backend.ranking.weights import DEFAULT_WEIGHTS


@pytest.fixture(autouse=True)
def use_corpus_data_source(corpus_data_source):
    """Seed the API tests independently of a developer's local database."""


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def open_count() -> int:
    # The API uses the real clock, so the expected total is computed the same way.
    return len(rank(get_repository().all(), SearchRequest(), DEFAULT_WEIGHTS, date.today()))


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["version"]


@pytest.mark.parametrize(
    "origin",
    ["http://localhost:5173", "http://127.0.0.1:5173", "https://annaseku.github.io"],
)
def test_cors_allows_the_vite_dev_server_and_the_pages_frontend(client, origin):
    # A browser preflight for the search endpoint from an allowed origin.
    response = client.options(
        "/api/search",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "POST" in response.headers["access-control-allow-methods"]


def test_cors_rejects_an_unknown_origin(client):
    response = client.options(
        "/api/search",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in response.headers


def test_empty_search_returns_first_ten_and_total_of_open_set(client):
    body = client.post("/api/search", json={}).json()
    assert len(body["results"]) == 10
    assert body["total"] == open_count()
    assert body["limit"] == 10
    assert body["offset"] == 0


def test_every_result_has_four_scores_labels_and_reasons(client):
    result = client.post("/api/search", json={}).json()["results"][0]
    for key in ("eligibility", "research_match", "funding_value", "deadline"):
        assert set(result[key]) == {"score", "label", "reasons"}
        assert result[key]["reasons"]
    assert "overall" in result
    assert result["opportunity"]["url"].startswith("http")


def test_offset_paging_continues_the_same_ordering(client):
    first = client.post("/api/search", json={"limit": 5}).json()["results"]
    second = client.post("/api/search", json={"limit": 5, "offset": 5}).json()["results"]
    everything = client.post("/api/search", json={"limit": 100}).json()["results"]
    assert [r["opportunity"]["id"] for r in first + second] == [
        r["opportunity"]["id"] for r in everything[:10]
    ]


def test_weights_are_echoed_and_overridable(client):
    default = client.post("/api/search", json={}).json()["weights"]
    assert default == DEFAULT_WEIGHTS.as_dict()
    custom = client.post("/api/search", json={"weights": {"deadline": 0.9}}).json()["weights"]
    assert custom["deadline"] == 0.9
    assert custom["eligibility"] == DEFAULT_WEIGHTS.eligibility


def test_hide_ineligible_removes_likely_ineligible_end_to_end(client):
    request = {"citizenships": ["US"], "employer_type": "industry", "limit": 100}
    shown = client.post("/api/search", json=request).json()["results"]
    hidden = client.post("/api/search", json={**request, "hide_ineligible": True}).json()["results"]
    assert any(r["eligibility"]["label"] == "likely_ineligible" for r in shown)
    assert not any(r["eligibility"]["label"] == "likely_ineligible" for r in hidden)
    assert len(hidden) < len(shown)


def test_include_closed_adds_the_soft_deleted_records(client):
    open_total = client.post("/api/search", json={}).json()["total"]
    all_total = client.post("/api/search", json={"include_closed": True}).json()["total"]
    assert all_total == len(get_repository().all())
    assert all_total > open_total


@pytest.mark.parametrize("payload", [{"limit": 0}, {"limit": 101}, {"career_stage": "professor"}])
def test_invalid_input_is_422(client, payload):
    assert client.post("/api/search", json=payload).status_code == 422


def test_get_opportunity_by_id_including_closed(client):
    closed = next(o for o in get_repository().all() if o.status == "closed")
    body = client.get(f"/api/opportunities/{closed.id}").json()
    assert body["id"] == closed.id


def test_unknown_opportunity_is_404(client):
    assert client.get("/api/opportunities/nope").status_code == 404


def _crawled_row_fields(row) -> dict:
    return {
        "title": row.title,
        "raw_text": row.raw_text,
        "deadline_raw": row.deadline_raw,
        "deadline_parsed": row.deadline_parsed,
        "funding_amount_raw": row.funding_amount_raw,
        "eligibility_snippet": row.eligibility_snippet,
    }


@pytest.fixture
def sqlite_data_source(tmp_path, monkeypatch):
    """Points get_repository at a normalised temp database for the duration
    of one test, then clears the cache again so the corpus-backed tests above
    keep passing regardless of test order."""
    from backend.crawler.storage import init_db, save_opportunity
    from backend.normaliser.pipeline import normalise_database
    from backend.normaliser.rules import load_fixture_rows
    from backend.tests.conftest import TODAY

    db = tmp_path / "crawler.db"
    init_db(str(db))
    for row in load_fixture_rows():
        save_opportunity(row.url, _crawled_row_fields(row), row.source_query or "", db_path=str(db))
    normalise_database(db, TODAY)

    monkeypatch.setenv("FMF_DATA_SOURCE", "sqlite")
    monkeypatch.setenv("FMF_DB_PATH", str(db))
    get_repository.cache_clear()
    yield db
    get_repository.cache_clear()


def test_search_reads_from_the_sqlite_repository_when_selected(client, sqlite_data_source):
    body = client.post("/api/search", json={"include_closed": True, "limit": 100}).json()
    assert body["total"] == 5


def test_status_reports_the_last_run_and_rule_only_summaries(
    client, normalised_sqlite_db, monkeypatch
):
    # normalised_sqlite_db ran without an extractor, so every summary is rule-built.
    monkeypatch.setenv("FMF_DB_PATH", str(normalised_sqlite_db))
    get_repository.cache_clear()
    body = client.get("/api/status").json()
    assert body["last_run"]["llm_stop_reason"] == "not_configured"
    assert body["opportunities"] > 0
    assert body["rule_only_summaries"] == body["opportunities"]
