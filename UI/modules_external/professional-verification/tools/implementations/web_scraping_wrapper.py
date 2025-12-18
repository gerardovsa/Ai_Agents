"""
Web Scraping Wrapper
=====================

Maps Registry V3 tool calls to web scraping implementations.
"""

from tools.registry_v3 import tool_executor


@tool_executor()
def scrape_website_content(url: str):
    """Scrape and analyze complete website content."""
    from web_scraping_core import scrape_website_content as impl
    return impl(url)


@tool_executor()
def analyze_website_structure(url: str):
    """Analyze website structure including robots.txt, sitemap, security headers."""
    from web_scraping_core import analyze_website_structure as impl
    return impl(url)


@tool_executor()
def extract_ssl_certificate_info(domain: str):
    """Extract SSL certificate information."""
    from web_scraping_core import extract_ssl_certificate_info as impl
    return impl(domain)


@tool_executor()
def check_dns_records(domain: str):
    """Check DNS records (A, AAAA, MX, NS, TXT)."""
    from web_scraping_core import check_dns_records as impl
    return impl(domain)


@tool_executor()
def search_github_repositories(query: str, organization: str = None):
    """Search GitHub for repositories."""
    from web_scraping_core import search_github_repositories as impl
    return impl(query, organization)


@tool_executor()
def analyze_builtwith_technology(url: str):
    """Detect website technologies (analytics, CMS, frameworks, CDN)."""
    from web_scraping_core import analyze_builtwith_technology as impl
    return impl(url)


@tool_executor()
def check_wayback_availability(url: str, year: int = None):
    """Check Wayback Machine availability and get snapshots."""
    from web_scraping_core import check_wayback_availability as impl
    return impl(url, year)
