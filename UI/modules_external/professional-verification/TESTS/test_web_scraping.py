"""
Web Scraping Module Test - Gregory Dutton Case
===============================================

Tests all web scraping and metadata extraction capabilities for ISB & SCA Technology.
"""

import sys
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
load_dotenv(env_path)

# Add module to path
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(module_dir, 'tools', 'implementations'))

from web_scraping_core import (
    scrape_website_content,
    analyze_website_structure,
    extract_ssl_certificate_info,
    check_dns_records,
    search_github_repositories,
    analyze_builtwith_technology,
    check_wayback_availability
)

print("=" * 100)
print("  WEB SCRAPING & METADATA EXTRACTION TEST")
print("=" * 100)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

results = {
    'test_date': datetime.now().isoformat(),
    'isb': {},
    'sca': {}
}

# Test both domains
domains = {
    'isb': 'isb.eco',
    'sca': 'scatechnology.ai'
}

for org, domain in domains.items():
    print(f"\n{'=' * 100}")
    print(f"  TESTING: {domain.upper()} ({'ISB' if org == 'isb' else 'SCA Technology'})")
    print("=" * 100)
    
    # ===== TEST 1: Website Content Scraping =====
    print(f"\n🔍 Scraping website content: {domain}")
    content = scrape_website_content(domain)
    results[org]['content'] = content
    
    if content.get('success'):
        print(f"   ✅ Title: {content.get('title', 'N/A')}")
        print(f"   ✅ Links found: {content.get('links_count', 0)}")
        print(f"   ✅ Images found: {content.get('images_count', 0)}")
        print(f"   ✅ Technologies: {', '.join(content.get('technologies_detected', [])) or 'None detected'}")
        print(f"   ✅ Has HTTPS: {content.get('has_https', False)}")
        
        if content.get('contact_info'):
            emails = content['contact_info'].get('emails', [])
            phones = content['contact_info'].get('phones', [])
            if emails:
                print(f"   ✅ Emails found: {', '.join(emails[:3])}")
            if phones:
                print(f"   ✅ Phones found: {', '.join(phones[:3])}")
        
        if content.get('social_media_links'):
            print(f"   ✅ Social media: {', '.join(content['social_media_links'].keys())}")
    else:
        print(f"   ❌ Failed: {content.get('error')}")
    
    # ===== TEST 2: Website Structure Analysis =====
    print(f"\n🔍 Analyzing website structure: {domain}")
    structure = analyze_website_structure(domain)
    results[org]['structure'] = structure
    
    if structure.get('success'):
        print(f"   ✅ Robots.txt: {'Found' if structure.get('has_robots_txt') else 'Not found'}")
        print(f"   ✅ Sitemap: {'Found' if structure.get('has_sitemap') else 'Not found'}")
        print(f"   ✅ Security score: {structure.get('security_score', 0)}/100")
        print(f"   ✅ Server: {structure.get('server', 'Unknown')}")
        
        common_pages = structure.get('common_pages_found', {})
        if common_pages:
            print(f"   ✅ Common pages: {', '.join(common_pages.keys())}")
    else:
        print(f"   ❌ Failed: {structure.get('error')}")
    
    # ===== TEST 3: SSL Certificate =====
    print(f"\n🔍 Checking SSL certificate: {domain}")
    ssl_info = extract_ssl_certificate_info(domain)
    results[org]['ssl'] = ssl_info
    
    if ssl_info.get('success'):
        print(f"   ✅ Issuer: {ssl_info.get('issuer_organization', 'Unknown')}")
        print(f"   ✅ Valid: {ssl_info.get('is_valid', False)}")
        print(f"   ✅ Days until expiry: {ssl_info.get('days_until_expiry', 0)}")
        print(f"   ✅ Issued: {ssl_info.get('issued_date', 'Unknown')[:10]}")
    else:
        print(f"   ❌ Failed: {ssl_info.get('error')}")
    
    # ===== TEST 4: DNS Records =====
    print(f"\n🔍 Checking DNS records: {domain}")
    dns_info = check_dns_records(domain)
    results[org]['dns'] = dns_info
    
    if dns_info.get('success'):
        records = dns_info.get('records', {})
        print(f"   ✅ IPv4 addresses: {len(records.get('A', []))}")
        print(f"   ✅ IPv6 addresses: {len(records.get('AAAA', []))}")
        print(f"   ✅ Mail servers: {len(records.get('MX', []))}")
        print(f"   ✅ Nameservers: {len(records.get('NS', []))}")
        
        if records.get('A'):
            print(f"   ✅ IP: {records['A'][0]}")
    else:
        print(f"   ⚠️  Note: {dns_info.get('error')}")
        if 'install_command' in dns_info:
            print(f"   ℹ️  Install: {dns_info['install_command']}")
    
    # ===== TEST 5: Technology Stack =====
    print(f"\n🔍 Analyzing technology stack: {domain}")
    tech = analyze_builtwith_technology(domain)
    results[org]['technology'] = tech
    
    if tech.get('success'):
        techs = tech.get('technologies', {})
        total = tech.get('total_technologies_detected', 0)
        print(f"   ✅ Total technologies: {total}")
        
        for category, items in techs.items():
            if items:
                print(f"   ✅ {category}: {', '.join(items)}")
    else:
        print(f"   ❌ Failed: {tech.get('error')}")
    
    # ===== TEST 6: Wayback Machine =====
    print(f"\n🔍 Checking Wayback Machine: {domain}")
    wayback = check_wayback_availability(domain)
    results[org]['wayback'] = wayback
    
    if wayback.get('success'):
        if wayback.get('is_archived'):
            print(f"   ✅ Archived: Yes")
            print(f"   ✅ Latest snapshot: {wayback.get('latest_snapshot_date', 'Unknown')[:10]}")
            print(f"   ✅ Snapshot URL: {wayback.get('latest_snapshot_url', 'N/A')[:80]}...")
        else:
            print(f"   ⚠️  Not archived in Wayback Machine")
    else:
        print(f"   ❌ Failed: {wayback.get('error')}")

