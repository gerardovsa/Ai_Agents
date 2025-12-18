"""
Social Media Search Test for SCA Technology Team
================================================

Searches LinkedIn, Facebook, and other social platforms for:
- Greg Dutton (CEO)
- Casey Dutton (COO)
- SCA Technology company profiles
"""

import sys
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
load_dotenv(env_path)

# Add module to path
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(module_dir, 'tools', 'implementations'))

from verification_core import (
    search_company_social_media,
    verify_email_deliverability,
    check_data_breach_exposure
)

print("=" * 100)
print("  SOCIAL MEDIA & ONLINE PRESENCE SEARCH")
print("=" * 100)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Target: SCA Technology (Greg Dutton, Casey Dutton)")
print("=" * 100)

results = {
    'company': {},
    'greg_dutton': {},
    'casey_dutton': {}
}

# ===== COMPANY SOCIAL MEDIA =====
print("\n" + "=" * 100)
print("  COMPANY SOCIAL MEDIA PRESENCE")
print("=" * 100)

print("\n🔍 Searching for SCA Technology social media...")
company_social = search_company_social_media('SCA Technology', 'scatechnology.ai')
results['company']['social_media'] = company_social
print(json.dumps(company_social, indent=2))

if company_social.get('platforms_found'):
    print(f"\n✅ Found on {len(company_social['platforms_found'])} platforms:")
    for platform in company_social['platforms_found']:
        print(f"   - {platform['platform']}: {platform['url']}")
else:
    print("\n⚠️  No social media presence found for SCA Technology")

# ===== GREG DUTTON - INDIVIDUAL SEARCHES =====
print("\n" + "=" * 100)
print("  GREG DUTTON - INDIVIDUAL VERIFICATION")
print("=" * 100)

# Email verification
print("\n🔍 Verifying email: greg@scatechnology.ai")
greg_email = verify_email_deliverability('greg@scatechnology.ai')
results['greg_dutton']['email'] = greg_email
print(json.dumps(greg_email, indent=2))

# Data breach check (with API key)
print("\n🔍 Checking data breaches: greg@scatechnology.ai")
greg_breaches = check_data_breach_exposure('greg@scatechnology.ai')
results['greg_dutton']['breaches'] = greg_breaches
print(json.dumps(greg_breaches, indent=2))

if greg_breaches.get('success') and greg_breaches.get('exposed'):
    print(f"\n⚠️  FOUND in {greg_breaches['breach_count']} data breaches:")
    for breach in greg_breaches.get('breaches', [])[:5]:
        print(f"   - {breach['name']} ({breach['date']})")
elif greg_breaches.get('success'):
    print("\n✅ Email NOT found in data breaches")
else:
    print(f"\n❌ Breach check failed: {greg_breaches.get('error')}")

# Manual social media links to check
print("\n🔍 Social Media Profile Links to Check:")
greg_profiles = {
    'LinkedIn': [
        'https://www.linkedin.com/in/gregdutton',
        'https://www.linkedin.com/in/gregory-dutton',
        'https://www.linkedin.com/in/greg-dutton',
        'https://www.linkedin.com/search/results/all/?keywords=Greg%20Dutton%20SCA%20Technology'
    ],
    'Facebook': [
        'https://www.facebook.com/greg.dutton',
        'https://www.facebook.com/gregory.dutton',
        'https://www.facebook.com/search/top?q=Greg%20Dutton%20SCA%20Technology'
    ],
    'Twitter/X': [
        'https://twitter.com/gregdutton',
        'https://twitter.com/search?q=Greg%20Dutton%20SCA%20Technology'
    ]
}

for platform, urls in greg_profiles.items():
    print(f"\n   {platform}:")
    for url in urls:
        print(f"      {url}")

# ===== CASEY DUTTON - INDIVIDUAL SEARCHES =====
print("\n" + "=" * 100)
print("  CASEY DUTTON - INDIVIDUAL VERIFICATION")
print("=" * 100)

