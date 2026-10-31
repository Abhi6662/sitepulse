# sitepulse

[![CI](https://github.com/Abhi6662/sitepulse/actions/workflows/ci.yml/badge.svg)](https://github.com/Abhi6662/sitepulse/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Technical SEO audit CLI and library for analyzing live websites.

## Features

- **Meta Tags**: Title, description length validation
- **OpenGraph**: Social media tag coverage
- **JSON-LD Schema**: Structured data detection
- **robots.txt & sitemap.xml**: Crawl configuration audit
- **HTTP Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options

## Installation

```bash
pip install sitepulse
```

## CLI Usage

```bash
# Markdown output (default)
sitepulse https://example.com

# JSON output
sitepulse https://example.com --format json

# Custom timeout
sitepulse https://example.com --timeout 15
```

## Library Usage

```python
from sitepulse import SEOAuditor

auditor = SEOAuditor("https://example.com")
results = auditor.audit()

print(f"Title: {results['meta']['title']}")
print(f"OpenGraph tags: {len(results['opengraph'])}")
print(f"robots.txt exists: {results['robots']['exists']}")
```

## Development

```bash
poetry install
poetry run pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.
