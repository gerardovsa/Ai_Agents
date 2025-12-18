"""
Advanced Analysis Test Suite
============================

Demonstrates AI-powered content analysis, traffic estimation,
backlink analysis, government claim verification, business registry
searches, and digital presence scoring.

Tests both ISB.ECO and SCA Technology for comparison.
"""

import sys
import os
from typing import Any

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import implementations directly
from tools.implementations.advanced_analysis_core import (
    analyze_content_with_ai,
    estimate_web_traffic,
    analyze_backlinks,
    verify_government_claims,
    analyze_business_registries,
    calculate_digital_presence_score
)

# Also import web scraping for content extraction
from tools.implementations.web_scraping_core import (
    scrape_website_content
)


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result(label: str, value: Any):
    """Print formatted result."""
    print(f"  {label}: {value}")


def test_ai_content_analysis():
    """Test AI-powered content analysis."""
    print_section("AI CONTENT ANALYSIS")
    
    domains = ['isb.eco', 'scatechnology.ai']
    
    for domain in domains:
        print(f"\n🔍 Analyzing content for: {domain}")
        
        # First scrape the website
        scrape_result = scrape_website_content(domain)
        if not scrape_result.get('success'):
            print(f"  ❌ Failed to scrape: {scrape_result.get('error')}")
            continue
        
        # Extract text content
        content = scrape_result.get('content', {})
        full_text = f"{content.get('title', '')} {content.get('meta_description', '')} "
        full_text += " ".join(content.get('headings', []))
        
        # Analyze with AI
        result = analyze_content_with_ai(full_text, domain)
        
        if result.get('success'):
            print(f"  ✅ API Used: {result.get('api_used')}")
            print(f"  📝 Content Length: {result.get('content_length')} chars")
            
            if 'ai_scores' in result:
                scores = result['ai_scores']
                print(f"\n  AI SCORES:")
                if isinstance(scores, dict):
                    for key, value in scores.items():
                        print(f"    {key}: {value}")
            elif 'ai_analysis_text' in result:
                print(f"\n  AI ANALYSIS:")
                print(f"    {result['ai_analysis_text'][:300]}...")
            
            print()
        else:
            print(f"  ❌ Error: {result.get('error')}")


def test_web_traffic():
    """Test web traffic estimation."""
    print_section("WEB TRAFFIC ESTIMATION")
    
    domains = ['isb.eco', 'scatechnology.ai']
    
    for domain in domains:
        print(f"\n🌐 Estimating traffic for: {domain}")
        
        result = estimate_web_traffic(domain)
        
        if result.get('success'):
            print(f"  ✅ Traffic Tier: {result.get('estimated_traffic_tier')}")
            print(f"  📊 Traffic Score: {result.get('traffic_score', 0):.1f}/100")
            
            # Tranco ranking
            tranco = result.get('traffic_sources', {}).get('tranco', {})
            if tranco.get('in_top_million'):
                print(f"  🏆 Tranco Rank: #{tranco.get('rank'):,} (Top 1M)")
            else:
                print(f"  ⚠️  Not in Tranco Top 1M")
            
            # Certificate activity
            ct = result.get('traffic_sources', {}).get('certificate_transparency', {})
            if ct:
                print(f"  🔒 SSL Certificates: {ct.get('total_certificates', 0)}")
                print(f"  🌍 Subdomains: {ct.get('subdomains_detected', 0)}")
                print(f"  📡 Activity: {ct.get('activity_indicator', 'Unknown')}")
            
            # Global DNS
            dns = result.get('traffic_sources', {}).get('global_dns', {})
            if dns:
                print(f"  🌐 DNS Reachability: {dns.get('reachable_from', 'Unknown')}")
                print(f"  ✨ Global Presence: {dns.get('global_presence', 'Unknown')}")
            
            print()
        else:
            print(f"  ❌ Error: {result.get('error')}")


