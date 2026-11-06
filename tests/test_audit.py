"""Tests for SEOAuditor."""

import pytest
import requests
from sitepulse import SEOAuditor


def test_auditor_initialization():
    """Test auditor initialization."""
    auditor = SEOAuditor("https://example.com")
    assert auditor.url == "https://example.com"
    assert auditor.base_domain == "https://example.com"


def test_auditor_strips_trailing_slash():
    """Test URL normalization."""
    auditor = SEOAuditor("https://example.com/")
    assert auditor.url == "https://example.com"


def test_audit_structure():
    """Test audit returns expected structure."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "url" in results
    assert "meta" in results
    assert "opengraph" in results
    assert "schema" in results
    assert "robots" in results
    assert "sitemap" in results
    assert "security_headers" in results
    assert "viewport" in results
    assert "images" in results
    assert "meta_robots" in results


def test_twitter_cards_audit():
    """Test Twitter Card meta tags audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "twitter_cards" in results
    twitter = results["twitter_cards"]
    assert "present" in twitter
    assert "card_type" in twitter
    assert "tags" in twitter
    assert "missing_required" in twitter
    assert "valid" in twitter


def test_canonical_audit():
    """Test canonical URL audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "canonical" in results
    assert "present" in results["canonical"]


def test_headings_audit():
    """Test heading hierarchy audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "headings" in results
    assert "h1_count" in results["headings"]
    assert "h1_valid" in results["headings"]


def test_viewport_audit():
    """Test viewport meta tag audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "viewport" in results
    viewport = results["viewport"]
    assert "present" in viewport
    assert "has_width_device_width" in viewport
    assert "has_initial_scale" in viewport


def test_images_audit():
    """Test image alt text coverage audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "images" in results
    images = results["images"]
    assert "total" in images
    assert "with_alt" in images
    assert "missing_alt" in images
    assert "coverage_percent" in images
    assert "missing_details" in images


def test_meta_robots_audit():
    """Test meta robots tag audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "meta_robots" in results
    meta_robots = results["meta_robots"]
    assert "present" in meta_robots
    assert "noindex" in meta_robots
    assert "nofollow" in meta_robots
    assert "none" in meta_robots
    assert "directives" in meta_robots


def test_content_audit():
    """Test content analysis audit."""
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    assert "content" in results
    content = results["content"]
    assert "word_count" in content
    assert "reading_time_minutes" in content
    assert "sentence_count" in content
    assert "avg_words_per_sentence" in content
    assert "syllable_count" in content
    assert "flesch_reading_ease" in content
    assert "readability_grade" in content


def test_html_is_fetched_once_per_audit(monkeypatch):
    """Test that audit() fetches the live page only once (caching regression guard).

    Before this fix, every _audit_* method re-fetched the page (8+ HTTP calls per audit()).
    Now HTML and headers are fetched once each; robots.txt/sitemap.xml are separate URLs.

    Uses fake responses so the test is deterministic, network-free, and isolated
    from other tests' real network calls.
    """
    import sitepulse.audit as audit_module
    from unittest.mock import MagicMock

    calls: dict[str, int] = {}

    def fake_get(url, *args, **kwargs):
        calls[url] = calls.get(url, 0) + 1
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"<html><title>Example</title><meta name='description' content='desc'><img src='/a.png'><img src='/b.png'><meta name='robots' content='index,follow'></html>"
        resp.text = resp.content.decode()
        resp.headers = {"Content-Type": "text/html"}
        resp.raise_for_status = MagicMock()
        return resp

    monkeypatch.setattr(audit_module.requests, "get", fake_get)
    auditor = SEOAuditor("https://example.com", timeout=5)
    auditor.audit()

    # Main page: one HTML fetch + one headers fetch = exactly 2
    assert calls["https://example.com"] == 2, f"Main page fetched {calls['https://example.com']} times, expected 2"
    # robots.txt and sitemap.xml are distinct, legitimate fetches (1 each)
    assert calls.get("https://example.com/robots.txt", 0) == 1
    assert calls.get("https://example.com/sitemap.xml", 0) == 1


def test_twitter_cards_validation(monkeypatch):
    """Test Twitter Card validation logic with mocked HTML."""
    import sitepulse.audit as audit_module
    from unittest.mock import MagicMock

    calls: dict[str, int] = {}

    def fake_get(url, *args, **kwargs):
        calls[url] = calls.get(url, 0) + 1
        resp = MagicMock()
        resp.status_code = 200
        # HTML with valid Twitter Card (summary_large_image)
        resp.content = b"""
        <html>
            <head>
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:title" content="Test Title">
                <meta name="twitter:description" content="Test Description">
                <meta name="twitter:image" content="https://example.com/image.png">
            </head>
            <body></body>
        </html>
        """
        resp.text = resp.content.decode()
        resp.headers = {"Content-Type": "text/html"}
        resp.raise_for_status = MagicMock()
        return resp

    monkeypatch.setattr(audit_module.requests, "get", fake_get)
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    twitter = results["twitter_cards"]
    assert twitter["present"] is True
    assert twitter["card_type"] == "summary_large_image"
    assert twitter["valid"] is True
    assert twitter["missing_required"] == []
    assert "twitter:card" in twitter["tags"]
    assert "twitter:title" in twitter["tags"]
    assert "twitter:description" in twitter["tags"]
    assert "twitter:image" in twitter["tags"]


def test_twitter_cards_missing_required(monkeypatch):
    """Test Twitter Card validation detects missing required tags."""
    import sitepulse.audit as audit_module
    from unittest.mock import MagicMock

    calls: dict[str, int] = {}

    def fake_get(url, *args, **kwargs):
        calls[url] = calls.get(url, 0) + 1
        resp = MagicMock()
        resp.status_code = 200
        # HTML with incomplete Twitter Card (missing twitter:description and twitter:image)
        resp.content = b"""
        <html>
            <head>
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:title" content="Test Title">
            </head>
            <body></body>
        </html>
        """
        resp.text = resp.content.decode()
        resp.headers = {"Content-Type": "text/html"}
        resp.raise_for_status = MagicMock()
        return resp

    monkeypatch.setattr(audit_module.requests, "get", fake_get)
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    twitter = results["twitter_cards"]
    assert twitter["present"] is True
    assert twitter["card_type"] == "summary_large_image"
    assert twitter["valid"] is False
    assert "twitter:description" in twitter["missing_required"]
    assert "twitter:image" in twitter["missing_required"]


def test_twitter_cards_no_tags(monkeypatch):
    """Test Twitter Card audit when no Twitter tags present."""
    import sitepulse.audit as audit_module
    from unittest.mock import MagicMock

    calls: dict[str, int] = {}

    def fake_get(url, *args, **kwargs):
        calls[url] = calls.get(url, 0) + 1
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"<html><head><title>No Twitter Cards</title></head><body></body></html>"
        resp.text = resp.content.decode()
        resp.headers = {"Content-Type": "text/html"}
        resp.raise_for_status = MagicMock()
        return resp

    monkeypatch.setattr(audit_module.requests, "get", fake_get)
    auditor = SEOAuditor("https://example.com", timeout=5)
    results = auditor.audit()

    twitter = results["twitter_cards"]
    assert twitter["present"] is False
    assert twitter["valid"] is False
    assert twitter["card_type"] is None
    assert twitter["tags"] == {}