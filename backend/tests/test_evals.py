"""Ranking quality regression: the golden set must keep passing."""

from backend.evals.run_evals import MIN_LABEL_ACCURACY, evaluate
from backend.tests.conftest import TODAY


def test_golden_thresholds_hold():
    report = evaluate(TODAY)
    failures = [f for p in report.per_profile for f in p.failures]
    assert report.per_profile, "golden.json must cover at least one profile"
    assert report.label_accuracy >= MIN_LABEL_ACCURACY, failures
    assert report.top5_pass_rate == 1.0, failures
    assert report.top10_exclusion_pass_rate == 1.0, failures
