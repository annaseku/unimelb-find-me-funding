"""The evals corpus covers the ranker's input bands and researcher profiles."""

from backend.evals.corpus import load_corpus, load_profiles
from backend.ranking.deadline import score_deadline
from backend.ranking.funding_value import score_funding_value
from backend.ranking.models import (
    CareerStage,
    DeadlineBand,
    EmployerType,
    FundingBand,
    Opportunity,
    OpportunityStatus,
)
from backend.tests.conftest import TODAY


def test_every_corpus_record_validates_and_ids_are_unique():
    opportunities = load_corpus()
    assert len(opportunities) >= 30
    assert all(isinstance(o, Opportunity) for o in opportunities)
    assert len({o.id for o in opportunities}) == len(opportunities)


def test_corpus_data_covers_every_funding_band():
    bands = {score_funding_value(o).label for o in load_corpus()}
    assert bands == set(FundingBand)


def test_corpus_data_covers_every_deadline_band_relative_to_today():
    bands = {score_deadline(o, TODAY).label for o in load_corpus()}
    assert bands == set(DeadlineBand)


def test_corpus_data_has_closed_status_past_deadline_and_future_opening():
    opportunities = load_corpus()
    assert sum(o.status == OpportunityStatus.CLOSED for o in opportunities) >= 2
    assert any(
        o.status == OpportunityStatus.ACTIVE and o.deadline and o.deadline < TODAY
        for o in opportunities
    )
    assert sum(1 for o in opportunities if o.opens_at and o.opens_at > TODAY) >= 2
    assert sum(1 for o in opportunities if o.amount_aud is None) >= 3
    assert sum(1 for o in opportunities if o.deadline is None) >= 2


def test_corpus_data_covers_every_career_stage_and_employer_type():
    opportunities = load_corpus()
    stages = {s for o in opportunities for s in o.career_stages_allowed}
    employers = {e for o in opportunities for e in o.employer_types_allowed}
    assert stages == set(CareerStage)
    assert employers == set(EmployerType)


def test_profiles_load_as_search_requests():
    profiles = load_profiles()
    assert len(profiles) == 8
    assert len({p.id for p in profiles}) == 8
    assert any(p.request.model_dump(exclude_defaults=True) == {} for p in profiles), (
        "one empty profile"
    )
