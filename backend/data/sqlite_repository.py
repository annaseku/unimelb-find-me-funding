"""Serve normalised opportunities from a crawler SQLite database read-only."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from backend.data.repository import OpportunityRepository
from backend.normaliser.models import PipelineRun
from backend.normaliser.pipeline import NORMALISED_TABLE, load_latest_run
from backend.ranking.models import Opportunity


class SqliteRepository(OpportunityRepository):
    """Loads every row from `normalised_opportunities` once, at construction
    time. A database that hasn't been normalised yet (the table doesn't
    exist) yields an empty repository rather than raising."""

    def __init__(self, db_path: str | Path) -> None:
        opportunities, last_run, rule_only = self._load(db_path)
        super().__init__(opportunities, last_run, rule_only)

    @staticmethod
    def _load(db_path: str | Path) -> tuple[list[Opportunity], PipelineRun | None, int]:
        path = Path(db_path)
        if not path.is_file():
            raise FileNotFoundError(
                f"no crawler database at {db_path}: run the crawler and normaliser, "
                f"seed one with python -m backend.evals.seed_sqlite {db_path}, "
                "or set FMF_DATA_SOURCE=postgres"
            )
        with sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            last_run = load_latest_run(conn)
            try:
                cursor = conn.execute(
                    f"SELECT opportunity_json, provenance_json FROM {NORMALISED_TABLE}"
                )
            except sqlite3.OperationalError:
                # Table doesn't exist: nothing has been normalised yet.
                return [], last_run, 0
            rows = cursor.fetchall()
            opportunities = [Opportunity(**json.loads(row["opportunity_json"])) for row in rows]
            rule_only = sum(
                json.loads(row["provenance_json"]).get("summary") != "llm" for row in rows
            )
            return opportunities, last_run, rule_only
