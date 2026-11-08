"""SEO audit engine."""

import re
import json
import math
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
        self._html_soup: Optional[BeautifulSoup] = None
        self._headers: Optional[Dict] = None

    def audit(self) -> Dict:
        """Run full audit.

        Returns:
            Dictionary with audit results
        """
        # Fetch HTML once and reuse for all page-content audits
        self._fetch_html_once()
        self._fetch_headers_once()

        results = {
            "url": self.url,
            "meta": self._audit_meta(),
            "opengraph": self._audit_opengraph(),
            "schema": self._audit_schema(),
            "twitter_cards": self._audit_twitter_cards(),
            "robots": self._audit_robots(),
            "sitemap": self._audit_sitemap(),
            "security_headers": self._audit_security_headers(),
            "canonical": self._audit_canonical(),
            "headings": self._audit_headings(),
            "viewport": self._audit_viewport(),
            "images": self._audit_images(),
            "meta_robots": self._audit_meta_robots(),
            "content": self._audit_content(),
            "links": self._audit_links(),
        }
        return results

    def _fetch_html_once(self) -> None:
        """Fetch and parse HTML once, caching the result."""
        if self._html_soup is not None:
            return
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            resp.raise_for_status()
            self._html_soup = BeautifulSoup(resp.content, 'html.parser')
        except Exception:
            self._html_soup = None

    def _fetch_headers_once(self) -> None:
        """Fetch HTTP headers once, caching the result."""
        if self._headers is not None:
            return
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            self._headers = dict(resp.headers)
        except Exception:
            self._headers = {}

    def _audit_meta(self) -> Dict:
        """Audit meta tags."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        title = self._html_soup.find('title')
        description = self._html_soup.find('meta', attrs={'name': 'description'})

        return {
            "title": title.get_text(strip=True) if title else None,
            "title_length": len(title.get_text(strip=True)) if title else 0,
            "description": description.get('content') if description else None,
            "description_length": len(description.get('content')) if description else 0
        }

    def _audit_opengraph(self) -> Dict:
        """Audit OpenGraph tags."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        og_tags = {}
        for tag in self._html_soup.find_all('meta', property=re.compile(r'^og:')):
            og_tags[tag.get('property')] = tag.get('content')

        return og_tags

    def _audit_schema(self) -> List[Dict]:
        """Audit JSON-LD schema."""
        if self._html_soup is None:
            return [{"error": "Failed to fetch page"}]

        schemas = []
        for script in self._html_soup.find_all('script', type='application/ld+json'):
            try:
                schemas.append(json.loads(script.string))
            except json.JSONDecodeError:
                pass

        return schemas

    def _audit_twitter_cards(self) -> Dict:
        """Audit Twitter Card meta tags."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        twitter_tags = {}
        for tag in self._html_soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            twitter_tags[tag.get('name')] = tag.get('content')

        # Validate required tags for summary_large_image (most common)
        card_type = twitter_tags.get('twitter:card', '').lower()
        required_tags = {
            'summary': ['twitter:card', 'twitter:title'],
            'summary_large_image': ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'],
            'app': ['twitter:card', 'twitter:title', 'twitter:description'],
            'player': ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:player']
        }

        missing_required = []
        if card_type in required_tags:
            for req in required_tags[card_type]:
                if req not in twitter_tags or not twitter_tags[req]:
                    missing_required.append(req)

        return {
            "present": len(twitter_tags) > 0,
            "card_type": card_type if card_type else None,
            "tags": twitter_tags,
            "missing_required": missing_required,
            "valid": len(missing_required) == 0 and len(twitter_tags) > 0
        }

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
        if not self._headers:
            return {"error": "Failed to fetch headers"}

        headers = self._headers

        return {
            "strict_transport_security": headers.get('Strict-Transport-Security'),
            "content_security_policy": headers.get('Content-Security-Policy'),
            "x_frame_options": headers.get('X-Frame-Options'),
            "x_content_type_options": headers.get('X-Content-Type-Options')
        }

    def _audit_canonical(self) -> Dict:
        """Audit canonical URL."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        canonical = self._html_soup.find('link', rel='canonical')
        return {
            "present": canonical is not None,
            "href": canonical.get('href') if canonical else None
        }

    def _audit_headings(self) -> Dict:
        """Audit heading hierarchy."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        h1_count = len(self._html_soup.find_all('h1'))
        h2_count = len(self._html_soup.find_all('h2'))

        return {
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h1_valid": h1_count == 1  # Should have exactly one H1
        }

    def _audit_viewport(self) -> Dict:
        """Audit viewport meta tag for mobile responsiveness."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        viewport = self._html_soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            return {
                "present": False,
                "content": None,
                "has_width_device_width": False,
                "has_initial_scale": False
            }

        content = viewport.get('content') or ''
        content_lower = content.lower()
        return {
            "present": True,
            "content": content,
            "has_width_device_width": 'width=device-width' in content_lower,
            "has_initial_scale": 'initial-scale' in content_lower
        }

    def _audit_images(self) -> Dict:
        """Audit image alt text coverage."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        images = self._html_soup.find_all('img')
        total = len(images)

        if total == 0:
            return {
                "total": 0,
                "with_alt": 0,
                "missing_alt": 0,
                "coverage_percent": 100.0,
                "missing_details": []
            }

        with_alt = 0
        missing_details = []
        for idx, img in enumerate(images):
            alt = img.get('alt', '') or ''
            alt_stripped = alt.strip()
            if alt_stripped:
                with_alt += 1
            else:
                src = img.get('src', '') or ''
                missing_details.append({
                    "index": idx,
                    "src": src[:100] if src else "inline/no-src"
                })

        return {
            "total": total,
            "with_alt": with_alt,
            "missing_alt": total - with_alt,
            "coverage_percent": round((with_alt / total) * 100, 1),
            "missing_details": missing_details[:10]  # Limit to first 10
        }

    def _audit_meta_robots(self) -> Dict:
        """Audit meta robots tag for indexing directives."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        robots_meta = self._html_soup.find('meta', attrs={'name': 'robots'})
        if not robots_meta:
            return {
                "present": False,
                "content": None,
                "noindex": False,
                "nofollow": False,
                "none": False,
                "directives": []
            }

        content = robots_meta.get('content') or ''
        content_lower = content.lower()
        directives = [d.strip() for d in content_lower.split(',')]

        return {
            "present": True,
            "content": content,
            "noindex": 'noindex' in directives,
            "nofollow": 'nofollow' in directives,
            "none": 'none' in directives,
            "directives": directives
        }

    def _audit_content(self) -> Dict:
        """Audit page content: word count, reading time, readability."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        # Extract visible text content
        # Remove script, style, noscript, and other non-content tags
        for tag in self._html_soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()

        text = self._html_soup.get_text(separator=' ', strip=True)
        words = text.split()
        word_count = len(words)

        # Reading time: average adult reads ~200 words/min
        reading_time_minutes = math.ceil(word_count / 200) if word_count > 0 else 0

        # Simple readability: Flesch Reading Ease approximation
        # Count sentences (rough: . ! ?)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Count syllables roughly (vowel groups)
        def count_syllables(word):
            word = word.lower()
            vowels = 'aeiouy'
            count = 0
            prev_was_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    count += 1
                prev_was_vowel = is_vowel
            # Adjust for silent e
            if word.endswith('e') and count > 1:
                count -= 1
            return max(1, count)

        syllable_count = sum(count_syllables(w) for w in words)

        # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        flesch_score = None
        if sentence_count > 0 and word_count > 0:
            flesch_score = round(
                206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count),
                1
            )

        return {
            "word_count": word_count,
            "reading_time_minutes": reading_time_minutes,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": round(word_count / sentence_count, 1) if sentence_count > 0 else 0,
            "syllable_count": syllable_count,
            "flesch_reading_ease": flesch_score,
            "readability_grade": self._grade_from_flesch(flesch_score) if flesch_score is not None else None
        }

    def _grade_from_flesch(self, score: float) -> str:
        """Convert Flesch Reading Ease score to grade level description."""
        if score >= 90:
            return "5th grade (Very Easy)"
        elif score >= 80:
            return "6th grade (Easy)"
        elif score >= 70:
            return "7th grade (Fairly Easy)"
        elif score >= 60:
            return "8th-9th grade (Standard)"
        elif score >= 50:
            return "10th-12th grade (Fairly Difficult)"
        elif score >= 30:
            return "College (Difficult)"
        else:
            return "College Graduate (Very Difficult)"

    def _audit_links(self) -> Dict:
        """Audit internal and external links on the page."""
        if self._html_soup is None:
            return {"error": "Failed to fetch page"}

        links = self._html_soup.find_all('a', href=True)
        internal = []
        external = []

        for link in links:
            href = link.get('href', '').strip()
            if not href:
                continue

            # Resolve relative URLs
            absolute_url = urljoin(self.url, href)

            # Categorize
            if absolute_url.startswith(self.base_domain):
                internal.append({
                    "url": absolute_url,
                    "anchor": link.get_text(strip=True)[:100],
                    "rel": link.get('rel', [])
                })
            else:
                external.append({
                    "url": absolute_url,
                    "anchor": link.get_text(strip=True)[:100],
                    "rel": link.get('rel', [])
                })

        # Anchor text analysis for internal links
        anchor_texts = [l["anchor"] for l in internal if l["anchor"]]
        anchor_diversity = len(set(anchor_texts)) / len(anchor_texts) if anchor_texts else 1.0

        return {
            "total": len(links),
            "internal_count": len(internal),
            "external_count": len(external),
            "internal_links": internal[:50],  # Limit output
            "external_links": external[:50],  # Limit output
            "anchor_text_diversity": round(anchor_diversity, 2),
            "unique_anchors": len(set(anchor_texts)),
        }