# ===== TEST 7: GitHub Search =====
print(f"\n{'=' * 100}")
print("  GITHUB REPOSITORY SEARCH")
print("=" * 100)

github_searches = {
    'isb_org': ('Institute of Sustainable Biodiversity', None),
    'sca_org': ('SCA Technology', None),
    'gregory_dutton': ('Gregory Dutton', None)
}

for search_key, (query, org_name) in github_searches.items():
    print(f"\n🔍 Searching GitHub: {query}")
    github = search_github_repositories(query, org_name)
    results[f'github_{search_key}'] = github
    
    if github.get('success'):
        total = github.get('total_count', 0)
        repos = github.get('repositories', [])
        print(f"   ✅ Total repositories: {total}")
        
        if repos:
            print(f"   ✅ Top repositories:")
            for repo in repos[:5]:
                print(f"      • {repo['full_name']} ({repo.get('stars', 0)} ⭐)")
                if repo.get('description'):
                    print(f"        {repo['description'][:80]}...")
        else:
            print(f"   ⚠️  No repositories found")
    else:
        print(f"   ❌ Failed: {github.get('error')}")

# ===== SUMMARY =====
print(f"\n{'=' * 100}")
print("  COMPARISON SUMMARY")
print("=" * 100)

print("\n📊 ISB.ECO vs SCATECHNOLOGY.AI:\n")

comparison = {
    'Website accessible': [
        results['isb'].get('content', {}).get('success', False),
        results['sca'].get('content', {}).get('success', False)
    ],
    'HTTPS enabled': [
        results['isb'].get('content', {}).get('has_https', False),
        results['sca'].get('content', {}).get('has_https', False)
    ],
    'Valid SSL certificate': [
        results['isb'].get('ssl', {}).get('is_valid', False),
        results['sca'].get('ssl', {}).get('is_valid', False)
    ],
    'Has sitemap.xml': [
        results['isb'].get('structure', {}).get('has_sitemap', False),
        results['sca'].get('structure', {}).get('has_sitemap', False)
    ],
    'Security score': [
        f"{results['isb'].get('structure', {}).get('security_score', 0)}/100",
        f"{results['sca'].get('structure', {}).get('security_score', 0)}/100"
    ],
    'Wayback archived': [
        results['isb'].get('wayback', {}).get('is_archived', False),
        results['sca'].get('wayback', {}).get('is_archived', False)
    ],
    'Technologies detected': [
        results['isb'].get('technology', {}).get('total_technologies_detected', 0),
        results['sca'].get('technology', {}).get('total_technologies_detected', 0)
    ]
}

for metric, values in comparison.items():
    isb_val, sca_val = values
    print(f"   {metric:25} | ISB: {str(isb_val):15} | SCA: {str(sca_val):15}")

# Save results
output_file = os.path.join(current_dir, 'web_scraping_test_results.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n{'=' * 100}")
print(f"💾 Full results saved to: {output_file}")
print("=" * 100)

print(f"\n{'=' * 100}")
print("  KEY FINDINGS")
print("=" * 100)

print("""
✅ WHAT THIS REVEALS:

1. WEBSITE LEGITIMACY:
   - ISB (809 days old): Should have established web presence
   - SCA (168 days old): Too new to have extensive content

2. TECHNICAL INFRASTRUCTURE:
   - SSL certificates verify domain ownership
   - Security headers indicate professional setup
   - Technology stack reveals CMS/framework choices

3. CONTACT INFORMATION:
   - Emails, phone numbers extracted from pages
   - Social media links verify cross-platform presence
   - Staff/team pages confirm organizational structure

4. HISTORICAL PRESENCE:
   - Wayback Machine shows when site went live
   - GitHub repos verify technical work
   - Technology stack evolution over time

5. RED FLAGS TO CHECK:
   ✗ No SSL certificate → Unprofessional/insecure
   ✗ No contact information → Suspicious
   ✗ No social media links → Lack of presence
   ✗ No Wayback history → Recently created
   ✗ No sitemap/robots.txt → Poor SEO/unprofessional
   ✗ Security score < 40 → Vulnerable to attacks
""")

print("=" * 100)
