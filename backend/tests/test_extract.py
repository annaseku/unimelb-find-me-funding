"""The crawler's text extraction keeps body copy and drops page chrome."""

from backend.crawler.extract import extract_deadline, extract_funding_amount, extract_title_and_text

PAGE = """
<html><head><title>Reef Grant</title></head><body>
<header>Site Logo</header>
<nav><a>Home</a><a>About Us</a><a>Donate</a></nav>
<main><h1>Reef Grant</h1><p>We fund coral reef research in Australia.</p></main>
<aside>Related links</aside>
<footer>Privacy Contact</footer>
</body></html>
"""


def test_extract_drops_navigation_header_and_footer():
    title, text = extract_title_and_text(PAGE)
    assert title == "Reef Grant"
    assert text == "Reef Grant We fund coral reef research in Australia."


def test_extract_without_main_keeps_the_body():
    _, text = extract_title_and_text("<html><body><nav>Menu</nav><p>Body copy.</p></body></html>")
    assert text == "Body copy."


def test_a_dollar_figure_followed_by_a_word_starting_with_m_is_not_millions():
    assert extract_funding_amount("We offer $500 more to early career researchers") == "$500"


def test_dollar_amounts_keep_their_multiplier():
    assert extract_funding_amount("Up to $1.2 million over three years") == "$1.2 million"
    assert extract_funding_amount("Grants of AUD 500k") == "AUD 500k"


def test_a_dollar_sign_without_digits_is_not_an_amount():
    assert extract_funding_amount("Costs in $, see the budget guide") is None


def test_slash_deadlines_are_read_day_first():
    _raw, parsed = extract_deadline("Applications close: 03/04/2026 at 5pm")
    assert parsed == "2026-04-03"
