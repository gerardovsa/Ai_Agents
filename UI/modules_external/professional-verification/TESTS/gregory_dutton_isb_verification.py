"""
Gregory Dutton ISB Verification
================================

CRITICAL DISCREPANCY DETECTED:
- Email claims: Gregory Dutton @ Institute of Sustainable Biodiversity (isb.eco)
- Previous investigation: Greg Dutton @ SCA Technology (scatechnology.ai)

This script verifies:
1. Which organization is legitimate?
2. Is this the same person or an impersonator?
3. Profile image verification methods
4. Alias detection techniques
"""

import sys
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
load_dotenv(env_path)

# Add module to path
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(module_dir, 'tools', 'implementations'))

from verification_core import (
    check_domain_age,
    check_wayback_history,
    verify_github_profile,
    check_data_breach_exposure,
    verify_email_deliverability,
    search_company_social_media
)

print("=" * 100)
print("  🚨 CRITICAL DISCREPANCY INVESTIGATION")
print("=" * 100)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Subject: Gregory Dutton")
print(f"Claimed Organization: Institute of Sustainable Biodiversity (ISB)")
print(f"Previous Claim: SCA Technology")
print("=" * 100)

results = {
    'discrepancy_summary': {
        'claim_1': 'SCA Technology (scatechnology.ai)',
        'claim_2': 'Institute of Sustainable Biodiversity (isb.eco)',
        'red_flag': 'Same person claiming two different organizations'
    },
    'isb_verification': {},
    'sca_comparison': {},
    'identity_analysis': {}
}

# ===== ISB.ECO DOMAIN VERIFICATION =====
print("\n" + "=" * 100)
print("  VERIFYING ISB.ECO DOMAIN")
print("=" * 100)

print("\n🔍 Checking isb.eco domain age...")
isb_domain = check_domain_age('isb.eco')
results['isb_verification']['domain_age'] = isb_domain
print(json.dumps(isb_domain, indent=2, default=str))

if isb_domain.get('success'):
    age_days = isb_domain.get('age_days', 0)
    if age_days < 180:
        print(f"⚠️  RED FLAG: Domain only {age_days} days old (< 6 months)")
    elif age_days < 365:
        print(f"⚠️  CAUTION: Domain only {age_days} days old (< 1 year)")
    else:
        print(f"✅ Domain is {age_days} days old ({age_days/365:.1f} years)")

print("\n🔍 Checking Wayback Machine history for isb.eco...")
isb_history = check_wayback_history('isb.eco', '2020-01-01', '2025-12-18')
results['isb_verification']['wayback_history'] = isb_history
print(json.dumps(isb_history, indent=2))

snapshot_count = isb_history.get('snapshot_count', 0)
if snapshot_count == 0:
    print("🚨 CRITICAL: No Wayback Machine snapshots - no historical web presence")
elif snapshot_count < 5:
    print(f"⚠️  WARNING: Only {snapshot_count} snapshots - limited historical presence")
else:
    print(f"✅ Found {snapshot_count} snapshots - established web presence")

# ===== EMAIL VERIFICATION =====
print("\n" + "=" * 100)
print("  EMAIL VERIFICATION")
print("=" * 100)

print("\n🔍 Verifying greg@isb.eco...")
isb_email = verify_email_deliverability('greg@isb.eco')
results['isb_verification']['email'] = isb_email
print(json.dumps(isb_email, indent=2))

print("\n🔍 Checking data breaches for greg@isb.eco...")
isb_breaches = check_data_breach_exposure('greg@isb.eco')
results['isb_verification']['breaches'] = isb_breaches
print(json.dumps(isb_breaches, indent=2))

# ===== GITHUB VERIFICATION =====
print("\n" + "=" * 100)
print("  GITHUB PROFILE SEARCH")
print("=" * 100)

github_usernames = ['gregorydutton', 'gregory-dutton', 'gregdutton', 'greg-dutton']

for username in github_usernames:
    print(f"\n🔍 Searching for: {username}")
    github_result = verify_github_profile(username)
    results['isb_verification'][f'github_{username}'] = github_result
    print(json.dumps(github_result, indent=2))
    
    if github_result.get('profile_exists'):
        print(f"✅ FOUND: https://github.com/{username}")
        print(f"   Name: {github_result.get('name', 'Not provided')}")
        print(f"   Bio: {github_result.get('bio', 'Not provided')}")
        print(f"   Location: {github_result.get('location', 'Not provided')}")
        print(f"   Public repos: {github_result.get('public_repos', 0)}")
    else:
        print(f"❌ Not found: {username}")

