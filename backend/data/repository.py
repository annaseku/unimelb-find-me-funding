"""Select the SQLite or Postgres funding store behind the API's repository interface."""

from __future__ import annotations

import os
from functools import lru_cache

from backend.normaliser.models import PipelineRun
from backend.ranking.models import Opportunity, OpportunityStatus

DATA_SOURCES = ("sqlite", "postgres")


class OpportunityRepository:
    def __init__(
        self,
        opportunities: list[Opportunity],
        last_run: PipelineRun | None = None,
        provenance: dict[str, dict[str, str]] | None = None,
    ) -> None:
        self._by_id = {o.id: o for o in opportunities}
        self.last_run = last_run
        funding = [o for o in self._by_id.values() if o.status != OpportunityStatus.NOT_FUNDING]
        self.funding_count = len(funding)
        provenance = provenance or {}
        # Count summaries only among funding records, including closed schemes.
        self.rule_only_summaries = sum(
            provenance.get(o.id, {}).get("summary") != "llm" for o in funding
        )

    def all(self) -> list[Opportunity]:
        return list(self._by_id.values())

    def get(self, opportunity_id: str) -> Opportunity | None:
        return self._by_id.get(opportunity_id)


@lru_cache(maxsize=1)
def get_repository() -> OpportunityRepository:
    """Loaded once per process; the API depends on this.

    Unset or sqlite reads FMF_DB_PATH (default the crawler's DB_PATH);
    postgres reads FMF_DATABASE_URL. Read os.environ inside the function,
    rather than at import time, so tests can switch sources with
    monkeypatch.setenv plus cache_clear().
    """
    source = os.environ.get("FMF_DATA_SOURCE", "sqlite")

    if source == "postgres":
        # Imported lazily so the sqlite path never needs psycopg,
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
    raise RuntimeError(
        f"invalid FMF_DATA_SOURCE {source!r}: valid values are {', '.join(DATA_SOURCES)}"
    )
