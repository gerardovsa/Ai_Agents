"""
Gregory Dutton Image Verification
==================================

Practical guide for verifying Gregory Dutton's identity using image analysis.
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

from image_verification_core import (
    reverse_image_search_urls,
    search_profile_image_online,
    verify_profile_image_consistency,
    check_facial_recognition_databases
)

print("=" * 100)
print("  🖼️  GREGORY DUTTON - IMAGE VERIFICATION GUIDE")
print("=" * 100)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Subject: Gregory Dutton")
print("Organization Claim: Institute of Sustainable Biodiversity (ISB)")
print("Phone: +61 (0) 461 357 358")
print("Email: greg@isb.eco")
print("=" * 100)

print("""
⚠️  CRITICAL: You need to get Gregory Dutton's actual LinkedIn profile image URL.

HOW TO GET THE IMAGE URL:
1. Go to https://www.linkedin.com/in/gregorydutton (or search for him)
2. Find his profile and open it
3. Right-click on his profile picture
4. Select "Copy image address" or "Copy image link"
5. Paste that URL below in this script or use it with the tools

EXAMPLE URL FORMAT:
https://media.licdn.com/dms/image/v2/ABC123/profile-displayphoto-shrink_200_200/...
""")

# Since we don't have the actual image URL, we'll generate search strategies
results = {}

# ===== STEP 1: SEARCH FOR IMAGES =====
print("\n" + "=" * 100)
print("  STEP 1: SEARCH FOR GREGORY DUTTON'S PHOTOS ONLINE")
print("=" * 100)

print("\n🔍 Generating Google Image searches...")
isb_search = search_profile_image_online('Gregory Dutton', 'Institute of Sustainable Biodiversity')
sca_search = search_profile_image_online('Gregory Dutton', 'SCA Technology')

results['image_searches'] = {
    'isb': isb_search,
    'sca': sca_search
}

print("\n✅ ISB Image Searches:")
for i, url in enumerate(list(isb_search['image_search_urls'].values())[:3], 1):
    print(f"   {i}. {url}")

print("\n✅ SCA Technology Image Searches:")
for i, url in enumerate(list(sca_search['image_search_urls'].values())[:3], 1):
    print(f"   {i}. {url}")

# ===== STEP 2: PROFILE CONSISTENCY CHECK =====
print("\n" + "=" * 100)
print("  STEP 2: CHECK PROFILE IMAGE CONSISTENCY")
print("=" * 100)

print("\n🔍 Generating consistency check instructions...")
consistency = verify_profile_image_consistency(
    'https://www.linkedin.com/in/gregorydutton',
    'https://www.facebook.com/gregory.dutton',
    'https://twitter.com/gregorydutton'
)

results['consistency_check'] = consistency

print("\n✅ Manual Verification Steps:")
for i, step_info in enumerate(consistency['verification_steps'], 1):
    print(f"\n   Platform {i}: {step_info['platform'].upper()}")
    print(f"   URL: {step_info['url']}")
    print(f"   Action: Download profile picture and save as {step_info['platform']}_profile.jpg")

print("\n⚠️  RED FLAGS TO LOOK FOR:")
for flag in consistency['red_flags_to_check']:
    print(f"   ✗ {flag}")

# ===== STEP 3: REVERSE IMAGE SEARCH =====
print("\n" + "=" * 100)
print("  STEP 3: REVERSE IMAGE SEARCH")
print("=" * 100)

print("""
Once you have Gregory Dutton's LinkedIn profile image URL, use this:

from image_verification_core import reverse_image_search_urls

# Replace with actual image URL
image_url = "https://media.licdn.com/dms/image/v2/..."
result = reverse_image_search_urls(image_url)

# Open these URLs in your browser:
for platform, url in result['search_urls'].items():
    print(f"{platform}: {url}")
    
WHAT TO CHECK:
✓ Does the image appear on stock photo sites?
✓ Is the same image used for multiple different people?
✓ Where was the image first seen online?
✓ Does it appear on any suspicious websites?
✓ Is it associated with other organizations?
""")

example_url = "PASTE_GREGORY_DUTTON_IMAGE_URL_HERE"
reverse_urls = reverse_image_search_urls(example_url)
results['reverse_search_template'] = reverse_urls

print("\n✅ Reverse Image Search URLs (use with actual image):")
for platform, url in reverse_urls['search_urls'].items():
    print(f"   {platform.upper()}: {url[:80]}...")

# ===== STEP 4: FACIAL RECOGNITION DATABASES =====
print("\n" + "=" * 100)
print("  STEP 4: PAID FACIAL RECOGNITION SERVICES")
print("=" * 100)

print("\n⚠️  Only use these if FREE searches are inconclusive:\n")

facial_db = check_facial_recognition_databases(example_url)
results['facial_recognition'] = facial_db

for service, info in facial_db['services'].items():
    print(f"   📱 {service.upper()}")
    print(f"      URL: {info['url']}")
    print(f"      Cost: {info['cost']}")
    print(f"      Features: {', '.join(info['features'][:2])}")
    print()

# ===== STEP 5: AI GENERATION DETECTION =====
print("\n" + "=" * 100)
print("  STEP 5: CHECK FOR AI-GENERATED PROFILE PICTURE")
print("=" * 100)

print("""
Visual inspection checklist (zoom to 200% on the image):