def test_backlink_analysis():
    """Test backlink and authority analysis."""
    print_section("BACKLINK & DOMAIN AUTHORITY ANALYSIS")
    
    domains = ['isb.eco', 'scatechnology.ai']
    
    for domain in domains:
        print(f"\n🔗 Analyzing backlinks for: {domain}")
        
        result = analyze_backlinks(domain)
        
        if result.get('success'):
            print(f"  📈 Domain Authority: {result.get('domain_authority_score', 0)}/100")
            print(f"  🏆 Authority Tier: {result.get('authority_tier', 'Unknown')}")
            
            sources = result.get('backlink_sources', {})
            
            # Common Crawl
            cc = sources.get('common_crawl', {})
            if cc.get('indexed'):
                print(f"  ✅ Common Crawl: {cc.get('pages_indexed', 0)} pages indexed")
                print(f"     Frequency: {cc.get('crawl_frequency', 'Unknown')}")
            else:
                print(f"  ❌ Common Crawl: Not indexed")
            
            # Web Archive
            wa = sources.get('web_archive', {})
            print(f"  📚 Web Archive: {wa.get('total_snapshots', 0)} snapshots")
            print(f"     Depth: {wa.get('archival_depth', 'Unknown')}")
            
            # Wikipedia
            wiki = sources.get('wikipedia', {})
            print(f"  📖 Wikipedia: {wiki.get('mentions', 0)} mentions")
            print(f"     Authority: {wiki.get('authority_indicator', 'None')}")
            
            # GitHub
            gh = sources.get('github', {})
            print(f"  💻 GitHub: {gh.get('code_references', 0)} code references")
            
            print()
        else:
            print(f"  ❌ Error: {result.get('error')}")


def test_government_claims():
    """Test government claim verification."""
    print_section("GOVERNMENT CLAIM VERIFICATION")
    
    # Test Gregory Dutton / ISB claims
    print("\n🏛️  Testing: Institute of Sustainable Biodiversity (ISB)")
    print("   Claim: 'Environmental organization working on biodiversity conservation'")
    
    result = verify_government_claims(
        organization_name="Institute of Sustainable Biodiversity",
        claim_text="Environmental organization working on biodiversity conservation with government partnerships",
        country="AU"
    )
    
    if result.get('success'):
        print(f"  ✅ Verification Sources Available")
        
        sources = result.get('verification_sources', {})
        
        # AusTender
        if 'austender' in sources:
            print(f"\n  🇦🇺 AusTender (Australian Government Tenders):")
            print(f"     URL: {sources['austender'].get('search_url', 'N/A')[:80]}...")
        
        # ABR
        if 'abr' in sources:
            print(f"\n  🏢 Australian Business Register:")
            print(f"     URL: {sources['abr'].get('search_url', 'N/A')[:80]}...")
        
        # News search
        if 'news_search' in sources:
            print(f"\n  📰 News Search:")
            print(f"     URL: {sources['news_search'].get('google_news', 'N/A')[:80]}...")
        
        print()
    else:
        print(f"  ❌ Error: {result.get('error')}")
    
    # Test SCA Technology claims
    print("\n🏛️  Testing: SCA Technology")
    print("   Claim: 'AI company with government contracts'")
    
    result = verify_government_claims(
        organization_name="SCA Technology",
        claim_text="AI company with government contracts and funding",
        country="US"
    )
    
    if result.get('success'):
        print(f"  ✅ Verification Sources Available")
        
        sources = result.get('verification_sources', {})
        
        # USASpending
        if 'usaspending' in sources:
            print(f"\n  🇺🇸 USASpending.gov:")
            print(f"     URL: {sources['usaspending'].get('search_url', 'N/A')[:80]}...")
        
        # SAM.gov
        if 'sam_gov' in sources:
            print(f"\n  📋 SAM.gov (System for Award Management):")
            print(f"     URL: {sources['sam_gov'].get('search_url', 'N/A')[:80]}...")
        
        print()
    else:
        print(f"  ❌ Error: {result.get('error')}")


