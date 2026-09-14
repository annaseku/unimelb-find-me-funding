"""Loads the mock opportunity set and exposes it behind a small repository.

This is the seam decision 7 describes between the structured funding store
and the search layer: the API only ever calls `all()` and `get()`, so a
crawler-backed repository replaces this one class and nothing else changes.

The mock values are illustrative. Scheme names are real so the demo reads
naturally, but amounts, dates and rules were not verified with the funders.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from backend.ranking.models import Opportunity, SearchRequest

_DATA_DIR = Path(__file__).parent
OPPORTUNITIES_FILE = _DATA_DIR / "mock_opportunities.json"
PROFILES_FILE = _DATA_DIR / "mock_profiles.json"


class MockProfile(BaseModel):
    id: str
    label: str
    request: SearchRequest


class OpportunityRepository:
    def __init__(self, opportunities: list[Opportunity]) -> None:
        self._by_id = {o.id: o for o in opportunities}

    def all(self) -> list[Opportunity]:
        return list(self._by_id.values())

    def get(self, opportunity_id: str) -> Opportunity | None:
        return self._by_id.get(opportunity_id)


def load_mock_opportunities(path: Path = OPPORTUNITIES_FILE) -> list[Opportunity]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    # The file carries a top-level note explaining it is illustrative.
    return [Opportunity(**record) for record in payload["opportunities"]]


def load_mock_profiles(path: Path = PROFILES_FILE) -> list[MockProfile]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    return [MockProfile(**record) for record in payload["profiles"]]


@lru_cache(maxsize=1)
def get_repository() -> OpportunityRepository:
    """Loaded once per process; the API depends on this.

    FMF_DATA_SOURCE=postgres reads FMF_DATABASE_URL (this is what the Render
    deployment uses); FMF_DATA_SOURCE=sqlite reads FMF_DB_PATH (default the
    crawler's DB_PATH); anything else (including unset) keeps the
    illustrative mock set. Reading os.environ inside the function, rather
    than at import time, is what lets tests switch data sources with
    monkeypatch.setenv plus cache_clear().
    """
    source = os.environ.get("FMF_DATA_SOURCE")

    if source == "postgres":
        # Imported lazily so the mock and sqlite paths never need psycopg,
        # and so an unset FMF_DATABASE_URL fails here rather than at import.
        from backend.data.postgres_repository import PostgresRepository

        database_url = os.environ.get("FMF_DATABASE_URL")
        if not database_url:
            raise RuntimeError("FMF_DATA_SOURCE=postgres requires FMF_DATABASE_URL")
        return PostgresRepository(database_url)

    if source == "sqlite":
        # Imported lazily: sqlite_repository imports OpportunityRepository
        # from this module, so importing it at module level would cycle.
        from backend.crawler.config import DB_PATH
        from backend.data.sqlite_repository import SqliteRepository

        db_path = os.environ.get("FMF_DB_PATH", DB_PATH)
        return SqliteRepository(db_path)
    return OpportunityRepository(load_mock_opportunities())
