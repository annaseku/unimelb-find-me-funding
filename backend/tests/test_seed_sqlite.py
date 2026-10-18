"""The evals corpus seeds an idempotent SQLite test fixture."""

from backend.data.sqlite_repository import SqliteRepository
from backend.evals.corpus import corpus_records, load_corpus
from backend.evals.seed_sqlite import main, seed


def test_seed_creates_a_database_with_every_corpus_opportunity(tmp_path):
    db = tmp_path / "fixture.db"
    assert seed(db) == 30
    assert {o.id for o in SqliteRepository(db).all()} == {o.id for o in load_corpus()}


def test_main_prints_the_count_and_database_path(tmp_path, capsys):
    db = tmp_path / "fixture.db"
    assert main([str(db)]) == 0
    assert capsys.readouterr().out == f"seeded 30 opportunities into {db}\n"
    assert len(SqliteRepository(db).all()) == 30


def test_seeding_twice_keeps_thirty_rows(tmp_path):
    db = tmp_path / "fixture.db"
    assert seed(db) == 30
    assert seed(db) == 30
    assert len(SqliteRepository(db).all()) == 30


def test_seed_upserts_supplied_records_from_an_iterable(tmp_path):
    db = tmp_path / "fixture.db"
    records = corpus_records()[:1]
    assert seed(db, iter(records)) == 1
    records[0].opportunity.title = "Updated scheme"
    assert seed(db, iter(records)) == 1
    served = SqliteRepository(db).all()
    assert len(served) == 1
    assert served[0].title == "Updated scheme"


def test_seed_with_no_records_leaves_an_empty_repository(tmp_path):
    db = tmp_path / "fixture.db"
    assert seed(db, []) == 0
    assert SqliteRepository(db).all() == []
