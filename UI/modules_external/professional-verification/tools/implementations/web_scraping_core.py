"""
Web Scraping & Metadata Extraction Core Module
===============================================

Comprehensive website analysis using FREE tools and APIs:
- BeautifulSoup for HTML parsing
- Requests for HTTP metadata
- BuiltWith API (free tier) for technology detection
- Wayback Machine API for historical data
- DNS/WHOIS lookups
- SSL certificate analysis
- Social media metadata extraction
- GitHub repository scanning

All tools are FREE with no API keys required (or free tiers).
"""

import logging
import os
import re
import json
import base64
import socket
import ssl
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import whois

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_website_content(
    url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Scrape and analyze website content including structure, metadata, and text (FREE).
    
    Args:
        url: Website URL to scrape
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Complete website structure and content analysis
    """
    logger.info(f"[WEB_SCRAPE] Scraping: {url}")
    
    try:
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # Fetch with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract metadata
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        
        # Extract title
        title = soup.find('title')
        title_text = title.string.strip() if title else None
        
        # Extract headings
        headings = {
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
        }
        
        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            links.append({'url': href, 'text': text})
        
        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            alt = img.get('alt', '')
            if src:
                images.append({'src': src, 'alt': alt})
        
        # Extract scripts (technology detection)
        scripts = []
        for script in soup.find_all('script'):
            src = script.get('src')
            if src:
                scripts.append(src)
        
        # Detect technologies from scripts
        technologies = []
        script_text = ' '.join(scripts)
        tech_patterns = {
            'Google Analytics': r'google-analytics\.com|gtag|ga\.js',
            'jQuery': r'jquery',
            'React': r'react',
            'Vue.js': r'vue\.js',
            'Angular': r'angular',
            'WordPress': r'wp-content|wp-includes',
            'Shopify': r'shopify',
            'Stripe': r'stripe\.com',
            'Facebook Pixel': r'facebook\.net|fbevents',
            'Cloudflare': r'cloudflare',
            'Bootstrap': r'bootstrap'
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, script_text, re.IGNORECASE):
                technologies.append(tech)
        
        # Extract body text (limited to first 2000 chars)
        body_text = soup.get_text(separator=' ', strip=True)[:2000]
        
        # Extract contact information
        contact_info = {
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body_text),
            'phones': re.findall(r'\+?\d[\d\s\-\(\)]{8,}\d', body_text)
        }
        
        # Extract social media links
        social_links = {}
        social_patterns = {
            'linkedin': r'linkedin\.com/(?:company|in)/([^/\s\"\']+)',
            'facebook': r'facebook\.com/([^/\s\"\']+)',
            'twitter': r'twitter\.com/([^/\s\"\']+)',
            'instagram': r'instagram\.com/([^/\s\"\']+)',
            'github': r'github\.com/([^/\s\"\']+)'
        }
        
        html_content = str(soup)
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                social_links[platform] = list(set(matches))[:3]  # Limit to 3 unique matches
        
        return {
            'success': True,
            'url': url,
            'final_url': response.url,
            'status_code': response.status_code,
            'title': title_text,
            'meta_tags': meta_tags,
            'headings': headings,
            'links_count': len(links),
            'images_count': len(images),
            'technologies_detected': technologies,
            'contact_info': contact_info,
            'social_media_links': social_links,
            'body_preview': body_text[:500],
            'has_https': response.url.startswith('https://'),
            'content_length': len(response.content),
            'response_time_ms': int(response.elapsed.total_seconds() * 1000),
            'top_links': links[:10],  # First 10 links
            'top_images': images[:5]   # First 5 images
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[WEB_SCRAPE] HTTP Error: {e}")
        return {'success': False, 'error': f'HTTP Error: {str(e)}'}
    except Exception as e:
        logger.error(f"[WEB_SCRAPE] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_website_structure(
    url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze website structure including sitemap, robots.txt, security headers (FREE).
    
    Args:
        url: Website URL to analyze
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Website structure analysis
    """
    logger.info(f"[WEB_STRUCTURE] Analyzing: {url}")
    
    try:
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; SEO-Bot/1.0)'}
        
        # Check robots.txt
        robots_url = f"{base_url}/robots.txt"
        robots_txt = None
        try:
            robots_response = requests.get(robots_url, headers=headers, timeout=10)
            if robots_response.status_code == 200:
                robots_txt = robots_response.text[:1000]  # First 1000 chars
        except:
            pass
        
        # Check sitemap.xml
        sitemap_url = f"{base_url}/sitemap.xml"
        has_sitemap = False
        sitemap_urls = []
        try:
            sitemap_response = requests.get(sitemap_url, headers=headers, timeout=10)
            if sitemap_response.status_code == 200:
                has_sitemap = True
                # Parse sitemap
                soup = BeautifulSoup(sitemap_response.content, 'xml')
                urls = soup.find_all('url')
                sitemap_urls = [url.find('loc').text for url in urls[:10]]  # First 10 URLs
        except:
            pass
        
        # Check common pages
        common_pages = {}
        pages_to_check = {
            'about': ['/about', '/about-us', '/about.html'],
            'contact': ['/contact', '/contact-us', '/contact.html'],
            'team': ['/team', '/our-team', '/team.html'],
            'privacy': ['/privacy', '/privacy-policy', '/privacy.html'],
            'terms': ['/terms', '/terms-of-service', '/tos.html']
        }
        
        for page_type, paths in pages_to_check.items():
            for path in paths:
                try:
                    page_url = base_url + path
                    page_response = requests.head(page_url, headers=headers, timeout=5, allow_redirects=True)
                    if page_response.status_code == 200:
                        common_pages[page_type] = page_url
                        break
                except:
                    continue
        
        # Get main page for header analysis
        main_response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        # Analyze security headers
        security_headers = {
            'Strict-Transport-Security': main_response.headers.get('Strict-Transport-Security'),
            'Content-Security-Policy': main_response.headers.get('Content-Security-Policy'),
            'X-Frame-Options': main_response.headers.get('X-Frame-Options'),
            'X-Content-Type-Options': main_response.headers.get('X-Content-Type-Options'),
            'X-XSS-Protection': main_response.headers.get('X-XSS-Protection')
        }
        
        # Calculate security score
        security_score = sum(1 for v in security_headers.values() if v) * 20
        
        return {
            'success': True,
            'url': url,
            'base_url': base_url,
            'has_robots_txt': robots_txt is not None,
            'robots_txt_preview': robots_txt,
            'has_sitemap': has_sitemap,
            'sitemap_urls_sample': sitemap_urls,
            'common_pages_found': common_pages,
            'security_headers': security_headers,
            'security_score': security_score,
            'server': main_response.headers.get('Server'),
            'powered_by': main_response.headers.get('X-Powered-By'),
            'content_type': main_response.headers.get('Content-Type')
        }
        
    except Exception as e:
        logger.error(f"[WEB_STRUCTURE] Error: {e}")
        return {'success': False, 'error': str(e)}


