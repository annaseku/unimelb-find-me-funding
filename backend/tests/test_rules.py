"""Tests for backend.normaliser.rules: composing a full Opportunity (with
provenance) from one crawled row, against the five realistic fixture rows."""

from __future__ import annotations

import copy

from backend.normaliser.rules import content_hash, load_fixture_rows, normalise_row
from backend.ranking.models import (
    CareerStage,
    EmployerType,
    FundingType,
    OpportunityStatus,
)
from backend.tests.conftest import TODAY

ERC_URL = "https://erc.europa.eu/apply-grant/starting-grant"
ARC_URL = (
    "https://www.arc.gov.au/funding-research/funding-schemes/discovery-program/discovery-projects"
)
NHMRC_URL = "https://www.nhmrc.gov.au/funding/find-funding/ideas-grants"
NEWS_URL = "https://www.example-news.org/2026/07/university-announces-new-lab"
TRAVEL_URL = "https://www.example-foundation.org/grants/travel-award-2026"


def _rows_by_url():
    return {row.url: row for row in load_fixture_rows()}


def _records_by_url():
    rows = _rows_by_url()
    return {url: normalise_row(row, TODAY) for url, row in rows.items()}


# --- ERC Starting Grant -------------------------------------------------


def test_erc_amount_converted_from_eur():
    record = _records_by_url()[ERC_URL]
    assert record.opportunity.amount_aud == 2_475_000


def test_erc_deadline_and_status():
    record = _records_by_url()[ERC_URL]
    assert record.opportunity.deadline.isoformat() == "2026-10-14"
    assert record.opportunity.status == OpportunityStatus.ACTIVE


def test_erc_career_stages_reach_all_four_postdoc_bands():
    # The page only says "0-10 years of experience since completion of PhD"
    # (three bands, per lexicon.stages_for_years' strict-overlap semantics)
    # plus "2 and up to 7 years" (already inside those three). The fourth
    # band, POSTDOC_10_PLUS, comes from the separate "research leaders"
    # phrase ("show potential to be research leaders"), which the lexicon's
    # _SENIOR_PATTERN matches on its own, independent of the numeric ranges.
    record = _records_by_url()[ERC_URL]
    assert set(record.opportunity.career_stages_allowed) == {
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
        CareerStage.POSTDOC_5_10,
        CareerStage.POSTDOC_10_PLUS,
    }


def test_erc_employer_types_include_research_institute():
    record = _records_by_url()[ERC_URL]
    assert EmployerType.RESEARCH_INSTITUTE in record.opportunity.employer_types_allowed


def test_erc_citizenships_unrestricted():
    # "Researchers of any nationality" matches no citizenship phrase in the
    # lexicon table, which is correct: an empty list means unrestricted.
    record = _records_by_url()[ERC_URL]
    assert record.opportunity.citizenships_allowed == []


def test_erc_for_codes_empty_or_subset():
    # Observed: []. The ERC page is a generic "how to apply" page with no
    # discipline-specific keywords in its title or summary, so no FoR
    # division fires. That is consistent with "empty or a subset" for a
    # generic page.
    record = _records_by_url()[ERC_URL]
    assert record.opportunity.for_codes == []


def test_erc_provenance_deadline_and_amount_are_rule_countries_missing():
    record = _records_by_url()[ERC_URL]
    assert record.provenance["deadline"] == "rule"
    assert record.provenance["amount_aud"] == "rule"
    assert record.provenance["countries"] == "missing"


# --- ARC Discovery Projects ----------------------------------------------


def test_arc_amount_bare_dollar_assumed_aud():
    record = _records_by_url()[ARC_URL]
    assert record.opportunity.amount_aud == 500_000


def test_arc_deadline():
    record = _records_by_url()[ARC_URL]
    assert record.opportunity.deadline.isoformat() == "2027-03-10"


def test_arc_employer_types_university_only():
    record = _records_by_url()[ARC_URL]
    assert record.opportunity.employer_types_allowed == [EmployerType.UNIVERSITY]


def test_arc_citizenships_unrestricted():
    # "There are no citizenship or residency requirements" matches no
    # phrase in the lexicon table (deliberately: see lexicon.py), so [].
    record = _records_by_url()[ARC_URL]
    assert record.opportunity.citizenships_allowed == []


def test_arc_funding_types_observed_empty():
    # Ran normalise_row and looked at the result: the ARC raw text never
    # mentions "consumables", "salary", "stipend" or any other funding-type
    # phrase from the lexicon (it only talks about total dollar amounts per
    # project), so find_funding_types correctly returns []. Pinning the
    # observed value per the plan's instruction not to force CONSUMABLES or
    # SALARY onto text that doesn't support them.
    record = _records_by_url()[ARC_URL]
    assert record.opportunity.funding_types_offered == []


# --- NHMRC Ideas Grants ---------------------------------------------------


def test_nhmrc_amount():
    record = _records_by_url()[NHMRC_URL]
    assert record.opportunity.amount_aud == 1_200_000


def test_nhmrc_deadline():
    record = _records_by_url()[NHMRC_URL]
    assert record.opportunity.deadline.isoformat() == "2027-02-24"


