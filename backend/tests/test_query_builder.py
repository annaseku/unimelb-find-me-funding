"""Discovery queries are scoped to Australia, where UoM researchers are based."""

from backend.crawler.query_builder import generate_seed_queries


def test_every_seed_query_mentions_australia():
    queries = generate_seed_queries(
        field_of_research="marine biology",
        career_stage="postdoc_2_5",
        free_text_description="coral reef resilience",
    )
    assert queries
    assert all("Australia" in q for q in queries)
