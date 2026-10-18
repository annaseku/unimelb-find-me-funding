"""The crawler's text extraction keeps body copy and drops page chrome."""

from backend.crawler.extract import extract_title_and_text

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
