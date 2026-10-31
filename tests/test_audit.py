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
