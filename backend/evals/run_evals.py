"""Golden-set evaluation of the ranker.

Usage, from the repository root:  python -m backend.evals.run_evals

Compares the ranker's output for each eval profile against hand-written
expectations in golden.json, then shows how the top 5 shifts under a few
alternative weightings so the team can see what the open weighting decision
actually changes. Exit code 1 if any threshold fails.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from backend.evals.corpus import load_corpus, load_profiles
from backend.ranking.ranker import rank
from backend.ranking.weights import DEFAULT_WEIGHTS, Weights

GOLDEN_FILE = Path(__file__).parent / "golden.json"

# Thresholds the test suite enforces.
MIN_LABEL_ACCURACY = 0.9

ALTERNATIVE_WEIGHTS = {
    "default": DEFAULT_WEIGHTS,
    "eligibility-heavy": Weights(
        eligibility=0.7, research_match=0.2, funding_value=0.05, deadline=0.05
    ),
    "match-heavy": Weights(eligibility=0.3, research_match=0.5, funding_value=0.1, deadline=0.1),
    "even": Weights(eligibility=0.25, research_match=0.25, funding_value=0.25, deadline=0.25),
}


@dataclass
class ProfileReport:
    profile_id: str
    labels_checked: int = 0
    labels_correct: int = 0
    top5_checks: int = 0
    top5_passed: int = 0
    top10_checks: int = 0
    top10_passed: int = 0
    failures: list[str] = field(default_factory=list)


@dataclass
class EvalReport:
    per_profile: list[ProfileReport]

    def _rate(self, passed: str, checked: str) -> float:
        total = sum(getattr(p, checked) for p in self.per_profile)
        return sum(getattr(p, passed) for p in self.per_profile) / total if total else 1.0

    @property
    def label_accuracy(self) -> float:
        return self._rate("labels_correct", "labels_checked")

    @property
    def top5_pass_rate(self) -> float:
        return self._rate("top5_passed", "top5_checks")

    @property
    def top10_exclusion_pass_rate(self) -> float:
        return self._rate("top10_passed", "top10_checks")

    @property
    def passed(self) -> bool:
        return (
            self.label_accuracy >= MIN_LABEL_ACCURACY
            and self.top5_pass_rate == 1.0
            and self.top10_exclusion_pass_rate == 1.0
        )


def _load_golden() -> dict:
    return json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))


def evaluate(today: date, weights: Weights = DEFAULT_WEIGHTS) -> EvalReport:
    golden = _load_golden()["profiles"]
    opportunities = load_corpus()
    reports = []
    for profile in load_profiles():
        expected = golden.get(profile.id)
        if expected is None:
            continue
        report = ProfileReport(profile_id=profile.id)
        ranked = rank(opportunities, profile.request, weights, today)
        by_id = {r.opportunity.id: r for r in ranked}
        order = [r.opportunity.id for r in ranked]

        for opp_id, label in expected.get("expected_eligibility", {}).items():
            report.labels_checked += 1
            # Closed records never reach the ranked list, so they read as filtered out.
            actual = by_id[opp_id].eligibility.label if opp_id in by_id else "filtered-out"
            if actual == label:
                report.labels_correct += 1
            else:
                report.failures.append(
                    f"{profile.id}: {opp_id} eligibility {actual!r}, expected {label!r}"
                )

        for opp_id in expected.get("must_be_in_top_5", []):
            report.top5_checks += 1
            if opp_id in order[:5]:
                report.top5_passed += 1
            else:
                position = order.index(opp_id) + 1 if opp_id in order else None
                report.failures.append(
                    f"{profile.id}: {opp_id} expected in top 5, was at {position}"
                )

        for opp_id in expected.get("must_not_be_in_top_10", []):
            report.top10_checks += 1
            if opp_id not in order[:10]:
                report.top10_passed += 1
            else:
                position = order.index(opp_id) + 1
                report.failures.append(
                    f"{profile.id}: {opp_id} expected outside top 10, was at {position}"
                )
        reports.append(report)
    return EvalReport(per_profile=reports)


def _print_report(report: EvalReport) -> None:
    print(f"{'profile':30} {'labels':>8} {'top5':>6} {'top10x':>7}")
    for p in report.per_profile:
        print(
            f"{p.profile_id:30} {p.labels_correct:>3}/{p.labels_checked:<4} "
            f"{p.top5_passed:>2}/{p.top5_checks:<3} {p.top10_passed:>3}/{p.top10_checks:<3}"
        )
    print(
        f"\nlabel accuracy {report.label_accuracy:.2f}   top-5 {report.top5_pass_rate:.2f}   "
        f"top-10 exclusion {report.top10_exclusion_pass_rate:.2f}"
    )
    for p in report.per_profile:
        for failure in p.failures:
            print("  FAIL", failure)


def _print_weight_sensitivity(today: date) -> None:
    print(
        "\nTop 5 under alternative weightings "
        "(open decision, see docs/07-requirements/ranking-discussion-points.md)"
    )
    opportunities = load_corpus()
    for profile in load_profiles():
        print(f"\n{profile.id}")
        for name, weights in ALTERNATIVE_WEIGHTS.items():
            top = [
                r.opportunity.id for r in rank(opportunities, profile.request, weights, today)[:5]
            ]
            print(f"  {name:18} {', '.join(top)}")


def main() -> int:
    today = date.fromisoformat(_load_golden()["today"])
    report = evaluate(today)
    _print_report(report)
    _print_weight_sensitivity(today)
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