def test_nhmrc_employer_types_contain_university_and_research_institute():
    record = _records_by_url()[NHMRC_URL]
    types = record.opportunity.employer_types_allowed
    assert EmployerType.UNIVERSITY in types
    assert EmployerType.RESEARCH_INSTITUTE in types


def test_nhmrc_citizenships_au():
    record = _records_by_url()[NHMRC_URL]
    assert record.opportunity.citizenships_allowed == ["AU"]


def test_nhmrc_career_stages_early_mid_and_within_10_years():
    # "Early career researchers and mid-career researchers" gives the first
    # two postdoc bands directly; "within 10 years of their PhD" gives
    # POSTDOC_0_2, POSTDOC_2_5 and POSTDOC_5_10 under stages_for_years'
    # strict-overlap semantics (band 10-plus does not overlap [0, 10)).
    # POSTDOC_10_PLUS is not expected here: nothing in this fixture uses a
    # "senior"/"established"/"professor"/"research leader" phrase.
    record = _records_by_url()[NHMRC_URL]
    stages = record.opportunity.career_stages_allowed
    assert CareerStage.POSTDOC_0_2 in stages
    assert CareerStage.POSTDOC_2_5 in stages
    assert CareerStage.POSTDOC_5_10 in stages


def test_nhmrc_funding_types_consumables_and_equipment_not_salary():
    record = _records_by_url()[NHMRC_URL]
    types = record.opportunity.funding_types_offered
    assert FundingType.CONSUMABLES in types
    assert FundingType.EQUIPMENT in types
    assert FundingType.SALARY not in types


def test_nhmrc_for_codes_include_health_or_biomedical():
    record = _records_by_url()[NHMRC_URL]
    for_codes = set(record.opportunity.for_codes)
    assert "42" in for_codes or "32" in for_codes


# --- News page (false-positive amount) ------------------------------------


def test_news_amount_is_a_false_positive_the_rules_cannot_detect():
    # "$5 million" for building a laboratory parses the same way a genuine
    # funding figure would: no rule can tell "we spent" from "we will
    # award" apart, so this is exactly the kind of case provenance and the
    # LLM merge step exist to catch later, not something Task 4 can fix.
    record = _records_by_url()[NEWS_URL]
    assert record.opportunity.amount_aud == 5_000_000


def test_news_eligibility_text_empty():
    record = _records_by_url()[NEWS_URL]
    assert record.opportunity.eligibility_text == ""


def test_news_employer_types_empty():
    record = _records_by_url()[NEWS_URL]
    assert record.opportunity.employer_types_allowed == []


def test_news_status_active_with_no_deadline():
    record = _records_by_url()[NEWS_URL]
    assert record.opportunity.deadline is None
    assert record.opportunity.status == OpportunityStatus.ACTIVE


def test_news_for_codes_include_biological():
    record = _records_by_url()[NEWS_URL]
    assert "31" in record.opportunity.for_codes


# --- Travel award ----------------------------------------------------------


def test_travel_amount():
    record = _records_by_url()[TRAVEL_URL]
    assert record.opportunity.amount_aud == 3_000


def test_travel_deadline_and_status_closed():
    record = _records_by_url()[TRAVEL_URL]
    assert record.opportunity.deadline.isoformat() == "2026-08-15"
    assert record.opportunity.status == OpportunityStatus.CLOSED


def test_travel_citizenships_australian_or_new_zealand():
    # "must be Australian or New Zealand citizens" is a coordinated phrase;
    # the lexicon handles it explicitly so both codes come through.
    record = _records_by_url()[TRAVEL_URL]
    assert record.opportunity.citizenships_allowed == ["AU", "NZ"]


def test_travel_career_stages_undergraduate_and_graduate():
    record = _records_by_url()[TRAVEL_URL]
    stages = record.opportunity.career_stages_allowed
    assert CareerStage.UNDERGRADUATE in stages
    assert CareerStage.GRADUATE_STUDENT in stages


def test_travel_employer_types_university_only():
    record = _records_by_url()[TRAVEL_URL]
    assert record.opportunity.employer_types_allowed == [EmployerType.UNIVERSITY]


# --- content_hash and cross-fixture invariants -----------------------------


def test_content_hash_changes_when_raw_text_changes():
    row = _rows_by_url()[ERC_URL]
    original_hash = content_hash(row)
    changed = copy.deepcopy(row)
    changed.raw_text = (changed.raw_text or "") + " Extra sentence added for the test."
    assert content_hash(changed) != original_hash


def test_content_hash_stable_for_unchanged_row():
    row = _rows_by_url()[ERC_URL]
    assert content_hash(row) == content_hash(row.model_copy())


def test_ids_unique_across_fixtures():
    records = _records_by_url()
    ids = [record.opportunity.id for record in records.values()]
    assert len(ids) == len(set(ids))


def test_every_fixture_row_normalises_to_a_valid_opportunity():
    # Constructing each Opportunity inside normalise_row is itself the
    # assertion: Pydantic validation would raise if any field were the
    # wrong shape, so simply building the records for all five rows and
    # reaching this point proves they all validate.
    records = _records_by_url()
    assert len(records) == 5