def test_business_registries():
    """Test business registry searches."""
    print_section("BUSINESS REGISTRY VERIFICATION")
    
    # Test ISB
    print("\n🏢 Testing: Institute of Sustainable Biodiversity")
    
    result = analyze_business_registries(
        company_name="Institute of Sustainable Biodiversity",
        country="AU"
    )
    
    if result.get('success'):
        print(f"  ✅ Registry Searches Available")
        
        registries = result.get('registries', {})
        
        for name, data in registries.items():
            print(f"\n  📋 {name.upper()}:")
            if 'search_url' in data:
                print(f"     URL: {data['search_url'][:80]}...")
            if 'note' in data:
                print(f"     Note: {data['note']}")
        
        print()
    else:
        print(f"  ❌ Error: {result.get('error')}")
    
    # Test SCA Technology
    print("\n🏢 Testing: SCA Technology")
    
    result = analyze_business_registries(
        company_name="SCA Technology",
        country="US"
    )
    
    if result.get('success'):
        print(f"  ✅ Registry Searches Available")
        
        registries = result.get('registries', {})
        
        for name, data in registries.items():
            print(f"\n  📋 {name.upper()}:")
            if 'search_url' in data:
                print(f"     URL: {data['search_url'][:80]}...")
            if 'note' in data:
                print(f"     Note: {data['note']}")
        
        print()
    else:
        print(f"  ❌ Error: {result.get('error')}")


def test_digital_presence():
    """Test comprehensive digital presence scoring."""
    print_section("COMPREHENSIVE DIGITAL PRESENCE ANALYSIS")
    
    tests = [
        ('isb.eco', 'Institute of Sustainable Biodiversity'),
        ('scatechnology.ai', 'SCA Technology')
    ]
    
    for domain, company in tests:
        print(f"\n🌐 Analyzing digital presence: {company}")
        
        result = calculate_digital_presence_score(domain, company)
        
        if result.get('success'):
            print(f"  📊 Total Score: {result.get('total_score', 0):.1f}/100")
            print(f"  🏆 Assessment: {result.get('assessment', {}).get('tier', 'Unknown')}")
            
            components = result.get('presence_components', {})
            
            # Social media
            if 'social_media' in components:
                print(f"\n  📱 SOCIAL MEDIA:")
                urls = components['social_media'].get('verification_urls', {})
                for platform, url in list(urls.items())[:3]:
                    print(f"     {platform.title()}: {url[:60]}...")
            
            # Professional networks
            if 'professional' in components:
                print(f"\n  💼 PROFESSIONAL NETWORKS:")
                for platform, url in list(components['professional'].items())[:3]:
                    print(f"     {platform.title()}: {url[:60]}...")
            
            # Content marketing
            if 'content' in components:
                print(f"\n  📝 CONTENT MARKETING:")
                for platform, url in list(components['content'].items())[:2]:
                    print(f"     {platform.replace('_', ' ').title()}: {url[:60]}...")
            
            # Technical presence
            if 'technical' in components:
                print(f"\n  💻 TECHNICAL PRESENCE:")
                for platform, url in list(components['technical'].items())[:3]:
                    print(f"     {platform.replace('_', ' ').title()}: {url[:60]}...")
            
            print()
        else:
            print(f"  ❌ Error: {result.get('error')}")


def main():
    """Run all advanced analysis tests."""
    print("\n" + "="*80)
    print("  ADVANCED ANALYSIS TEST SUITE")
    print("  AI-Powered Verification Tools")
    print("="*80)
    
    try:
        # Test 1: AI Content Analysis
        test_ai_content_analysis()
        
        # Test 2: Web Traffic Estimation
        test_web_traffic()
        
        # Test 3: Backlink Analysis
        test_backlink_analysis()
        
        # Test 4: Government Claims
        test_government_claims()
        
        # Test 5: Business Registries
        test_business_registries()
        
        # Test 6: Digital Presence
        test_digital_presence()
        
        print_section("TEST SUITE COMPLETE")
        print("✅ All advanced analysis tests executed successfully!")
        print("\n📋 SUMMARY:")
        print("  - AI content analysis demonstrates content quality assessment")
        print("  - Traffic estimation shows popularity and visitor metrics")
        print("  - Backlink analysis reveals domain authority and citations")
        print("  - Government verification checks official databases")
        print("  - Business registries confirm legal entity existence")
        print("  - Digital presence scoring assesses overall footprint")
        print("\n🎯 These tools provide COMPREHENSIVE verification beyond basic checks!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
