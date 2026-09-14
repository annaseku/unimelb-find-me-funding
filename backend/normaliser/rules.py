"""Composes the parsers and lexicon into a full `NormalisedRecord`: one
`Opportunity` per crawled row, plus a provenance entry for every field a
rule or the model might set, and a content hash used to skip unchanged pages
on later pipeline runs."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from backend.normaliser.lexicon import (
    find_career_stages,
    find_citizenships,
    find_employer_types,
    find_for_divisions,
    find_funding_types,
)
from backend.normaliser.models import CrawledRow, NormalisedRecord, Source
from backend.normaliser.parsers import (
    derive_status,
    funder_from_url,
    keywords_from,
    make_id,
    parse_amount_aud,
    parse_deadline,
    summarise,
)
from backend.ranking.models import Opportunity

# Only used by load_fixture_rows below, as a convenient default for tests.
FIXTURE_FILE = Path(__file__).parents[1] / "tests" / "fixtures" / "crawled_rows.json"


def content_hash(row: CrawledRow) -> str:
    """SHA-256 hex digest of the row's title and raw text, so the pipeline
    can tell an unchanged page from a re-crawled one without comparing every
    field."""
    payload = f"{row.title or ''}\n{row.raw_text or ''}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalise_row(row: CrawledRow, today: date) -> NormalisedRecord:
    """Build an Opportunity from one crawled row using only the deterministic
    parsers and lexicon (no LLM). Every field the LLM merge step might later
    touch gets a provenance entry: "rule" when a non-empty value was found,
    "missing" otherwise. `toa_codes`, `countries` and `opens_at` are always
    "missing" here; the rules have no source for them."""
    url = row.url
    funder = funder_from_url(url)
    title = row.title or funder

    summary = summarise(row.raw_text, row.title)
    keywords = keywords_from(row.title)

    amount_aud, amount_note = parse_amount_aud(row.funding_amount_raw)
    deadline = parse_deadline(row.deadline_parsed, row.deadline_raw)
    status = derive_status(deadline, today)

    citizenships_allowed = find_citizenships(row.raw_text)
    employer_types_allowed = find_employer_types(row.eligibility_snippet)
    # Career stage phrases (and the "N years since PhD" numeric ranges) can
    # turn up in the title, the eligibility snippet or the wider body text,
    # so all three are searched together.
    career_stage_text = f"{row.title or ''} {row.eligibility_snippet or ''} {row.raw_text or ''}"
    career_stages_allowed = find_career_stages(career_stage_text)
    funding_types_offered = find_funding_types(row.raw_text)
    # FoR division keywords are searched in the title and the summary (a
    # cleaned-up version of raw_text), not the whole raw text, to keep noise
    # out of the discipline classification.
    for_codes = find_for_divisions(f"{row.title or ''} {summary}")
    eligibility_text = row.eligibility_snippet or ""

    opportunity = Opportunity(
        id=make_id(url),
        title=title,
        funder=funder,
        url=url,
        source_urls=[url],
        summary=summary,
        amount_aud=amount_aud,
        amount_note=amount_note,
        deadline=deadline,
        opens_at=None,
        countries=[],
        citizenships_allowed=citizenships_allowed,
        employer_types_allowed=employer_types_allowed,
        career_stages_allowed=career_stages_allowed,
        funding_types_offered=funding_types_offered,
        for_codes=for_codes,
        toa_codes=[],
        keywords=keywords,
        eligibility_text=eligibility_text,
        status=status,
    )

    amount_provenance: Source = "rule" if amount_aud is not None else "missing"
    provenance: dict[str, Source] = {
        "funder": "rule",
        "summary": "rule" if summary else "missing",
        "amount_aud": amount_provenance,
        "amount_note": amount_provenance,
        "deadline": "rule" if deadline is not None else "missing",
        "citizenships_allowed": "rule" if citizenships_allowed else "missing",
        "employer_types_allowed": "rule" if employer_types_allowed else "missing",
        "career_stages_allowed": "rule" if career_stages_allowed else "missing",
        "funding_types_offered": "rule" if funding_types_offered else "missing",
        "for_codes": "rule" if for_codes else "missing",
        "keywords": "rule" if keywords else "missing",
        "eligibility_text": "rule" if eligibility_text else "missing",
        "toa_codes": "missing",
        "countries": "missing",
        "opens_at": "missing",
    }

    return NormalisedRecord(
        opportunity=opportunity,
        provenance=provenance,
        content_hash=content_hash(row),
        used_llm=False,
    )


def load_fixture_rows(path: Path = FIXTURE_FILE) -> list[CrawledRow]:
    """Load the shared test fixture of crawled rows."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [CrawledRow(**row) for row in data["rows"]]
