"""The crawler's SQLite store upserts by URL and keeps failed fetches out of the results."""

import sqlite3
from contextlib import closing

import pytest

from backend.crawler import storage

FIELDS = {
    "title": "Reef Grant",
    "raw_text": "We fund coral reef research.",
    "deadline_raw": "3 April 2027",
    "deadline_parsed": "2027-04-03",
    "funding_amount_raw": "$50,000",
    "eligibility_snippet": "Open to Australian researchers.",
}
URL = "https://funder.example/grants/reef"


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "crawler.db")
    storage.init_db(path)
    return path


def test_a_saved_page_comes_back_with_its_fields_and_query(db):
    storage.save_opportunity(URL, FIELDS, "reef grant", db_path=db)
    [row] = storage.get_all_opportunities(db)
    assert {k: row[k] for k in FIELDS} == FIELDS
    assert row["source_query"] == "reef grant"


def test_saving_again_updates_the_page_but_keeps_when_it_was_first_seen(db):
    storage.save_opportunity(URL, FIELDS, "reef grant", db_path=db)
    [first] = storage.get_all_opportunities(db)
    storage.save_opportunity(URL, {**FIELDS, "title": "Reef Grant 2027"}, "refresh", db_path=db)
    [second] = storage.get_all_opportunities(db)
    assert second["title"] == "Reef Grant 2027"
    assert second["first_seen_at"] == first["first_seen_at"]


def test_a_failed_fetch_hides_the_page_until_it_is_fetched_again(db):
    storage.save_opportunity(URL, FIELDS, "reef grant", db_path=db)
    storage.mark_fetch_failed(URL, db_path=db)
    assert storage.get_all_opportunities(db) == []
    storage.save_opportunity(URL, FIELDS, "refresh", db_path=db)
    assert len(storage.get_all_opportunities(db)) == 1


def test_only_pages_older_than_the_cutoff_are_stale(db):
    storage.save_opportunity(URL, FIELDS, "reef grant", db_path=db)
    storage.save_opportunity("https://fresh.example", FIELDS, "reef grant", db_path=db)
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute(
            "UPDATE opportunities SET fetched_at = datetime('now', '-8 days') WHERE url = ?",
            (URL,),
        )
    assert storage.get_stale_urls(7, db_path=db) == [URL]