# ===== COMPANY SOCIAL MEDIA =====
print("\n" + "=" * 100)
print("  COMPANY SOCIAL MEDIA VERIFICATION")
print("=" * 100)

print("\n🔍 Searching for ISB social media presence...")
isb_social = search_company_social_media('Institute of Sustainable Biodiversity', 'isb.eco')
results['isb_verification']['social_media'] = isb_social
print(json.dumps(isb_social, indent=2))

# ===== LINKEDIN SEARCH URLS =====
print("\n" + "=" * 100)
print("  LINKEDIN MANUAL SEARCH URLS")
print("=" * 100)

linkedin_urls = [
    "https://www.linkedin.com/in/gregorydutton",
    "https://www.linkedin.com/in/gregory-dutton",
    "https://www.linkedin.com/in/gregdutton",
    "https://www.linkedin.com/in/greg-dutton",
    "https://www.linkedin.com/search/results/all/?keywords=Gregory%20Dutton%20Institute%20Sustainable%20Biodiversity",
    "https://www.linkedin.com/search/results/all/?keywords=Gregory%20Dutton%20ISB",
    "https://www.linkedin.com/search/results/all/?keywords=Gregory%20Dutton%20isb.eco"
]

print("\n🔗 Check these LinkedIn URLs manually:")
for url in linkedin_urls:
    print(f"   {url}")

# ===== IMAGE VERIFICATION METHODS =====
print("\n" + "=" * 100)
print("  IMAGE VERIFICATION TECHNIQUES")
print("=" * 100)

print("""
🖼️  PROFILE IMAGE VERIFICATION METHODS:

1. REVERSE IMAGE SEARCH:
   - Google Images: https://images.google.com (upload profile picture)
   - TinEye: https://tineye.com (specialized reverse image search)
   - Yandex Images: https://yandex.com/images (often better for faces)
   
2. AI-GENERATED FACE DETECTION:
   - thispersondoesnotexist.com patterns (check for artifacts)
   - Eyes not aligned perfectly
   - Unnatural hair transitions
   - Warped backgrounds near face edges
   - Too perfect symmetry
   
3. SOCIAL MEDIA CROSS-REFERENCE:
   - Download profile picture from LinkedIn
   - Search on Google Images
   - Check if same face appears on multiple unrelated profiles
   - Look for stock photography watermarks
   
4. EXIF DATA ANALYSIS:
   - Download original image (if possible)
   - Check EXIF metadata for creation date
   - Check camera model (AI images often lack camera data)
   - GPS coordinates (if present)
   
5. FACIAL RECOGNITION (Advanced):
   - PimEyes: https://pimeyes.com (face search engine)
   - FaceCheck.ID: https://facecheck.id
   - Note: These may require payment or have privacy concerns

🚨 RED FLAGS FOR FAKE PROFILES:
   - Generic stock photo appearance
   - Image appears on multiple unrelated profiles
   - AI-generated artifacts (unnatural features)
   - Very recent account with professional headshot
   - No other photos of the same person
   - Profile picture doesn't match description (age, ethnicity, etc.)
""")

results['identity_analysis']['image_verification_methods'] = {
    'reverse_image_search': ['Google Images', 'TinEye', 'Yandex Images'],
    'ai_detection': 'Check for AI-generated face artifacts',
    'exif_analysis': 'Metadata verification',
    'facial_recognition': ['PimEyes', 'FaceCheck.ID']
}

# ===== ALIAS DETECTION TECHNIQUES =====
print("\n" + "=" * 100)
print("  ALIAS / IDENTITY FRAUD DETECTION")
print("=" * 100)