def extract_ssl_certificate_info(
    domain: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Extract SSL certificate information for security analysis (FREE).
    
    Args:
        domain: Domain name (without http://)
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        SSL certificate details
    """
    logger.info(f"[SSL_CERT] Checking: {domain}")
    
    try:
        # Remove protocol if present
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        
        # Parse certificate
        subject = dict(x[0] for x in cert['subject'])
        issuer = dict(x[0] for x in cert['issuer'])
        
        # Parse dates
        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        
        days_until_expiry = (not_after - datetime.now()).days
        
        # Check validity
        is_valid = datetime.now() > not_before and datetime.now() < not_after
        
        return {
            'success': True,
            'domain': domain,
            'subject': subject,
            'issuer': issuer,
            'issued_date': not_before.isoformat(),
            'expiry_date': not_after.isoformat(),
            'days_until_expiry': days_until_expiry,
            'is_valid': is_valid,
            'version': cert.get('version'),
            'serial_number': cert.get('serialNumber'),
            'subject_alt_names': cert.get('subjectAltName', []),
            'issuer_organization': issuer.get('organizationName', 'Unknown')
        }
        
    except Exception as e:
        logger.error(f"[SSL_CERT] Error: {e}")
        return {'success': False, 'error': str(e)}


def check_dns_records(
    domain: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Check DNS records for domain verification (FREE).
    
    Args:
        domain: Domain name
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        DNS record information
    """
    logger.info(f"[DNS_CHECK] Checking: {domain}")
    
    try:
        import dns.resolver
        
        # Remove protocol if present
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        
        records = {}
        
        # Check A record (IPv4)
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            records['A'] = [str(r) for r in a_records]
        except:
            records['A'] = []
        
        # Check AAAA record (IPv6)
        try:
            aaaa_records = dns.resolver.resolve(domain, 'AAAA')
            records['AAAA'] = [str(r) for r in aaaa_records]
        except:
            records['AAAA'] = []
        
        # Check MX records (mail)
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            records['MX'] = [f"{r.preference} {r.exchange}" for r in mx_records]
        except:
            records['MX'] = []
        
        # Check NS records (nameservers)
        try:
            ns_records = dns.resolver.resolve(domain, 'NS')
            records['NS'] = [str(r) for r in ns_records]
        except:
            records['NS'] = []
        
        # Check TXT records (SPF, DMARC, verification)
        try:
            txt_records = dns.resolver.resolve(domain, 'TXT')
            records['TXT'] = [str(r) for r in txt_records]
        except:
            records['TXT'] = []
        
        return {
            'success': True,
            'domain': domain,
            'records': records,
            'has_ipv4': len(records['A']) > 0,
            'has_ipv6': len(records['AAAA']) > 0,
            'has_mail': len(records['MX']) > 0,
            'nameserver_count': len(records['NS'])
        }
        
    except ImportError:
        return {
            'success': False,
            'error': 'dnspython library required',
            'install_command': 'pip install dnspython'
        }
    except Exception as e:
        logger.error(f"[DNS_CHECK] Error: {e}")
        return {'success': False, 'error': str(e)}


def search_github_repositories(
    query: str,
    organization: Optional[str] = None,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Search GitHub for repositories related to person/company (FREE API).
    
    Args:
        query: Search query (person name, company name)
        organization: GitHub organization name (optional)
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        GitHub repository search results
    """
    logger.info(f"[GITHUB_SEARCH] Searching: {query}")
    
    try:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        # Check for GitHub token
        github_token = os.environ.get('GITHUB_TOKEN')
        if _injected_credentials:
            github_token = _injected_credentials.get('github_token', github_token)
        
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        # Search repositories
        if organization:
            # Search organization repos
            api_url = f'https://api.github.com/orgs/{organization}/repos'
        else:
            # General search
            api_url = f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc'
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return {
                'success': True,
                'query': query,
                'organization': organization,
                'repositories': [],
                'total_count': 0,
                'message': 'No repositories found'
            }
        
        response.raise_for_status()
        data = response.json()
        
        # Parse results
        if organization:
            repos = data
            total_count = len(repos)
        else:
            repos = data.get('items', [])
            total_count = data.get('total_count', 0)
        
        # Extract key info
        repository_list = []
        for repo in repos[:10]:  # Limit to 10
            repository_list.append({
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description'),
                'url': repo['html_url'],
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language'),
                'created_at': repo.get('created_at'),
                'updated_at': repo.get('updated_at'),
                'topics': repo.get('topics', [])
            })
        
        return {
            'success': True,
            'query': query,
            'organization': organization,
            'total_count': total_count,
            'repositories': repository_list,
            'has_results': total_count > 0
        }
        
    except Exception as e:
        logger.error(f"[GITHUB_SEARCH] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_builtwith_technology(
    url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze website technologies using BuiltWith-style detection (FREE).
    
    Args:
        url: Website URL
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Technology stack analysis
    """
    logger.info(f"[BUILTWITH] Analyzing: {url}")
    
    try:
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        html_content = str(soup).lower()
        header_text = str(response.headers).lower()
        
        technologies = {
            'analytics': [],
            'advertising': [],
            'cms': [],
            'javascript_frameworks': [],
            'css_frameworks': [],
            'web_servers': [],
            'cdn': [],
            'payment': [],
            'email': []
        }
        
        # Analytics
        if 'google-analytics' in html_content or 'gtag' in html_content:
            technologies['analytics'].append('Google Analytics')
        if 'matomo' in html_content:
            technologies['analytics'].append('Matomo')
        if 'plausible' in html_content:
            technologies['analytics'].append('Plausible')
        
        # Advertising
        if 'google-adsense' in html_content:
            technologies['advertising'].append('Google AdSense')
        if 'facebook.net' in html_content or 'fbevents' in html_content:
            technologies['advertising'].append('Facebook Pixel')
        
        # CMS
        if 'wp-content' in html_content or 'wordpress' in html_content:
            technologies['cms'].append('WordPress')
        if 'shopify' in html_content:
            technologies['cms'].append('Shopify')
        if 'wix.com' in html_content:
            technologies['cms'].append('Wix')
        if 'squarespace' in html_content:
            technologies['cms'].append('Squarespace')
        
        # JavaScript Frameworks
        if 'react' in html_content:
            technologies['javascript_frameworks'].append('React')
        if 'vue.js' in html_content or 'vue.min.js' in html_content:
            technologies['javascript_frameworks'].append('Vue.js')
        if 'angular' in html_content:
            technologies['javascript_frameworks'].append('Angular')
        if 'jquery' in html_content:
            technologies['javascript_frameworks'].append('jQuery')
        
        # CSS Frameworks
        if 'bootstrap' in html_content:
            technologies['css_frameworks'].append('Bootstrap')
        if 'tailwind' in html_content:
            technologies['css_frameworks'].append('Tailwind CSS')
        if 'foundation' in html_content:
            technologies['css_frameworks'].append('Foundation')
        
        # Web Servers
        server = response.headers.get('Server', '')
        if server:
            technologies['web_servers'].append(server)
        
        # CDN
        if 'cloudflare' in header_text or 'cf-ray' in header_text:
            technologies['cdn'].append('Cloudflare')
        if 'fastly' in header_text:
            technologies['cdn'].append('Fastly')
        if 'akamai' in header_text:
            technologies['cdn'].append('Akamai')
        
        # Payment
        if 'stripe' in html_content:
            technologies['payment'].append('Stripe')
        if 'paypal' in html_content:
            technologies['payment'].append('PayPal')
        if 'square' in html_content:
            technologies['payment'].append('Square')
        
        # Email
        if 'mailchimp' in html_content:
            technologies['email'].append('Mailchimp')
        if 'sendgrid' in html_content:
            technologies['email'].append('SendGrid')
        
        # Count total technologies
        total_tech = sum(len(v) for v in technologies.values())
        
        return {
            'success': True,
            'url': url,
            'technologies': technologies,
            'total_technologies_detected': total_tech,
            'technology_summary': {
                'has_analytics': len(technologies['analytics']) > 0,
                'has_cms': len(technologies['cms']) > 0,
                'uses_cdn': len(technologies['cdn']) > 0,
                'has_payment': len(technologies['payment']) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"[BUILTWITH] Error: {e}")
        return {'success': False, 'error': str(e)}


def check_wayback_availability(
    url: str,
    year: Optional[int] = None,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Check Wayback Machine availability and get snapshots (FREE API).
    
    Args:
        url: Website URL
        year: Specific year to check (optional)
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Wayback Machine availability data
    """
    logger.info(f"[WAYBACK_API] Checking: {url}")
    
    try:
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # Wayback Machine availability API
        api_url = f'https://archive.org/wayback/available?url={url}'
        
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        archived_snapshots = data.get('archived_snapshots', {})
        closest = archived_snapshots.get('closest', {})
        
        if closest:
            snapshot_url = closest.get('url')
            snapshot_timestamp = closest.get('timestamp')
            snapshot_date = datetime.strptime(snapshot_timestamp, '%Y%m%d%H%M%S')
            
            return {
                'success': True,
                'url': url,
                'is_archived': True,
                'latest_snapshot_url': snapshot_url,
                'latest_snapshot_date': snapshot_date.isoformat(),
                'snapshot_timestamp': snapshot_timestamp,
                'status_code': closest.get('status')
            }
        else:
            return {
                'success': True,
                'url': url,
                'is_archived': False,
                'message': 'No archived snapshots found'
            }
        
    except Exception as e:
        logger.error(f"[WAYBACK_API] Error: {e}")
        return {'success': False, 'error': str(e)}
