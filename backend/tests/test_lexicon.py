"""Phrase-to-code lexicon tables: citizenship, employer type, career stage,
funding type and ANZSRC FoR division, plus the funding-type negation rule."""

from __future__ import annotations

from backend.normaliser.lexicon import (
    find_career_stages,
    find_citizenships,
    find_employer_types,
    find_for_divisions,
    find_funding_types,
    stages_for_years,
)
from backend.ranking.models import CareerStage, EmployerType, FundingType

NHMRC_NEGATION_SENTENCE = (
    "Salary support for the Chief Investigator is not available under this scheme; "
    "funding covers direct research costs including consumables and equipment."
)


# --- citizenship -------------------------------------------------------------


def test_australian_citizens_gives_au():
    assert find_citizenships("Applicants must be Australian citizens.") == ["AU"]


def test_australian_permanent_residents_gives_au():
    assert find_citizenships("Open to Australian permanent residents.") == ["AU"]


def test_new_zealand_citizens_gives_nz():
    assert find_citizenships("Open to New Zealand citizens only.") == ["NZ"]


def test_us_citizens_variants_give_us():
    assert find_citizenships("Must be a US citizen.") == ["US"]
    assert find_citizenships("Must be a U.S. citizen.") == ["US"]
    assert find_citizenships("Must be a United States citizen.") == ["US"]


def test_uk_variants_give_gb():
    assert find_citizenships("Open to UK nationals.") == ["GB"]
    assert find_citizenships("Open to British citizens.") == ["GB"]


def test_canadian_citizens_gives_ca():
    assert find_citizenships("Open to Canadian citizens.") == ["CA"]


def test_multiple_citizenships_are_sorted_and_unique():
    text = "Open to Australian citizens and New Zealand citizens."
    assert find_citizenships(text) == ["AU", "NZ"]


def test_no_citizenship_requirement_phrases_return_empty():
    assert find_citizenships("Open to any nationality.") == []
    assert find_citizenships("There are no citizenship or residency requirements.") == []


def test_citizenship_negative_case_with_unrelated_text():
    assert find_citizenships("This scheme funds equipment purchases only.") == []


def test_citizenship_empty_and_none_input():
    assert find_citizenships(None) == []
    assert find_citizenships("") == []


# --- employer type -----------------------------------------------------------


def test_university_phrase_gives_university():
    assert find_employer_types("Open to university staff.") == [EmployerType.UNIVERSITY]


def test_research_institute_phrases_give_research_institute():
    assert find_employer_types("Employed by a research institute.") == [
        EmployerType.RESEARCH_INSTITUTE
    ]
    assert find_employer_types("A medical research institute is eligible.") == [
        EmployerType.RESEARCH_INSTITUTE
    ]


def test_industry_phrases_give_industry():
    assert find_employer_types("Open to industry and small businesses.") == [EmployerType.INDUSTRY]


def test_philanthropic_phrases_give_philanthropic():
    assert find_employer_types("A registered charity or NGO may apply.") == [
        EmployerType.PHILANTHROPIC
    ]


def test_employer_types_sorted_by_enum_order():
    text = "Open to industry, universities and charities."
    assert find_employer_types(text) == [
        EmployerType.UNIVERSITY,
        EmployerType.INDUSTRY,
        EmployerType.PHILANTHROPIC,
    ]


def test_employer_type_negative_case():
    assert find_employer_types("Applications close on 1 January.") == []


def test_employer_type_empty_and_none_input():
    assert find_employer_types(None) == []
    assert find_employer_types("") == []


# --- career stage -------------------------------------------------------------


def test_undergraduate_phrase():
    assert find_career_stages("Open to undergraduates.") == [CareerStage.UNDERGRADUATE]


def test_graduate_student_phrases():
    assert find_career_stages("Open to PhD candidates.") == [CareerStage.GRADUATE_STUDENT]
    assert find_career_stages("Open to postgraduates.") == [CareerStage.GRADUATE_STUDENT]


def test_early_career_gives_first_two_postdoc_bands():
    assert find_career_stages("For early career researchers.") == [
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
    ]


def test_early_career_hyphen_and_space_are_equivalent():
    hyphenated = find_career_stages("For early-career researchers.")
    spaced = find_career_stages("For early career researchers.")
    assert hyphenated == spaced == [CareerStage.POSTDOC_0_2, CareerStage.POSTDOC_2_5]


def test_mid_career_gives_postdoc_5_10():
    assert find_career_stages("For mid-career researchers.") == [CareerStage.POSTDOC_5_10]


def test_senior_researcher_phrases_give_postdoc_10_plus():
    assert find_career_stages("For senior researchers and professors.") == [
        CareerStage.POSTDOC_10_PLUS
    ]


