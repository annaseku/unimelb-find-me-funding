"""Tests for the deterministic parsers: amount, deadline, status, id, funder,
summary and keywords."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pytest

from backend.normaliser.parsers import (
    derive_status,
    funder_from_url,
    keywords_from,
    make_id,
    parse_amount_aud,
    parse_deadline,
    summarise,
)
from backend.ranking.models import OpportunityStatus
from backend.tests.conftest import TODAY

# --- parse_amount_aud ---------------------------------------------------


def test_amount_bare_dollar_500000_assumed_aud():
    amount, note = parse_amount_aud("$500,000")
    assert amount == 500_000
    assert "assumed AUD" in note


def test_amount_aud_2000000_stated_in_aud():
    amount, note = parse_amount_aud("AUD 2,000,000")
    assert amount == 2_000_000
    assert "stated in AUD" in note


def test_amount_a_dollar_1_2_million():
    amount, _note = parse_amount_aud("A$1.2 million")
    assert amount == 1_200_000


def test_amount_eur_1_5_million_converted():
    amount, note = parse_amount_aud("EUR 1.5 million")
    assert amount == 2_475_000
    assert "EUR" in note
    assert "1.65" in note


def test_amount_gbp_3m():
    amount, _note = parse_amount_aud("£3m")
    assert amount == 5_700_000


def test_amount_usd_750k():
    amount, _note = parse_amount_aud("US$750k")
    assert amount == 1_125_000


def test_amount_below_minimum_ignored():
    amount, note = parse_amount_aud("$5 application fee")
    assert amount is None
    assert "below" in note


def test_amount_none_input_gives_no_amount_found():
    amount, note = parse_amount_aud(None)
    assert amount is None
    assert note == "no amount found"


def test_amount_empty_string_gives_no_amount_found():
    amount, note = parse_amount_aud("")
    assert amount is None
    assert note == "no amount found"


def test_amount_takes_first_figure_not_the_duration():
    amount, _note = parse_amount_aud("up to EUR 1.5 million for a period of 5 years")
    assert amount == 2_475_000


# --- parse_deadline -------------------------------------------------------


def test_deadline_iso_parsed_wins_over_raw():
    result = parse_deadline("2027-02-24", "some unrelated text mentioning 1 January 2030")
    assert result.isoformat() == "2027-02-24"


def test_deadline_raw_fuzzy_parse_when_parsed_is_none():
    result = parse_deadline(None, "24 February 2027, 5:00 pm AEDT")
    assert result.isoformat() == "2027-02-24"


def test_deadline_garbage_raw_gives_none():
    assert parse_deadline(None, "garbage") is None


def test_deadline_parsed_year_out_of_range_falls_back_to_raw():
    result = parse_deadline("1899-01-01", "24 February 2027, 5:00 pm AEDT")
    assert result.isoformat() == "2027-02-24"


def test_deadline_parsed_year_out_of_range_and_no_raw_gives_none():
    assert parse_deadline("1899-01-01", None) is None


# --- derive_status ---------------------------------------------------------


def test_status_deadline_yesterday_is_closed():
    assert derive_status(TODAY - timedelta(days=1), TODAY) == OpportunityStatus.CLOSED


def test_status_deadline_tomorrow_is_active():
    assert derive_status(TODAY + timedelta(days=1), TODAY) == OpportunityStatus.ACTIVE


def test_status_no_deadline_is_active():
    assert derive_status(None, TODAY) == OpportunityStatus.ACTIVE


# --- make_id ----------------------------------------------------------------


def test_id_is_deterministic():
    url = "https://erc.europa.eu/apply-grant/starting-grant"
    assert make_id(url) == make_id(url)


def test_id_differs_for_different_urls_on_the_same_host():
    first = make_id("https://www.arc.gov.au/funding/discovery-projects")
    second = make_id("https://www.arc.gov.au/funding/linkage-projects")
    assert first != second


def test_id_strips_leading_www():
    assert make_id("https://www.arc.gov.au/funding/discovery-projects").startswith("arc-gov-au-")


def test_funder_from_url_strips_leading_www():
    assert funder_from_url("https://www.arc.gov.au/funding/discovery-projects") == "arc.gov.au"


# --- summarise ---------------------------------------------------------------


def test_summarise_removes_title_prefix():
    title = "Student Travel Award 2026"
    raw_text = "Student Travel Award 2026. The Foundation offers travel awards."
    assert summarise(raw_text, title).startswith("The Foundation offers travel awards.")


def test_summarise_cuts_at_sentence_boundary_within_max_chars():
    sentence = "This is a sentence about funding opportunities for researchers. "
    raw_text = sentence * 10 + "Trailing words that would overflow the limit without a full stop"
    result = summarise(raw_text, None, max_chars=400)
    assert len(result) <= 400
    assert result.endswith(".")


def test_summarise_none_gives_empty_string():
    assert summarise(None, "Some Title") == ""


# --- keywords_from -------------------------------------------------------


def test_keywords_from_erc_title():
    title = "ERC Starting Grant - Funding Opportunities for Early-Career Researchers"
    keywords = keywords_from(title)
    for expected in ("starting", "opportunities", "early", "career", "researchers"):
        assert expected in keywords
    assert "grant" not in keywords
    assert "funding" not in keywords


def test_keywords_from_respects_limit():
    title = "ERC Starting Grant - Funding Opportunities for Early-Career Researchers"
    assert len(keywords_from(title, limit=2)) == 2


def test_amount_following_word_is_not_read_as_a_multiplier():
    # "may" must not turn $500,000 into 500 billion via the "m" multiplier.
    amount, _ = parse_amount_aud("Budgets of up to $500,000 may be requested")
    assert amount == 500_000


def test_amount_currency_code_needs_word_boundary():
    # "European" contains "Eur" but is not a currency marker.
    amount, note = parse_amount_aud("European 2026 round offers $40,000")
    assert amount == 40_000
    assert "AUD" in note


def test_summarise_skips_leading_menu_text():
    raw_text = (
        "Skip to main content Home About Us Funding News Contact Search "
        "The Foundation funds early-career researchers studying coral reefs. "
        "Applications close in March."
    )
    assert summarise(raw_text, None).startswith("The Foundation funds early-career researchers")


def test_summarise_keeps_text_that_starts_with_prose():
    raw_text = "Our grants support field-initiated research on young people."
    assert summarise(raw_text, None) == raw_text


def test_summarise_skips_government_banner_sentences():
    raw_text = (
        "An official website of the United States government. "
        "Federal government websites often end in .gov or .mil. "
        "This program funds agricultural research at land-grant universities."
    )
    assert summarise(raw_text, None).startswith("This program funds agricultural research")


# --- summarise real page openings (KAN-68) ------------------------------------


@pytest.fixture(scope="module")
def prose_start_pages():
    path = Path(__file__).parent / "fixtures" / "prose_start_pages.json"
    return json.loads(path.read_text(encoding="utf-8"))["pages"]


def test_summarise_keeps_fhri_fund_name(prose_start_pages):
    page = prose_start_pages["fhri_wa"]
    summary = summarise(page["raw_text"], page["title"])
    assert "The FHRI Fund releases funding programs" in summary
    assert not summary.startswith("Fund releases")


def test_summarise_keeps_nesp_program_name(prose_start_pages):
    page = prose_start_pages["nesp_marine"]
    summary = summarise(page["raw_text"], page["title"])
    assert summary.startswith(
        "The National Environmental Science Program (NESP) is a long-term commitment"
    )


def test_summarise_keeps_biological_technologies_and_company_name(prose_start_pages):
    page = prose_start_pages["nsf_seedfund"]
    summary = summarise(page["raw_text"], page["title"])
    assert "Biological Technologies (BT) Miromatrix Medical Inc’s unique technology" in summary
    assert not summary.startswith("Inc’s")


def test_summarise_skips_creative_australia_filter_menu(prose_start_pages):
    page = prose_start_pages["creative_australia"]
    summary = summarise(page["raw_text"], page["title"])
    assert summary.startswith("Fellowships of $80,000 support")


@pytest.mark.parametrize("name", ["aimspress", "aimspress_old"])
def test_summarise_skips_journal_navigation(prose_start_pages, name):
    page = prose_start_pages[name]
    summary = summarise(page["raw_text"], page["title"])
    assert not summary.startswith("Home")
    assert "(MBE) is an interdisciplinary Open Access journal" in summary
    assert summary.startswith(
        (
            "Mathematical Biosciences and Engineering (MBE) is",
            "Contact by email Mathematical Biosciences",
        )
    )


def test_summarise_skips_sicb_breadcrumb(prose_start_pages):
    page = prose_start_pages["sicb"]
    summary = summarise(page["raw_text"], page["title"])
    assert not summary.startswith("Home <")
    assert "SICB offers grants and scholarships" in summary


def test_summarise_skips_laf_scholarship_headings(prose_start_pages):
    page = prose_start_pages["lafoundation"]
    summary = summarise(page["raw_text"], page["title"])
    assert summary.startswith("To date, LAF has awarded")


@pytest.mark.parametrize("name", ["lafoundation_old", "sicb_old"])
def test_summarise_skips_old_extractor_accessibility_links(prose_start_pages, name):
    page = prose_start_pages[name]
    summary = summarise(page["raw_text"], page["title"])
    assert not summary.startswith("Skip to")


def test_summarise_keeps_name_marked_by_a_sentence_opener():
    raw_text = (
        "Home About Donate The Coral Reef Foundation supports early-career researchers "
        "studying marine life."
    )
    assert summarise(raw_text, None).startswith("The Coral Reef Foundation supports")


@pytest.mark.parametrize(
    "boundary", ["/", "<", "|", "Share", "Twitter", "Facebook", "LinkedIn", "Email"]
)
def test_summarise_keeps_name_marked_by_an_acronym_after_a_menu_boundary(boundary):
    raw_text = (
        f"Home {boundary} "
        "Coral Reef Foundation (CRF) supports early-career researchers studying marine life."
    )
    assert summarise(raw_text, None).startswith("Coral Reef Foundation (CRF) supports")


def test_summarise_treats_an_unmarked_capitalised_run_as_a_menu():
    # Without an opener or an acronym, "Home About Donate Coral Reef Foundation" reads
    # the same as a menu; the bulk comparison on 684 crawled rows showed that restoring
    # such runs re-attached menus far more often than it recovered names.
    raw_text = (
        "Home About Donate Coral Reef Foundation supports early-career researchers "
        "studying marine life."
    )
    assert summarise(raw_text, None).startswith("Foundation supports")
