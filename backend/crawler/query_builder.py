"""
Builds search queries from the full set of user-supplied search inputs,
so discovery reflects the researcher's actual profile rather than just
a topic keyword.
"""

from backend.crawler.config import FUNDING_TERMS

# Mapping from career stage labels (as used in the frontend inputs) to
# extra query terms that might surface stage-specific funding (e.g. an
# "postdoctoral fellowship" vs an "undergraduate scholarship").
CAREER_STAGE_TERMS = {
    "undergraduate": "undergraduate scholarship",
    "graduate_student": "graduate student funding",
    "postdoc_0_2": "early career postdoctoral fellowship",
    "postdoc_2_5": "postdoctoral research grant",
    "postdoc_5_10": "senior postdoctoral fellowship",
    "postdoc_10_plus": "senior researcher funding",
}

FUNDING_TYPE_TERMS = {
    "salary": "salary funding",
    "consumables": "consumables funding",
    "equipment": "equipment grant",
    "all": "",  # no extra bias -- user wants any/all types
    "any": "",  # no extra bias
}


def generate_seed_queries(
    field_of_research: str,
    type_of_activity: str = "",
    career_stage: str = "",
    funding_type: str = "",
    free_text_description: str = "",
    max_queries: int = 12,
) -> list:
    """
    Build a de-duplicated list of search queries from the full set of user
    inputs.

    Citizenship and employer type are deliberately NOT folded into the
    query text -- they matter for eligibility filtering later, not for
    finding candidate pages, and adding them here would narrow discovery
    without much benefit (few funding pages mention citizenship or
    employer type in their marketing copy).
    """
    base_terms = [field_of_research.strip()]
    if type_of_activity:
        base_terms.append(type_of_activity.strip())
    base = " ".join(t for t in base_terms if t)

    queries = []

    # Every query is scoped to Australia, where the researchers' institution is.
    base = f"{base} Australia".strip()

    # Core: research area x generic funding terms
    for term in FUNDING_TERMS:
        queries.append(f"{base} {term}")

    # Career-stage-specific variant, if we recognise the stage
    stage_term = CAREER_STAGE_TERMS.get(career_stage)
    if stage_term:
        queries.append(f"{base} {stage_term}")

    # Funding-type-specific variant, if meaningful
    type_term = FUNDING_TYPE_TERMS.get(funding_type)
    if type_term:
        queries.append(f"{base} {type_term}")

    # A query built from the free-text research description, since it
    # often contains more specific terms than the FoR/ToA drop-downs.
    if free_text_description:
        # Keep this short -- long queries tend to return worse search
        # results than a handful of well-chosen terms.
        snippet = " ".join(free_text_description.strip().split()[:12])
        queries.append(f"{snippet} research funding Australia")

    # De-duplicate while preserving order, then cap the list length so a
    # single search doesn't trigger an unbounded number of outbound requests.
    seen = set()
    deduped = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            deduped.append(q)

    return deduped[:max_queries]
