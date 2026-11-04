"""Real-model check of the LLM funding gate (KAN-84).

Usage, from the repository root, with OPENROUTER_API_KEY set:

    python -m backend.evals.gate_check [--compare-llm-module PATH]

Fetches every hand-labelled page in gate_cases.json (robots.txt respected),
asks the configured model whether it is about one specific funding
opportunity, and compares the answer with the label. Exit code 1 if any page
labelled as one scheme is rejected: dropping a real scheme is the failure
that matters. Non-schemes let through are reported, not failed. Exit code 2
(inconclusive) when the model answered for fewer than MIN_COVERAGE of the
pages, so a run where most calls fail can never pass.

With --compare-llm-module, the same pages also run through the SYSTEM_PROMPT
read from that file (for example main's llm.py), for a side-by-side.
The crawl workflow runs this with its `gate_check` input; it never publishes.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

CASES_FILE = Path(__file__).parent / "gate_cases.json"
MIN_COVERAGE = 0.8

# A classifier returns the model's answer, or a string naming why the page was skipped.
Classifier = Callable[[dict], "bool | str | None"]


@dataclass
class GateReport:
    total: int = 0
    checked: int = 0
    correct: int = 0
    schemes_rejected: list[str] = field(default_factory=list)
    non_schemes_kept: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def conclusive(self) -> bool:
        return self.total > 0 and self.checked >= MIN_COVERAGE * self.total

    @property
    def passed(self) -> bool:
        return self.conclusive and not self.schemes_rejected


def load_cases(path: Path = CASES_FILE) -> list[dict]:
    return json.loads(path.read_text())


def read_system_prompt(llm_module: Path) -> str:
    """Read SYSTEM_PROMPT from a copy of llm.py without importing it."""
    for node in ast.parse(llm_module.read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "SYSTEM_PROMPT" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f"no SYSTEM_PROMPT in {llm_module}")


def evaluate(cases: list[dict], classify: Classifier) -> GateReport:
    report = GateReport(total=len(cases))
    for case in cases:
        answer = classify(case)
        if isinstance(answer, str):
            report.skipped.append(f"{case['title']} ({answer})")
            continue
        report.checked += 1
        kept = answer is not False
        if kept == case["one_scheme"]:
            report.correct += 1
        elif case["one_scheme"]:
            report.schemes_rejected.append(case["title"])
        else:
            report.non_schemes_kept.append(case["title"])
    return report


def live_classifier(system_prompt: str | None = None) -> Classifier:
    from backend.crawler.crawler import fetch_page
    from backend.crawler.extract import extract_title_and_text
    from backend.crawler.robot_check import is_allowed
    from backend.normaliser.llm import OpenRouterExtractor
    from backend.normaliser.models import CrawledRow
    from backend.normaliser.pipeline import PipelineStats, _extract_with_retries

    extractor = OpenRouterExtractor(system_prompt=system_prompt)
    pages: dict[str, tuple[str, str] | str] = {}

    def classify(case: dict) -> bool | str | None:
        url = case["url"]
        if url not in pages:
            if not is_allowed(url):
                pages[url] = "robots.txt disallows"
            else:
                html = fetch_page(url)
                pages[url] = "fetch failed" if html is None else extract_title_and_text(html)
        page = pages[url]
        if isinstance(page, str):
            return page
        title, text = page
        row = CrawledRow(url=url, title=title, raw_text=text)
        try:
            # The pipeline's own retries, so the check sees what a crawl would.
            fields = _extract_with_retries(extractor, row, PipelineStats(), time.sleep)
        except Exception as exc:  # one bad reply must not end the check
            detail = (str(exc).splitlines()[1:2] or [""])[0].strip()[:160]
            return f"model error: {type(exc).__name__} {detail}"
        return fields.is_funding_opportunity

    return classify


def print_report(name: str, report: GateReport) -> None:
    print(f"\n{name}: {report.correct}/{report.checked} correct, {len(report.skipped)} skipped")
    if not report.conclusive:
        print(f"  INCONCLUSIVE: the model answered for {report.checked} of {report.total} pages")
    for title in report.schemes_rejected:
        print(f"  REJECTED A REAL SCHEME: {title}")
    for title in report.non_schemes_kept:
        print(f"  kept a non-scheme: {title}")
    for title in report.skipped:
        print(f"  skipped: {title}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--compare-llm-module", type=Path)
    args = parser.parse_args(argv)
    cases = load_cases()

    if args.compare_llm_module:
        before = evaluate(cases, live_classifier(read_system_prompt(args.compare_llm_module)))
        print_report(f"Comparison prompt ({args.compare_llm_module})", before)

    current = evaluate(cases, live_classifier())
    print_report("Current prompt", current)
    if not current.conclusive:
        return 2
    return 0 if current.passed else 1


if __name__ == "__main__":
    sys.exit(main())
