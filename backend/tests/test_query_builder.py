"""Tests for backend.crawler.queryBuilder: the search queries one research
area turns into, which decide how much of the SerpApi budget finds funding."""

from __future__ import annotations

from backend.crawler.config import EXCLUDED_SITES, FUNDING_TERMS
from backend.crawler.queryBuilder import generate_seed_queries


def test_a_research_area_alone_costs_one_search_per_funding_term():
    queries = generate_seed_queries(field_of_research="Earth Sciences")
    assert len(queries) == len(FUNDING_TERMS)
    assert all(q.startswith("Earth Sciences ") for q in queries)


def test_one_query_asks_for_australian_schemes():
    queries = generate_seed_queries(field_of_research="Earth Sciences")
    assert any("Australia" in q for q in queries)


def test_every_query_excludes_the_sites_that_never_hold_funding():
    queries = generate_seed_queries(
        field_of_research="Earth Sciences",
        career_stage="postdoc_0_2",
        free_text_description="coral reef resilience",
    )
    for query in queries:
        for site in EXCLUDED_SITES:
            assert f"-site:{site}" in query


def test_the_cap_counts_searches_not_exclusions():
    queries = generate_seed_queries(field_of_research="Earth Sciences", max_queries=2)
    assert len(queries) == 2
