"""SEO audit engine."""

import re
import json
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class SEOAuditor:
    """Technical SEO auditor."""
    
    def __init__(self, url: str, timeout: int = 10):
        """Initialize auditor.
        
        Args:
            url: URL to audit
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.parsed_url = urlparse(url)
        self.base_domain = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
    
    def audit(self) -> Dict:
        """Run full audit.
        
        Returns:
            Dictionary with audit results
        """
        results = {
            "url": self.url,
            "meta": self._audit_meta(),
            "opengraph": self._audit_opengraph(),
            "schema": self._audit_schema(),
            "robots": self._audit_robots(),
            "sitemap": self._audit_sitemap(),
            "security_headers": self._audit_security_headers()
        }
        return results
    
    def _fetch_html(self) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML."""
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, 'html.parser')
        except Exception:
            return None
    
    def _audit_meta(self) -> Dict:
        """Audit meta tags."""
        soup = self._fetch_html()
        if not soup:
            return {"error": "Failed to fetch page"}
        
        title = soup.find('title')
        description = soup.find('meta', attrs={'name': 'description'})
        
        return {
            "title": title.get_text(strip=True) if title else None,
            "title_length": len(title.get_text(strip=True)) if title else 0,
            "description": description.get('content') if description else None,
            "description_length": len(description.get('content')) if description else 0
        }
    
    def _audit_opengraph(self) -> Dict:
        """Audit OpenGraph tags."""
        soup = self._fetch_html()
        if not soup:
            return {"error": "Failed to fetch page"}
        
        og_tags = {}
        for tag in soup.find_all('meta', property=re.compile(r'^og:')):
            og_tags[tag.get('property')] = tag.get('content')
        
        return og_tags
    
    def _audit_schema(self) -> List[Dict]:
        """Audit JSON-LD schema."""
        soup = self._fetch_html()
        if not soup:
            return [{"error": "Failed to fetch page"}]
        
        schemas = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schemas.append(json.loads(script.string))
            except json.JSONDecodeError:
                pass
        
        return schemas
    
    def _audit_robots(self) -> Dict:
        """Audit robots.txt."""
        robots_url = urljoin(self.base_domain, '/robots.txt')
        try:
            resp = requests.get(robots_url, timeout=self.timeout)
            return {
                "url": robots_url,
                "status_code": resp.status_code,
                "exists": resp.status_code == 200,
                "content_length": len(resp.text) if resp.status_code == 200 else 0
            }
        except Exception:
            return {"url": robots_url, "exists": False}
    
    def _audit_sitemap(self) -> Dict:
        """Audit sitemap.xml."""
        sitemap_url = urljoin(self.base_domain, '/sitemap.xml')
        try:
            resp = requests.get(sitemap_url, timeout=self.timeout)
            return {
                "url": sitemap_url,
                "status_code": resp.status_code,
                "exists": resp.status_code == 200,
                "content_length": len(resp.text) if resp.status_code == 200 else 0
            }
        except Exception:
            return {"url": sitemap_url, "exists": False}
    
    def _audit_security_headers(self) -> Dict:
        """Audit HTTP security headers."""
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            headers = resp.headers
            
            return {
                "strict_transport_security": headers.get('Strict-Transport-Security'),
                "content_security_policy": headers.get('Content-Security-Policy'),
                "x_frame_options": headers.get('X-Frame-Options'),
                "x_content_type_options": headers.get('X-Content-Type-Options')
            }
        except Exception:
            return {"error": "Failed to fetch headers"}
