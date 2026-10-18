"""Illustrative opportunities and researcher profiles for evals and test fixtures.

Scheme names are real, but amounts, dates and rules were not verified with
funders. The product never loads this corpus as a data source.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel

from backend.normaliser.models import NormalisedRecord
from backend.ranking.models import Opportunity, SearchRequest

CORPUS_FILE = Path(__file__).parent / "corpus.json"
PROFILES_FILE = Path(__file__).parent / "profiles.json"


class EvalProfile(BaseModel):
    id: str
    label: str
    request: SearchRequest


def load_corpus(path: Path = CORPUS_FILE) -> list[Opportunity]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    return [Opportunity(**record) for record in payload["opportunities"]]


def load_profiles(path: Path = PROFILES_FILE) -> list[EvalProfile]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    return [EvalProfile(**record) for record in payload["profiles"]]


def corpus_records(path: Path = CORPUS_FILE) -> list[NormalisedRecord]:
    """Wrap the hand-written corpus without extractor provenance.

    Hash the sorted opportunity JSON so unchanged fixtures keep stable hashes.
    """
    records = []
    for opportunity in load_corpus(path):
        payload = json.dumps(opportunity.model_dump(mode="json"), sort_keys=True)
        records.append(
            NormalisedRecord(
                opportunity=opportunity,
                provenance={},
                content_hash=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                used_llm=False,
            )
        )
    return records
