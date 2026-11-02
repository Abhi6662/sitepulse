"""Tests for SEOAuditor."""

import pytest
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