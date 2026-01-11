import pytest
from utils.sanitize import clean_html, escape_text, linkify_text

def test_clean_html_basic():
    assert clean_html("<p>Hello</p>") == "<p>Hello</p>"
    # Bleach with strip=True removes the tag but keeps the content if not in tags
    # Wait, bleach.clean(strip=True) for <script> content? 
    # Usually bleach strips scripts content entirely because it's dangerous.
    assert clean_html("<script>alert(1)</script>") == "alert(1)"

def test_clean_html_strips_unsafe():
    unsafe = '<img src=x onerror=alert(1)> <a href="javascript:alert(1)">link</a>'
    cleaned = clean_html(unsafe)
    assert "onerror" not in cleaned
    assert "javascript:" not in cleaned

def test_clean_html_allows_safe():
    safe = '<div class="custom">Colored</div> <img src="/static/cat.png" alt="cat">'
    cleaned = clean_html(safe)
    assert "Colored" in cleaned
    assert 'class="custom"' in cleaned
    assert 'src="/static/cat.png"' in cleaned
    assert 'alt="cat"' in cleaned

def test_escape_text():
    assert escape_text("<b>bold</b>") == "bold"
    assert escape_text("simple text") == "simple text"

def test_linkify_text():
    text = "Visit https://google.com"
    linkified = linkify_text(text)
    assert '<a href="https://google.com"' in linkified
    assert 'rel="noopener noreferrer"' in linkified
    assert 'target="_blank"' in linkified

def test_clean_html_entities():
    # Bleach escapes < if it's not a tag it knows or if it's suspicious
    # <b> is allowed, so it stays.
    assert "<b>bold</b>" in clean_html("<b>bold</b>")
    assert "&lt;script&gt;" not in clean_html("<script>") # should be stripped if strip=True
