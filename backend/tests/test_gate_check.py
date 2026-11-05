"""The funding-gate check fails only when a real scheme is rejected (KAN-84)."""

from pathlib import Path

from backend.evals.gate_check import evaluate, load_cases, read_system_prompt
from backend.normaliser import llm

SCHEME = {"title": "One scheme", "url": "https://a.example", "one_scheme": True}
HUB = {"title": "A hub", "url": "https://b.example", "one_scheme": False}


def test_rejecting_a_real_scheme_fails_the_check():
    report = evaluate([SCHEME, HUB], lambda case: False)
    assert not report.passed
    assert report.schemes_rejected == ["One scheme"]
    assert report.correct == 1


def test_keeping_a_non_scheme_is_reported_but_does_not_fail():
    report = evaluate([SCHEME, HUB], lambda case: True)
    assert report.passed
    assert report.non_schemes_kept == ["A hub"]


def test_an_unknown_answer_counts_as_kept_like_the_merge_does():
    report = evaluate([SCHEME], lambda case: None)
    assert report.passed and report.correct == 1


def test_a_run_where_most_pages_got_no_answer_is_inconclusive_not_passed():
    # Run 41936070420 skipped 25 of 29 pages on model errors and still exited 0.
    cases = [SCHEME] + [{**HUB, "url": f"https://h{i}.example"} for i in range(9)]
    report = evaluate(cases, lambda case: True if case is SCHEME else "model error")
    assert report.checked == 1
    assert not report.conclusive
    assert not report.passed
    assert len(report.skipped) == 9


def test_reads_the_prompt_from_a_copy_of_llm_py_without_importing_it():
    assert read_system_prompt(Path(llm.__file__)) == llm.SYSTEM_PROMPT


def test_cases_are_labelled_and_cover_both_sides():
    cases = load_cases()
    assert {type(c["one_scheme"]) for c in cases} == {bool}
    assert any(c["one_scheme"] for c in cases) and not all(c["one_scheme"] for c in cases)
    assert len({c["url"] for c in cases}) == len(cases)
