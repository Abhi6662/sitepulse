"""CLI interface."""

import json
import click
from rich.console import Console
from rich.table import Table
from .audit import SEOAuditor


@click.command()
@click.argument('url')
@click.option('--format', type=click.Choice(['json', 'markdown']), default='markdown', help='Output format')
@click.option('--timeout', default=10, help='Request timeout in seconds')
def main(url: str, format: str, timeout: int):
    """Audit a URL for technical SEO issues."""
    console = Console()
    
    with console.status(f"[bold green]Auditing {url}..."):
        auditor = SEOAuditor(url, timeout=timeout)
        results = auditor.audit()
    
    if format == 'json':
        click.echo(json.dumps(results, indent=2))
    else:
        _print_markdown(results, console)


def _print_markdown(results: dict, console: Console):
    """Print results as formatted markdown."""
    console.print(f"\n[bold]SEO Audit: {results['url']}[/bold]\n")
    
    # Meta tags
    meta = results.get('meta', {})
    console.print("[bold cyan]Meta Tags[/bold cyan]")
    console.print(f"Title: {meta.get('title', 'Missing')} ({meta.get('title_length', 0)} chars)")
    console.print(f"Description: {meta.get('description', 'Missing')} ({meta.get('description_length', 0)} chars)\n")
    
    # OpenGraph
    og = results.get('opengraph', {})
    console.print(f"[bold cyan]OpenGraph Tags[/bold cyan]: {len(og)} found\n")
    
    # Schema
    schema = results.get('schema', [])
    console.print(f"[bold cyan]JSON-LD Schema[/bold cyan]: {len(schema)} found\n")
    
    # Robots
    robots = results.get('robots', {})
    console.print(f"[bold cyan]robots.txt[/bold cyan]: {'✓' if robots.get('exists') else '✗'}\n")
    
    # Sitemap
    sitemap = results.get('sitemap', {})
    console.print(f"[bold cyan]sitemap.xml[/bold cyan]: {'✓' if sitemap.get('exists') else '✗'}\n")
    
    # Security headers
    headers = results.get('security_headers', {})
    console.print("[bold cyan]Security Headers[/bold cyan]")
    console.print(f"Strict-Transport-Security: {'✓' if headers.get('strict_transport_security') else '✗'}")
    console.print(f"Content-Security-Policy: {'✓' if headers.get('content_security_policy') else '✗'}")
    console.print(f"X-Frame-Options: {'✓' if headers.get('x_frame_options') else '✗'}")
    console.print(f"X-Content-Type-Options: {'✓' if headers.get('x_content_type_options') else '✗'}")


if __name__ == '__main__':
    main()
