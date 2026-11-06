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

    # Twitter Cards
    twitter = results.get('twitter_cards', {})
    console.print("[bold cyan]Twitter Cards[/bold cyan]")
    if twitter.get('error'):
        console.print(f"Error: {twitter['error']}")
    else:
        console.print(f"Present: {'✓' if twitter.get('present') else '✗'}")
        if twitter.get('present'):
            console.print(f"Card Type: {twitter.get('card_type') or 'Not specified'}")
            console.print(f"Valid: {'✓' if twitter.get('valid') else '✗'}")
            if twitter.get('missing_required'):
                console.print(f"Missing Required: {', '.join(twitter['missing_required'])}")
            console.print(f"Tags Found: {len(twitter.get('tags', {}))}")
    console.print()

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
    console.print(f"X-Content-Type-Options: {'✓' if headers.get('x_content_type_options') else '✗'}\n")

    # Viewport
    viewport = results.get('viewport', {})
    console.print("[bold cyan]Viewport[/bold cyan]")
    if viewport.get('error'):
        console.print(f"Error: {viewport['error']}")
    else:
        console.print(f"Present: {'✓' if viewport.get('present') else '✗'}")
        if viewport.get('present'):
            console.print(f"Content: {viewport.get('content')}")
            console.print(f"width=device-width: {'✓' if viewport.get('has_width_device_width') else '✗'}")
            console.print(f"initial-scale: {'✓' if viewport.get('has_initial_scale') else '✗'}")
    console.print()

    # Images
    images = results.get('images', {})
    console.print("[bold cyan]Images[/bold cyan]")
    if images.get('error'):
        console.print(f"Error: {images['error']}")
    else:
        total = images.get('total', 0)
        with_alt = images.get('with_alt', 0)
        coverage = images.get('coverage_percent', 0)
        console.print(f"Total: {total}, With Alt: {with_alt}, Coverage: {coverage}%")
        missing = images.get('missing_details', [])
        if missing:
            console.print(f"Missing alt (first {len(missing)}):")
            for m in missing[:5]:
                console.print(f"  - [{m['index']}] {m['src']}")
    console.print()

    # Meta Robots
    meta_robots = results.get('meta_robots', {})
    console.print("[bold cyan]Meta Robots[/bold cyan]")
    if meta_robots.get('error'):
        console.print(f"Error: {meta_robots['error']}")
    else:
        console.print(f"Present: {'✓' if meta_robots.get('present') else '✗'}")
        if meta_robots.get('present'):
            console.print(f"Content: {meta_robots.get('content')}")
            console.print(f"noindex: {'⚠ YES' if meta_robots.get('noindex') else 'No'}")
            console.print(f"nofollow: {'⚠ YES' if meta_robots.get('nofollow') else 'No'}")
            console.print(f"none: {'⚠ YES' if meta_robots.get('none') else 'No'}")
            if meta_robots.get('directives'):
                console.print(f"Directives: {', '.join(meta_robots['directives'])}")

    # Content Analysis
    content = results.get('content', {})
    console.print("\n[bold cyan]Content Analysis[/bold cyan]")
    if content.get('error'):
        console.print(f"Error: {content['error']}")
    else:
        console.print(f"Word Count: {content.get('word_count', 0)}")
        console.print(f"Reading Time: {content.get('reading_time_minutes', 0)} min")
        console.print(f"Sentences: {content.get('sentence_count', 0)}")
        console.print(f"Avg Words/Sentence: {content.get('avg_words_per_sentence', 0)}")
        console.print(f"Flesch Reading Ease: {content.get('flesch_reading_ease', 'N/A')}")
        console.print(f"Readability Grade: {content.get('readability_grade', 'N/A')}")


if __name__ == '__main__':
    main()