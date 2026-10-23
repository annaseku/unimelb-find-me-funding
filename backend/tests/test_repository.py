"""Repository lookup and data-source selection."""

import pytest

from backend.data.repository import OpportunityRepository, get_repository
from backend.data.sqlite_repository import SqliteRepository
from backend.evals.corpus import load_corpus


@pytest.fixture(autouse=True)
def clear_repository_cache():
    get_repository.cache_clear()
    yield
    get_repository.cache_clear()


def test_repository_get_and_missing():
    repo = OpportunityRepository(load_corpus())
    first = repo.all()[0]
    assert repo.get(first.id) == first
    assert repo.get("does-not-exist") is None


def test_unset_data_source_reads_sqlite(monkeypatch, corpus_db):
    monkeypatch.delenv("FMF_DATA_SOURCE", raising=False)
    monkeypatch.setenv("FMF_DB_PATH", str(corpus_db))
    repo = get_repository()
    assert isinstance(repo, SqliteRepository)
    assert len(repo.all()) == 30


@pytest.mark.parametrize("source", ["unknown", "mock", ""])
def test_unknown_data_source_names_the_valid_values(monkeypatch, source):
    monkeypatch.setenv("FMF_DATA_SOURCE", source)
    with pytest.raises(RuntimeError, match=r"sqlite.*postgres"):
        get_repository()


def test_sqlite_missing_file_raises_without_creating_it(monkeypatch, tmp_path):
    db = tmp_path / "missing.db"
    monkeypatch.setenv("FMF_DATA_SOURCE", "sqlite")
    monkeypatch.setenv("FMF_DB_PATH", str(db))
    with pytest.raises(FileNotFoundError, match="no crawler database at"):
        get_repository()
    assert not db.exists()