print("""
🕵️  ALIAS DETECTION TECHNIQUES:

1. EMAIL PATTERN ANALYSIS:
   ✓ greg@scatechnology.ai (SCA Technology claim)
   ✓ greg@isb.eco (ISB claim)
   → Same first name "greg" suggests possible alias or impersonation
   
2. PHONE NUMBER VERIFICATION:
   - Cell: +61 (0) 461 357 358 (Australian number)
   - Search this number on:
     * Google
     * TrueCaller (phone number lookup)
     * WhatsApp (check if profile exists)
     * Facebook (search by phone number)
   
3. CROSS-ORGANIZATION VERIFICATION:
   - Does ISB have a staff directory?
   - Check isb.eco/about or isb.eco/team
   - Search "Gregory Dutton Institute Sustainable Biodiversity" on Google
   - Search "Gregory Dutton ISB" on Google Scholar
   
4. DOMAIN OWNERSHIP COMPARISON:
   - Check WHOIS for both domains
   - Compare registrant information
   - Look for common registration patterns
   
5. LINKEDIN EMPLOYMENT HISTORY:
   - If profile found, check employment timeline
   - Look for overlapping employment at both organizations
   - Check if SCA Technology is even listed
   
6. PUBLICATION SEARCH:
   - Google Scholar: "Gregory Dutton biodiversity"
   - ResearchGate: Search for author profile
   - ORCID: Search for researcher ID
   
7. PROFESSIONAL REGISTRATION:
   - Australian business registries (ABN lookup)
   - Professional associations
   - Academic credentials verification

🚨 CURRENT RED FLAGS:
   ✗ Same person claiming two different organizations
   ✗ Both domains recently registered (if ISB is also new)
   ✗ Requested access to competitor's systems (if genuine)
   ✗ No GitHub presence for either organization claim
   ✗ Inconsistent identity presentation
""")

results['identity_analysis']['alias_detection'] = {
    'phone_number': '+61 (0) 461 357 358',
    'email_patterns': ['greg@scatechnology.ai', 'greg@isb.eco'],
    'search_queries': [
        'Gregory Dutton Institute Sustainable Biodiversity',
        'Gregory Dutton ISB',
        'Gregory Dutton SCA Technology',
        '+61461357358'
    ]
}

# ===== COMPARISON ANALYSIS =====
print("\n" + "=" * 100)
print("  COMPARISON: SCA vs ISB")
print("=" * 100)

comparison = {
    'SCA Technology': {
        'domain': 'scatechnology.ai',
        'domain_age': '168 days (5.6 months)',
        'wayback_snapshots': 0,
        'github_presence': 'Not found',
        'social_media': 'Found (2 platforms)',
        'red_flags': 'Domain too new, no history'
    },
    'ISB': {
        'domain': 'isb.eco',
        'domain_age': isb_domain.get('age_days', 'Unknown'),
        'wayback_snapshots': isb_history.get('snapshot_count', 0),
        'github_presence': 'Checking...',
        'social_media': isb_social.get('total_platforms', 0)
    }
}

results['sca_comparison'] = comparison

print("\n📊 Organization Comparison:")
print(json.dumps(comparison, indent=2, default=str))

# ===== VERDICT =====
print("\n" + "=" * 100)
print("  PRELIMINARY VERDICT")
print("=" * 100)

isb_age = isb_domain.get('age_days', 0)
isb_snapshots = isb_history.get('snapshot_count', 0)

if isb_age < 180 and isb_snapshots == 0:
    verdict = "🚨 EXTREMELY HIGH RISK - Both organizations appear fraudulent"
    risk_level = "CRITICAL"
elif isb_age > 365 and isb_snapshots > 10:
    verdict = "⚠️  MODERATE RISK - ISB may be legitimate, SCA likely fraudulent"
    risk_level = "MEDIUM"
else:
    verdict = "⚠️  HIGH RISK - Insufficient evidence for either organization"
    risk_level = "HIGH"

results['verdict'] = {
    'summary': verdict,
    'risk_level': risk_level,
    'recommendation': 'DO NOT GRANT ACCESS until identity confirmed',
    'next_steps': [
        'Call +61 (0) 461 357 358 to verify identity',
        'Request video call with ID verification',
        'Check ISB staff directory at isb.eco',
        'Reverse image search profile picture',
        'Search phone number on TrueCaller',
        'Verify employment with ISB directly'
    ]
}

print(f"\n{verdict}")
print(f"Risk Level: {risk_level}")
print("\n📋 IMMEDIATE ACTIONS:")
for step in results['verdict']['next_steps']:
    print(f"   • {step}")

# ===== SAVE RESULTS =====
output_file = os.path.join(current_dir, 'gregory_dutton_isb_investigation.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 100)
print(f"💾 Full investigation saved to: {output_file}")
print("=" * 100)
