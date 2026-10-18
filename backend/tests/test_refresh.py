"""Offline coverage of the scheduled crawl, normalise and publish orchestration."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import date
from types import ModuleType

import pytest

from backend.data import refresh
from backend.normaliser.pipeline import PipelineStats, load_normalised


def fail_if_called(*args, **kwargs):
    pytest.fail("dry-run or invalid configuration must not run the pipeline")


@pytest.fixture
def blocked_pipeline(monkeypatch):
    for name in ("crawl", "refetch", "normalise", "publish_to_postgres"):
        monkeypatch.setattr(refresh, name, fail_if_called)


def test_seed_profiles_cover_all_23_divisions_with_nonempty_names():
    profiles = refresh.load_seed_profiles()
    assert len(profiles) == 23
    assert {p.for_division for p in profiles} == {str(n) for n in range(30, 53)}
    assert all(p.field_of_research.strip() for p in profiles)
    assert profiles[0].field_of_research == "Agricultural, Veterinary and Food Sciences"


def test_load_seed_profiles_reads_the_requested_file(tmp_path):
    path = tmp_path / "profiles.json"
    path.write_text(
        json.dumps({"profiles": [{"for_division": "42", "field_of_research": "Health"}]})
    )
    assert refresh.load_seed_profiles(path) == [
        refresh.SeedProfile(for_division="42", field_of_research="Health")
    ]


def test_five_profile_rotation_covers_every_area_once_before_wrapping():
    profiles = refresh.load_seed_profiles()
    selected = [p for week in range(5) for p in refresh.select_profiles(profiles, week, 5)]
    assert selected[:23] == profiles
    assert selected[23:] == profiles[:2]
    assert refresh.select_profiles(profiles, 4, 5) == profiles[20:] + profiles[:2]
    assert refresh.select_profiles(profiles, 23, 5) == profiles[:5]


@pytest.mark.parametrize("per_run", [23, 100])
def test_rotation_returns_all_profiles_in_order_when_the_slice_covers_them(per_run):
    profiles = refresh.load_seed_profiles()
    assert refresh.select_profiles(profiles, 7, per_run) == profiles


def test_rotation_handles_an_empty_seed_list():
    assert refresh.select_profiles([], 4, 5) == []


def test_dry_run_prints_ten_profiles_and_search_budget_without_credentials_or_crawler(
    monkeypatch, capsys, blocked_pipeline
):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    monkeypatch.setitem(sys.modules, "backend.crawler.crawler", None)
    monkeypatch.setitem(sys.modules, "backend.crawler.discoverURL", None)

    assert refresh.main(["--dry-run", "--week", "0"]) == 0

    output = capsys.readouterr()
    assert output.err == ""
    for profile in refresh.load_seed_profiles()[:10]:
        assert f"{profile.for_division}: {profile.field_of_research}" in output.out
    assert "SerpApi searches: 40" in output.out
    assert len(output.out.splitlines()) == 11


def test_dry_run_counts_generated_queries_instead_of_assuming_four(
    monkeypatch, capsys, blocked_pipeline
):
    monkeypatch.setattr(refresh, "generate_seed_queries", lambda **kwargs: ["a", "b"])
    assert refresh.main(["--dry-run", "--per-run", "3"]) == 0
    assert "SerpApi searches: 6" in capsys.readouterr().out


def test_dry_run_all_reports_all_23_profiles_and_92_searches(capsys, blocked_pipeline):
    assert refresh.main(["--dry-run", "--all"]) == 0
    output = capsys.readouterr().out
    assert len(output.splitlines()) == 24
    assert "SerpApi searches: 92" in output


def test_crawl_calls_the_lazy_crawler_once_per_research_area(monkeypatch):
    calls = []
    fake_crawler = ModuleType("backend.crawler.crawler")
    fake_crawler.run_crawl = lambda **kwargs: calls.append(kwargs)
    monkeypatch.setitem(sys.modules, "backend.crawler.crawler", fake_crawler)
    profiles = refresh.load_seed_profiles()[:2]

    assert refresh.crawl(profiles) is None
    assert calls == [
        {"field_of_research": "Agricultural, Veterinary and Food Sciences"},
        {"field_of_research": "Biological Sciences"},
    ]


@pytest.mark.parametrize("all_profiles", [False, True])
def test_main_runs_crawl_then_normalise_then_publish(monkeypatch, tmp_path, capsys, all_profiles):
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key")
    monkeypatch.setenv("FMF_DATABASE_URL", "postgresql://env-url")
    calls = []
    db = tmp_path / "crawler.db"
    stats = PipelineStats(rows_read=8, normalised=7)
    monkeypatch.setattr(refresh, "crawl", lambda profiles: calls.append(("crawl", profiles)))

    def normalise(db_path, today, use_llm):
        calls.append(("normalise", db_path, today, use_llm))
        return stats

    def publish(db_path, database_url):
        calls.append(("publish", db_path, database_url))
        return 7

    monkeypatch.setattr(refresh, "normalise", normalise)
    monkeypatch.setattr(refresh, "publish_to_postgres", publish)
    args = ["--week", "4", "--per-run", "5", "--db-path", str(db), "--no-llm"]
    if all_profiles:
        args.append("--all")
    else:
        args.extend(["--database-url", "postgresql://flag-url"])

    assert refresh.main(args) == 0

    profiles = refresh.load_seed_profiles()
    assert calls == [
        ("crawl", profiles if all_profiles else profiles[20:] + profiles[:2]),
        ("normalise", str(db), date.today(), False),
        ("publish", str(db), "postgresql://env-url" if all_profiles else "postgresql://flag-url"),
    ]
    assert "published: 7" in capsys.readouterr().out


def test_skip_publish_needs_no_database_url_and_never_publishes(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key")
    monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    calls = []
    db = tmp_path / "crawler.db"
    monkeypatch.setattr(refresh, "crawl", lambda profiles: calls.append("crawl"))
    monkeypatch.setattr(
        refresh,
        "normalise",
        lambda db_path, today, use_llm: calls.append("normalise") or PipelineStats(),
    )
    monkeypatch.setattr(
        refresh, "publish_to_postgres", lambda *a: pytest.fail("publish must not run")
    )

    assert refresh.main(["--skip-publish", "--no-llm", "--db-path", str(db)]) == 0
    assert calls == ["crawl", "normalise"]
    assert f"FMF_DB_PATH={db}" in capsys.readouterr().out


@pytest.mark.parametrize("key", [None, "", "   "])
def test_missing_serpapi_key_returns_two_before_running_any_stage(
    monkeypatch, capsys, blocked_pipeline, key
):
    if key is None:
        monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    else:
        monkeypatch.setenv("SERPAPI_API_KEY", key)
    assert refresh.main(["--database-url", "postgresql://test"]) == 2
    output = capsys.readouterr()
    assert "SERPAPI_API_KEY" in output.err
    assert len(output.err.splitlines()) == 1


@pytest.mark.parametrize("url", [None, "", "   "])
def test_missing_database_url_returns_two_before_running_any_stage(
    monkeypatch, capsys, blocked_pipeline, url
):
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key")
    if url is None:
        monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("FMF_DATABASE_URL", url)
    assert refresh.main([]) == 2
    output = capsys.readouterr()
    assert "FMF_DATABASE_URL" in output.err
    assert len(output.err.splitlines()) == 1


@pytest.mark.parametrize("use_llm", [False, True])
def test_normalise_selects_the_optional_extractor(monkeypatch, tmp_path, use_llm):
    calls = []
    extractor = object()

    def extractor_from_env():
        calls.append("extractor")
        return extractor

    def normalise_database(db_path, today, extractor=None):
        calls.append((db_path, today, extractor))
        return PipelineStats(normalised=3)

    monkeypatch.setattr(refresh, "extractor_from_env", extractor_from_env)
    monkeypatch.setattr(refresh, "normalise_database", normalise_database)
    db = tmp_path / "crawler.db"
    today = date(2026, 10, 18)
    assert refresh.normalise(db, today, use_llm).normalised == 3
    assert calls == (["extractor"] if use_llm else []) + [
        (db, today, extractor if use_llm else None)
    ]


def test_publish_to_postgres_passes_sqlite_records_to_the_publisher(monkeypatch, tmp_path):
    calls = []
    records = []
    db = tmp_path / "crawler.db"

    def read_records(db_path):
        calls.append(("read", db_path))
        return records

    def publish(database_url, payload, run):
        calls.append(("publish", database_url, payload, run))
        return 3

    monkeypatch.setattr(refresh, "latest_run_from_sqlite", lambda db_path: "run")
    monkeypatch.setattr(refresh, "records_from_sqlite", read_records)
    monkeypatch.setattr(refresh, "publish", publish)
    assert refresh.publish_to_postgres(db, "postgresql://test") == 3
    assert calls == [("read", db), ("publish", "postgresql://test", records, "run")]


def test_no_llm_normalises_real_crawled_rows(monkeypatch, normalised_sqlite_db, today):
    import sqlite3

    monkeypatch.setattr(refresh, "extractor_from_env", fail_if_called)
    with sqlite3.connect(normalised_sqlite_db) as conn:
        conn.execute("DELETE FROM normalised_opportunities")
    stats = refresh.normalise(normalised_sqlite_db, today, False)
    assert stats.normalised > 0
    with sqlite3.connect(normalised_sqlite_db) as conn:
        assert len(load_normalised(conn)) == stats.normalised


@pytest.mark.parametrize("per_run", ["0", "-1"])
def test_nonpositive_per_run_is_rejected(per_run, blocked_pipeline):
    with pytest.raises(SystemExit) as error:
        refresh.main(["--dry-run", "--per-run", per_run])
    assert error.value.code == 2


@pytest.mark.parametrize("skip_publish", [False, True])
def test_refetch_needs_no_serpapi_and_runs_before_normalise_and_publish(
    monkeypatch, tmp_path, capsys, skip_publish
):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    monkeypatch.setenv("FMF_DATABASE_URL", "postgresql://env-url")
    for name in ("crawl", "load_seed_profiles", "generate_seed_queries"):
        monkeypatch.setattr(refresh, name, fail_if_called)
    urls = ["https://example.org/a", "https://example.org/b"]
    calls = []
    db = str(tmp_path / "crawler.db")
    monkeypatch.setattr(refresh, "DB_PATH", db)
    monkeypatch.setattr(
        refresh,
        "read_published_urls",
        lambda database_url: calls.append(("read", database_url)) or urls,
    )
    monkeypatch.setattr(
        refresh, "refetch", lambda targets: calls.append(("refetch", targets)) or (1, 1)
    )
    monkeypatch.setattr(
        refresh,
        "normalise",
        lambda db_path, today, use_llm: (
            calls.append(("normalise", db_path, today, use_llm)) or PipelineStats(normalised=1)
        ),
    )
    monkeypatch.setattr(
        refresh,
        "publish_to_postgres",
        lambda db_path, database_url: calls.append(("publish", db_path, database_url)) or 1,
    )
    args = ["--refetch", "--db-path", db]
    if skip_publish:
        args.extend(["--skip-publish", "--no-llm"])
    else:
        args.extend(["--database-url", "postgresql://flag-url"])

    assert refresh.main(args) == 0
    database_url = "postgresql://env-url" if skip_publish else "postgresql://flag-url"
    assert calls == [
        ("read", database_url),
        ("refetch", urls),
        ("normalise", db, date.today(), not skip_publish),
    ] + ([] if skip_publish else [("publish", db, database_url)])
    output = capsys.readouterr()
    assert output.err == ""
    assert output.out.splitlines()[:4] == [
        "urls: 2",
        "fetched: 1",
        "fetch failed: 1",
        "normalised: 1",
    ]
    assert "llm calls: 0" in output.out
    assert ("not published:" if skip_publish else "published: 1") in output.out


@pytest.mark.parametrize("urls", [[], ["https://example.org/a", "https://example.org/b"]])
def test_refetch_dry_run_only_reads_and_counts_urls(monkeypatch, capsys, blocked_pipeline, urls):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    monkeypatch.setenv("FMF_DATABASE_URL", "postgresql://test")
    monkeypatch.setitem(sys.modules, "backend.crawler.crawler", None)
    for name in ("load_seed_profiles", "generate_seed_queries"):
        monkeypatch.setattr(refresh, name, fail_if_called)
    calls = []
    monkeypatch.setattr(
        refresh,
        "read_published_urls",
        lambda database_url: calls.append(database_url) or urls,
    )
    assert refresh.main(["--refetch", "--dry-run"]) == 0
    assert calls == ["postgresql://test"]
    assert capsys.readouterr().out == f"urls: {len(urls)}\n"


@pytest.mark.parametrize("conflict", [["--all"], ["--week", "0"]])
def test_refetch_rejects_seed_rotation_flags(monkeypatch, blocked_pipeline, conflict):
    monkeypatch.setattr(refresh, "read_published_urls", fail_if_called)
    with pytest.raises(SystemExit) as error:
        refresh.main(["--refetch", *conflict])
    assert error.value.code == 2


@pytest.mark.parametrize("extra", [[], ["--dry-run"], ["--skip-publish"]])
@pytest.mark.parametrize("database_url", [None, "", "   "])
def test_refetch_requires_database_before_any_stage(
    monkeypatch, capsys, blocked_pipeline, extra, database_url
):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    if database_url is None:
        monkeypatch.delenv("FMF_DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("FMF_DATABASE_URL", database_url)
    monkeypatch.setattr(refresh, "read_published_urls", fail_if_called)
    monkeypatch.setattr(refresh, "load_seed_profiles", fail_if_called)
    assert refresh.main(["--refetch", *extra]) == 2
    assert "FMF_DATABASE_URL" in capsys.readouterr().err


def test_refetch_database_error_returns_two_without_fetching(monkeypatch, capsys, blocked_pipeline):
    import psycopg

    def cannot_connect(database_url):
        raise psycopg.OperationalError("connection refused")

    monkeypatch.setattr(refresh, "read_published_urls", cannot_connect)
    assert refresh.main(["--refetch", "--dry-run", "--database-url", "postgresql://test"]) == 2
    assert "connection refused" in capsys.readouterr().err


def test_refetch_rejects_a_different_publish_database(
    monkeypatch, tmp_path, capsys, blocked_pipeline
):
    monkeypatch.setattr(refresh, "read_published_urls", fail_if_called)
    with pytest.raises(SystemExit) as error:
        refresh.main(
            [
                "--refetch",
                "--database-url",
                "postgresql://test",
                "--db-path",
                str(tmp_path / "other.db"),
            ]
        )
    assert error.value.code == 2
    assert "--db-path" in capsys.readouterr().err


@pytest.mark.parametrize("empty", [False, True])
def test_refetch_initialises_then_crawls_each_url_and_counts_sqlite_results(
    monkeypatch, tmp_path, empty
):
    from backend.crawler.storage import init_db, mark_fetch_failed, save_opportunity

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    calls = []
    urls = (
        [] if empty else ["https://example.org/a", "https://example.org/b", "https://example.org/c"]
    )
    fake_crawler = ModuleType("backend.crawler.crawler")

    def initialise():
        calls.append("init")
        init_db()

    def crawl_url(url, source_query):
        calls.append((url, source_query))
        if url.endswith("/a"):
            save_opportunity(
                url, {"title": "Grant", "raw_text": "Research grant funding"}, source_query
            )
        elif url.endswith("/b"):
            mark_fetch_failed(url)
        # /c models a robots.txt rejection, which stores nothing.

    fake_crawler.init_db = initialise
    fake_crawler.crawl_url = crawl_url
    monkeypatch.setitem(sys.modules, "backend.crawler.crawler", fake_crawler)
    assert refresh.refetch(urls) == ((0, 0) if empty else (1, 2))
    assert calls == ["init", *((url, "refetch") for url in urls)]
    with sqlite3.connect(refresh.DB_PATH) as conn:
        assert dict(conn.execute("SELECT url, fetch_failed FROM opportunities")) == (
            {} if empty else {urls[0]: 0, urls[1]: 1, urls[2]: 1}
        )


def test_refetch_reprocesses_cached_pages_and_does_not_publish_failed_cached_records(
    monkeypatch, normalised_sqlite_db, today
):
    from backend.crawler.storage import init_db, mark_fetch_failed
    from backend.normaliser.pipeline import read_crawled_rows

    monkeypatch.chdir(normalised_sqlite_db.parent)
    monkeypatch.setattr(refresh, "DB_PATH", str(normalised_sqlite_db))
    with sqlite3.connect(normalised_sqlite_db) as conn:
        rows = read_crawled_rows(conn)
    good, failed, blocked = (row.url for row in rows[:3])
    fake_crawler = ModuleType("backend.crawler.crawler")
    fake_crawler.init_db = lambda: init_db(str(normalised_sqlite_db))

    def crawl_url(url, source_query):
        if url == good:
            with sqlite3.connect(normalised_sqlite_db) as conn:
                conn.execute("UPDATE opportunities SET fetch_failed = 0 WHERE url = ?", (url,))
        elif url == failed:
            mark_fetch_failed(url, str(normalised_sqlite_db))

    fake_crawler.crawl_url = crawl_url
    monkeypatch.setitem(sys.modules, "backend.crawler.crawler", fake_crawler)
    assert refresh.refetch([good, failed, blocked]) == (1, 2)
    stats = refresh.normalise(normalised_sqlite_db, today, False)
    assert stats.normalised == 1
    published_urls = {r.opportunity.url for r in refresh.records_from_sqlite(normalised_sqlite_db)}
    assert good in published_urls
    assert failed not in published_urls
    assert blocked not in published_urls