def test_postdoctoral_gives_all_four_postdoc_bands():
    assert find_career_stages("Open to postdoctoral fellows.") == [
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
        CareerStage.POSTDOC_5_10,
        CareerStage.POSTDOC_10_PLUS,
    ]


def test_numeric_range_and_up_to_gives_postdoc_2_5_and_5_10():
    text = "Applicants must be 2 and up to 7 years post PhD."
    assert find_career_stages(text) == [CareerStage.POSTDOC_2_5, CareerStage.POSTDOC_5_10]


def test_numeric_range_dash_with_full_context_gives_all_four_postdoc_bands():
    # Drawn from the ERC fixture text: word-based matches ("early-career",
    # "research leaders") combine with the numeric range ("0-10 years ...
    # since completion of PhD") to cover all four postdoc bands.
    text = (
        "Starting Grants support talented early-career scientists who show "
        "potential to be research leaders. Researchers of any nationality "
        "with 0-10 years of experience since completion of PhD may apply."
    )
    assert find_career_stages(text) == [
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
        CareerStage.POSTDOC_5_10,
        CareerStage.POSTDOC_10_PLUS,
    ]


def test_within_ten_years_of_phd_gives_first_three_postdoc_bands():
    text = "The Chief Investigator must be within 10 years of their PhD."
    assert find_career_stages(text) == [
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
        CareerStage.POSTDOC_5_10,
    ]


def test_numeric_range_without_phd_context_is_ignored():
    assert find_career_stages("Projects run for 2-7 years.") == []


def test_career_stage_empty_and_none_input():
    assert find_career_stages(None) == []
    assert find_career_stages("") == []


# --- stages_for_years ---------------------------------------------------------


def test_stages_for_years_zero_to_two():
    assert stages_for_years(0, 2) == [CareerStage.POSTDOC_0_2]


def test_stages_for_years_two_to_seven():
    assert stages_for_years(2, 7) == [CareerStage.POSTDOC_2_5, CareerStage.POSTDOC_5_10]


def test_stages_for_years_zero_to_ten_excludes_ten_plus():
    # A closed range that just touches the open top band's edge does not
    # count as overlapping it; only a range starting at 10 or more does.
    assert stages_for_years(0, 10) == [
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
        CareerStage.POSTDOC_5_10,
    ]


def test_stages_for_years_ten_and_open_ended():
    assert stages_for_years(10, None) == [CareerStage.POSTDOC_10_PLUS]


def test_stages_for_years_zero_and_open_ended_gives_all_bands():
    assert stages_for_years(0, None) == [
        CareerStage.POSTDOC_0_2,
        CareerStage.POSTDOC_2_5,
        CareerStage.POSTDOC_5_10,
        CareerStage.POSTDOC_10_PLUS,
    ]


# --- funding type --------------------------------------------------------------


def test_salary_phrases_give_salary():
    assert find_funding_types("Includes a stipend of $30,000.") == [FundingType.SALARY]


def test_consumables_phrases_give_consumables():
    assert find_funding_types("Covers direct research costs.") == [FundingType.CONSUMABLES]


def test_equipment_phrases_give_equipment():
    assert find_funding_types("Covers equipment and infrastructure.") == [FundingType.EQUIPMENT]


def test_funding_types_sorted_by_enum_order():
    text = "Covers salary, consumables and equipment."
    assert find_funding_types(text) == [
        FundingType.SALARY,
        FundingType.CONSUMABLES,
        FundingType.EQUIPMENT,
    ]


def test_funding_type_negative_case():
    assert find_funding_types("Applications close on 1 January.") == []


def test_nhmrc_negation_sentence_excludes_salary_but_keeps_consumables_and_equipment():
    result = find_funding_types(NHMRC_NEGATION_SENTENCE)
    assert FundingType.SALARY not in result
    assert FundingType.CONSUMABLES in result
    assert FundingType.EQUIPMENT in result


def test_excluding_travel_is_negated():
    assert find_funding_types("This grant covers all costs excluding travel.") == []


def test_funding_type_empty_and_none_input():
    assert find_funding_types(None) == []
    assert find_funding_types("") == []


# --- ANZSRC FoR division -------------------------------------------------------


def test_for_division_positive_case_biological():
    assert find_for_divisions("A study of marine ecology and genetics.") == ["31"]


def test_for_division_negative_case():
    assert find_for_divisions("Applications close on 1 January.") == []


def test_coral_reef_and_ocean_acidification_gives_biological_and_earth():
    assert find_for_divisions("coral reef ecosystems and ocean acidification") == ["31", "37"]


def test_for_division_multiple_codes_sorted():
    text = "Research in machine learning applied to public health and epidemiology."
    assert find_for_divisions(text) == ["42", "46"]


def test_for_division_empty_and_none_input():
    assert find_for_divisions(None) == []
    assert find_for_divisions("") == []
