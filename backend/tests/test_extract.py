"""Tests for backend.crawler.extract and the crawler table's description
column: page text without menus, headers and footers, so the result card's
overview is the scheme's own words."""

from __future__ import annotations

import sqlite3

from backend.crawler.extract import extract_fields
from backend.crawler.storage import init_db, save_opportunity

BODY = (
    "The Discovery Projects scheme provides funding of up to $500,000 a year for research "
    "projects. Applications close 1 March 2027. Eligibility: researchers at Australian "
    "universities."
)
PAGE = f"""<html><head><title>Discovery Projects | ARC</title>
<meta name="description" content="Discovery Projects support excellent basic and applied
research by individuals and teams."></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<header><ul><li>Home</li><li>About</li><li>Funding</li></ul></header>
<nav>Grants Policy News Contact</nav>
<div class="breadcrumb">Home / Funding / Discovery</div>
<div id="cookie-banner">We use cookies</div>
<div role="navigation">Quick links</div>
<main><h1>Discovery Projects</h1><p>{BODY}</p></main>
<aside>Related schemes</aside>
<footer>Copyright Privacy Accessibility</footer></body></html>"""


def test_page_text_drops_menus_headers_footers_and_banners():
    text = extract_fields(PAGE)["raw_text"]
    assert text == f"Discovery Projects {BODY}"


def test_the_meta_description_is_kept_as_the_page_summary():
    fields = extract_fields(PAGE)
    assert fields["description"] == (
        "Discovery Projects support excellent basic and applied research by individuals and teams."
    )
    assert fields["title"] == "Discovery Projects | ARC"


def test_open_graph_description_is_used_when_there_is_no_meta_description():
    html = '<html><head><meta property="og:description" content="Funds early career work.">'
    html += "</head><body><p>Body text.</p></body></html>"
    assert extract_fields(html)["description"] == "Funds early career work."


def test_a_page_without_main_falls_back_to_the_cleaned_body():
    html = f"<html><body><nav>Home About</nav><div><p>{BODY}</p></div></body></html>"
    fields = extract_fields(html)
    assert fields["raw_text"] == BODY
    assert fields["description"] == ""


def test_a_short_main_teaser_does_not_hide_the_rest_of_the_page():
    html = f"<html><body><main>Teaser</main><div><p>{BODY}</p></div></body></html>"
    assert BODY in extract_fields(html)["raw_text"]


def test_storage_saves_the_description(tmp_path):
    db = str(tmp_path / "crawler.db")
    init_db(db)
    save_opportunity("https://example.org/grant", extract_fields(PAGE), "query", db_path=db)
    with sqlite3.connect(db) as conn:
        (description,) = conn.execute("SELECT description FROM opportunities").fetchone()
    assert description.startswith("Discovery Projects support")


def test_init_db_adds_the_description_column_to_an_older_database(tmp_path):
    db = str(tmp_path / "old.db")
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE opportunities (url TEXT PRIMARY KEY, title TEXT)")
    init_db(db)
    with sqlite3.connect(db) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(opportunities)")}
    assert "description" in columns


def test_a_page_wrapped_in_one_form_keeps_its_content():
    html = f'<html><body><form id="aspnetForm"><nav>Home</nav><p>{BODY}</p></form></body></html>'
    assert extract_fields(html)["raw_text"] == BODY


def test_menus_nested_inside_other_furniture_are_removed_once():
    html = f"""<html><body><div class="site-header"><nav><div class="menu">A B</div></nav></div>
    <p>{BODY}</p></body></html>"""
    assert extract_fields(html)["raw_text"] == BODY
