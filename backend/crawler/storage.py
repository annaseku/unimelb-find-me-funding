"""
SQLite storage for crawled funding opportunities.
"""

import sqlite3
from datetime import datetime, timezone

from backend.crawler.config import DB_PATH


def init_db(db_path: str = DB_PATH) -> None:
    """Create the opportunities table if it doesn't already exist."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opportunities (
                url TEXT PRIMARY KEY,
                title TEXT,
                raw_text TEXT,
                deadline_raw TEXT,
                deadline_parsed TEXT,
                funding_amount_raw TEXT,
                eligibility_snippet TEXT,
                source_query TEXT,
                first_seen_at TEXT,
                fetched_at TEXT,
                fetch_failed INTEGER DEFAULT 0
            )
            """
        )


def save_opportunity(url: str, fields: dict, source_query: str, db_path: str = DB_PATH) -> None:
    """
    Insert or update a crawled opportunity.

    `first_seen_at` is only meaningfully set on first insert (SQLite's
    ON CONFLICT clause below leaves it untouched on updates); every other
    field is refreshed on each re-crawl (upsert semantics keyed on URL).
    """
    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO opportunities (
                url, title, raw_text, deadline_raw, deadline_parsed,
                funding_amount_raw, eligibility_snippet, source_query,
                first_seen_at, fetched_at, fetch_failed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                raw_text = excluded.raw_text,
                deadline_raw = excluded.deadline_raw,
                deadline_parsed = excluded.deadline_parsed,
                funding_amount_raw = excluded.funding_amount_raw,
                eligibility_snippet = excluded.eligibility_snippet,
                source_query = excluded.source_query,
                fetched_at = excluded.fetched_at,
                fetch_failed = 0
            """,
            (
                url, fields.get("title"), fields.get("raw_text"),
                fields.get("deadline_raw"), fields.get("deadline_parsed"),
                fields.get("funding_amount_raw"), fields.get("eligibility_snippet"),
                source_query, now, now,
            ),
        )


def mark_fetch_failed(url: str, db_path: str = DB_PATH) -> None:
    """Flag a URL as having failed to fetch, without deleting its old data."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE opportunities SET fetch_failed = 1, fetched_at = ? WHERE url = ?",
            (datetime.now(timezone.utc).isoformat(), url),
        )


def get_stale_urls(stale_after_days: int, db_path: str = DB_PATH) -> list:
    """Return URLs whose stored data is older than `stale_after_days`."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT url FROM opportunities
            WHERE julianday('now') - julianday(fetched_at) > ?
            """,
            (stale_after_days,),
        )
        return [row[0] for row in cursor.fetchall()]


def get_all_opportunities(db_path: str = DB_PATH) -> list:
    """Return all stored (non-failed) opportunities as a list of dicts."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM opportunities WHERE fetch_failed = 0")
        return [dict(row) for row in cursor.fetchall()]