🔍 AI-GENERATED FACE RED FLAGS:
   ✗ Perfectly symmetrical face (measure eye positions)
   ✗ Unrealistic skin texture (too smooth, no pores)
   ✗ Warped background near hair edges
   ✗ Misaligned eyes or ears
   ✗ Unnatural hair transitions
   ✗ Floating accessories (glasses, earrings)
   ✗ Inconsistent lighting on face
   ✗ No visible pores or skin details
   ✗ Generic professional background
   ✗ Too-perfect teeth alignment

🔍 EXIF METADATA CHECK:
   Use: extract_image_metadata(image_url)
   
   AI-generated images typically LACK:
   ✗ Camera make/model
   ✗ Original date taken
   ✗ GPS coordinates
   ✗ Photo editing software info
   
   If metadata is missing → HIGH probability AI-generated or screenshot

🔍 ADVANCED TOOLS:
   - Illuminarty.ai: AI image detector (free trial)
   - Hive Moderation: AI-generated content detection
   - Optic.xyz: Deepfake detector
""")

# ===== STEP 6: PRACTICAL WORKFLOW =====
print("\n" + "=" * 100)
print("  🎯 COMPLETE VERIFICATION WORKFLOW")
print("=" * 100)

workflow = {
    'step_1': {
        'action': 'Find LinkedIn Profile',
        'details': [
            'Search LinkedIn for "Gregory Dutton" + "Institute of Sustainable Biodiversity"',
            'Alternative: Search "Gregory Dutton" + "+61 461 357 358"',
            'Check if profile exists and is active',
            'Note: account age, connections, posts, endorsements'
        ]
    },
    'step_2': {
        'action': 'Download Profile Image',
        'details': [
            'Right-click profile picture → "Save image as"',
            'Save as: gregory_dutton_linkedin.jpg',
            'Also save from Facebook/Twitter if found',
            'Compare images side-by-side for consistency'
        ]
    },
    'step_3': {
        'action': 'Reverse Image Search',
        'details': [
            'Go to https://images.google.com',
            'Click camera icon → Upload image',
            'Review all results carefully',
            'Repeat on TinEye.com and Yandex.com/images',
            'Note where else the image appears'
        ]
    },
    'step_4': {
        'action': 'Check for AI Generation',
        'details': [
            'Zoom to 200% on the face',
            'Look for symmetry issues',
            'Check background warping',
            'Upload to Illuminarty.ai for AI detection',
            'Extract EXIF data (check for camera metadata)'
        ]
    },
    'step_5': {
        'action': 'Cross-Reference with Organization',
        'details': [
            'Visit isb.eco website',
            'Look for staff directory or team page',
            'Check if Gregory Dutton is listed',
            'Compare website photo to LinkedIn photo',
            'Verify email format matches organization standard'
        ]
    },
    'step_6': {
        'action': 'Phone Number Verification',
        'details': [
            'Search "+61461357358" on Google',
            'Check TrueCaller app for spam reports',
            'Try searching on WhatsApp',
            'Facebook: Search people by phone number',
            'Note: Australian number format is correct (+61)'
        ]
    }
}

print("\n📋 COMPLETE VERIFICATION CHECKLIST:\n")
for step, info in workflow.items():
    print(f"   {step.upper()}: {info['action']}")
    for detail in info['details']:
        print(f"      • {detail}")
    print()

results['workflow'] = workflow

# ===== DECISION MATRIX =====
print("\n" + "=" * 100)
print("  ⚖️  DECISION MATRIX")
print("=" * 100)

decision_matrix = """
IF image appears on stock photo sites → 🚨 FRAUD (100% confidence)
IF same image used for multiple identities → 🚨 FRAUD (100% confidence)
IF AI-generated indicators present → 🚨 FRAUD (95% confidence)
IF no EXIF camera data + new profile → ⚠️  SUSPICIOUS (70% confidence)
IF different images across platforms → ⚠️  SUSPICIOUS (60% confidence)
IF image only appears on claimed profiles → ✅ LIKELY LEGITIMATE (40% confidence)
IF image appears in verified contexts (news, publications) → ✅ LEGITIMATE (80% confidence)

RECOMMENDATION THRESHOLDS:
- DENY ACCESS: Any fraud indicators OR suspicious + no verification
- REQUEST VERIFICATION: Suspicious indicators only
- APPROVE: Legitimate indicators + domain age > 2 years + verifiable history
"""

print(decision_matrix)

# ===== SAVE RESULTS =====
output_file = os.path.join(current_dir, 'gregory_dutton_image_verification_guide.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 100)
print(f"💾 Complete guide saved to: {output_file}")
print("=" * 100)

print("\n" + "=" * 100)
print("  🚀 NEXT STEPS")
print("=" * 100)

print("""
1. Open LinkedIn and search for Gregory Dutton
2. Copy his profile image URL
3. Run reverse_image_search_urls() with that URL
4. Open all 4 search URLs (Google, TinEye, Yandex, Bing)
5. Review results for red flags
6. If inconclusive, consider PimEyes ($30) for comprehensive search
7. Compare findings with domain age and organization verification
8. Make final access decision based on all evidence

🔴 CURRENT STATUS:
   - ISB domain: 809 days old (2.2 years) ✅
   - SCA domain: 168 days old (5.6 months) ❌
   - GitHub: Not found ❌
   - Social media: Both found ✅
   - Image verification: PENDING (requires your manual check)

🎯 RECOMMENDATION: 
   Complete image verification BEFORE granting any access.
   If ANY fraud indicators found → DENY ACCESS immediately.
""")

print("=" * 100)