# Email verification
print("\n🔍 Verifying email: casey@scatechnology.ai")
casey_email = verify_email_deliverability('casey@scatechnology.ai')
results['casey_dutton']['email'] = casey_email
print(json.dumps(casey_email, indent=2))

# Data breach check
print("\n🔍 Checking data breaches: casey@scatechnology.ai")
casey_breaches = check_data_breach_exposure('casey@scatechnology.ai')
results['casey_dutton']['breaches'] = casey_breaches
print(json.dumps(casey_breaches, indent=2))

if casey_breaches.get('success') and casey_breaches.get('exposed'):
    print(f"\n⚠️  FOUND in {casey_breaches['breach_count']} data breaches:")
    for breach in casey_breaches.get('breaches', [])[:5]:
        print(f"   - {breach['name']} ({breach['date']})")
elif casey_breaches.get('success'):
    print("\n✅ Email NOT found in data breaches")
else:
    print(f"\n❌ Breach check failed: {casey_breaches.get('error')}")

# Manual social media links
print("\n🔍 Social Media Profile Links to Check:")
casey_profiles = {
    'LinkedIn': [
        'https://www.linkedin.com/in/caseydutton',
        'https://www.linkedin.com/in/casey-dutton',
        'https://www.linkedin.com/search/results/all/?keywords=Casey%20Dutton%20SCA%20Technology'
    ],
    'Facebook': [
        'https://www.facebook.com/casey.dutton',
        'https://www.facebook.com/search/top?q=Casey%20Dutton%20SCA%20Technology'
    ],
    'Twitter/X': [
        'https://twitter.com/caseydutton',
        'https://twitter.com/search?q=Casey%20Dutton%20SCA%20Technology'
    ]
}

for platform, urls in casey_profiles.items():
    print(f"\n   {platform}:")
    for url in urls:
        print(f"      {url}")

# ===== SUMMARY =====
print("\n" + "=" * 100)
print("  SOCIAL MEDIA SEARCH SUMMARY")
print("=" * 100)

print("\n📊 Company Social Media:")
if results['company']['social_media'].get('platforms_found'):
    print(f"   ✅ Found on {len(results['company']['social_media']['platforms_found'])} platforms")
else:
    print(f"   ❌ No platforms found (Risk: HIGH)")

print("\n📧 Email Verification:")
print(f"   Greg: {'✅ Deliverable' if results['greg_dutton']['email'].get('is_deliverable') else '❌ Not deliverable'}")
print(f"   Casey: {'✅ Deliverable' if results['casey_dutton']['email'].get('is_deliverable') else '❌ Not deliverable'}")

print("\n🔓 Data Breach Exposure:")
if results['greg_dutton']['breaches'].get('success'):
    if results['greg_dutton']['breaches'].get('exposed'):
        print(f"   Greg: ⚠️  EXPOSED ({results['greg_dutton']['breaches']['breach_count']} breaches)")
    else:
        print(f"   Greg: ✅ Clean")
else:
    print(f"   Greg: ❓ Unable to check")

if results['casey_dutton']['breaches'].get('success'):
    if results['casey_dutton']['breaches'].get('exposed'):
        print(f"   Casey: ⚠️  EXPOSED ({results['casey_dutton']['breaches']['breach_count']} breaches)")
    else:
        print(f"   Casey: ✅ Clean")
else:
    print(f"   Casey: ❓ Unable to check")

print("\n" + "=" * 100)
print("  ACTION ITEMS")
print("=" * 100)
print("\n1. ✅ Manually check all LinkedIn URLs listed above")
print("2. ✅ Manually check all Facebook URLs listed above")
print("3. ✅ Manually check all Twitter/X URLs listed above")
print("4. ✅ Google search: 'Greg Dutton SCA Technology'")
print("5. ✅ Google search: 'Casey Dutton SCA Technology'")
print("6. ✅ Google search: 'SCA Technology Colombia'")
print("7. ✅ Check Colombian business registries (Cámara de Comercio)")
print("\n" + "=" * 100)

# Save results
output_file = os.path.join(current_dir, 'social_media_search_results.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n💾 Results saved to: {output_file}")
print("=" * 100)
