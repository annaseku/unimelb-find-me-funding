"""Serves normalised opportunities out of a crawler SQLite database, through
the same repository interface the mock-backed repository already
implements, so switching the API's data source is a one-line environment
change (see `get_repository` in backend/data/repository.py)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from backend.data.repository import OpportunityRepository
from backend.normaliser.pipeline import NORMALISED_TABLE
from backend.ranking.models import Opportunity


class SqliteRepository(OpportunityRepository):
    """Loads every row from `normalised_opportunities` once, at construction
    time. A database that hasn't been normalised yet (the table doesn't
    exist) yields an empty repository rather than raising."""

    def __init__(self, db_path: str | Path) -> None:
        super().__init__(self._load(db_path))

    @staticmethod
    def _load(db_path: str | Path) -> list[Opportunity]:
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.execute(f"SELECT opportunity_json FROM {NORMALISED_TABLE}")
            except sqlite3.OperationalError:
                # Table doesn't exist: nothing has been normalised yet.
                return []
            return [Opportunity(**json.loads(row["opportunity_json"])) for row in cursor.fetchall()]
