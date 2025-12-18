"""
Image Verification Module Test
================================

Tests reverse image search and AI detection capabilities.
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
    reverse_image_search_file,
    detect_ai_generated_face,
    extract_image_metadata,
    verify_profile_image_consistency,
    search_profile_image_online,
    check_facial_recognition_databases,
    analyze_profile_image_quality
)

print("=" * 100)
print("  IMAGE VERIFICATION MODULE TEST")
print("=" * 100)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

results = {
    'test_date': datetime.now().isoformat(),
    'tests': {}
}

# Test data - Use real accessible images
# Using GitHub avatar (publicly accessible)
test_image_url = "https://avatars.githubusercontent.com/u/1?v=4"  # GitHub's first user avatar
test_linkedin = "https://www.linkedin.com/in/gregorydutton"
test_facebook = "https://www.facebook.com/gregory.dutton"

# Alternative test images that are guaranteed to work
test_images = {
    'github_avatar': 'https://avatars.githubusercontent.com/u/1?v=4',
    'httpbin_image': 'https://httpbin.org/image/jpeg',  # Returns a sample JPEG
    'unsplash_sample': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400'  # Sample portrait
}

# ===== TEST 1: Reverse Image Search URLs =====
print("\n" + "=" * 100)
print("  TEST 1: REVERSE IMAGE SEARCH URLs")
print("=" * 100)

print("\n🔍 Generating reverse image search URLs...")
test1 = reverse_image_search_urls(test_image_url)
results['tests']['reverse_search_urls'] = test1
print(json.dumps(test1, indent=2))

if test1.get('success'):
    print("\n✅ Generated search URLs:")
    for platform, url in test1['search_urls'].items():
        print(f"   {platform}: {url[:80]}...")
else:
    print(f"\n❌ Failed: {test1.get('error')}")

# ===== TEST 2: AI-Generated Face Detection =====
print("\n" + "=" * 100)
print("  TEST 2: AI-GENERATED FACE DETECTION")
print("=" * 100)

print("\n🔍 Analyzing image for AI generation indicators...")
# Use a real accessible image
generic_url = test_images['github_avatar']
print(f"   Using: {generic_url}")
test2 = detect_ai_generated_face(generic_url)
results['tests']['ai_detection'] = test2
print(json.dumps(test2, indent=2))

if test2.get('success'):
    print("\n✅ Analysis complete")
    print(f"   Red flags to check: {len(test2.get('red_flags_to_check', []))}")
else:
    print(f"\n❌ Failed: {test2.get('error')}")

# ===== TEST 3: Profile Image Search =====
print("\n" + "=" * 100)
print("  TEST 3: PROFILE IMAGE SEARCH")
print("=" * 100)

print("\n🔍 Generating search queries for Gregory Dutton @ ISB...")
test3 = search_profile_image_online('Gregory Dutton', 'Institute of Sustainable Biodiversity')
results['tests']['profile_search'] = test3
print(json.dumps(test3, indent=2))

if test3.get('success'):
    print("\n✅ Generated search queries:")
    for i, query in enumerate(test3['search_queries'][:3], 1):
        print(f"   {i}. {query}")
else:
    print(f"\n❌ Failed: {test3.get('error')}")

# ===== TEST 4: Profile Consistency Check =====
print("\n" + "=" * 100)
print("  TEST 4: PROFILE IMAGE CONSISTENCY")
print("=" * 100)

print("\n🔍 Checking profile consistency across platforms...")
test4 = verify_profile_image_consistency(test_linkedin, test_facebook)
results['tests']['consistency_check'] = test4
print(json.dumps(test4, indent=2))

if test4.get('success'):
    print("\n✅ Consistency check instructions generated")
    print(f"   Platforms: {', '.join(test4['platforms_checked'])}")
else:
    print(f"\n❌ Failed: {test4.get('error')}")

# ===== TEST 5: Facial Recognition Databases =====
print("\n" + "=" * 100)
print("  TEST 5: FACIAL RECOGNITION DATABASES")
print("=" * 100)

print("\n🔍 Getting facial recognition service information...")
test5 = check_facial_recognition_databases(test_image_url)
results['tests']['facial_recognition'] = test5
print(json.dumps(test5, indent=2))

if test5.get('success'):
    print("\n✅ Service information retrieved")
    print(f"   Available services: {len(test5.get('services', {}))}")
    for service, info in test5.get('services', {}).items():
        print(f"   - {service}: {info['cost']}")
else:
    print(f"\n❌ Failed: {test5.get('error')}")

# ===== TEST 6: Image Quality Analysis =====
print("\n" + "=" * 100)
print("  TEST 6: IMAGE QUALITY ANALYSIS")
print("=" * 100)

print("\n🔍 Analyzing image quality...")
print(f"   Using: {generic_url}")
test6 = analyze_profile_image_quality(generic_url)
results['tests']['quality_analysis'] = test6
print(json.dumps(test6, indent=2))

if test6.get('success'):
    print("\n✅ Quality analysis complete")
    print(f"   Quality score: {test6.get('quality_score', 0)}/100")
    print(f"   Resolution: {test6.get('resolution_category', 'unknown')}")
else:
    print(f"\n❌ Note: {test6.get('error')}")
    if 'install_command' in test6:
        print(f"   Install: {test6['install_command']}")

# ===== TEST 7: EXIF Metadata Extraction =====
print("\n" + "=" * 100)
print("  TEST 7: EXIF METADATA EXTRACTION")
print("=" * 100)

print("\n🔍 Extracting EXIF metadata...")
print(f"   Using: {generic_url}")
test7 = extract_image_metadata(generic_url)
results['tests']['exif_extraction'] = test7
print(json.dumps(test7, indent=2))

if test7.get('success'):
    print("\n✅ EXIF extraction complete")
    print(f"   Has camera data: {test7.get('has_camera_info', False)}")
    print(f"   AI likelihood: {test7.get('ai_generation_likelihood', 'unknown')}")
else:
    print(f"\n❌ Note: {test7.get('error')}")
    if 'install_command' in test7:
        print(f"   Install: {test7['install_command']}")

# ===== SUMMARY =====
print("\n" + "=" * 100)
print("  TEST SUMMARY")
print("=" * 100)

total_tests = len(results['tests'])
passed_tests = sum(1 for test in results['tests'].values() if test.get('success', False))

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {total_tests - passed_tests}")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

print("\n📝 Notes:")
print("   - Some tools require Pillow library: pip install Pillow")
print("   - Reverse image search requires manual browser interaction")
print("   - AI detection provides visual inspection guidelines")
print("   - Facial recognition services are PAID (use only when necessary)")

# Save results
output_file = os.path.join(current_dir, 'image_verification_test_results.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n💾 Results saved to: {output_file}")
print("=" * 100)

print("\n" + "=" * 100)
print("  🎯 PRACTICAL USAGE FOR GREGORY DUTTON CASE")
print("=" * 100)

print("""
To verify Gregory Dutton's profile image:

1. GET PROFILE IMAGE URL:
   - Visit his LinkedIn profile
   - Right-click profile picture → "Copy image address"
   - Use that URL with reverse_image_search_urls()

2. REVERSE IMAGE SEARCH:
   result = reverse_image_search_urls('https://linkedin-image-url')
   # Open each URL in browser and check results

3. CHECK FOR AI GENERATION:
   result = detect_ai_generated_face('https://linkedin-image-url')
   # Follow red flags checklist

4. EXTRACT METADATA:
   result = extract_image_metadata('https://linkedin-image-url')
   # Check if camera data exists (AI images lack this)

5. SEARCH ONLINE:
   result = search_profile_image_online('Gregory Dutton', 'Institute of Sustainable Biodiversity')
   # Open search URLs to find other photos

6. CHECK CONSISTENCY:
   result = verify_profile_image_consistency(
       'https://linkedin.com/in/gregorydutton',
       'https://facebook.com/gregory.dutton'
   )
   # Compare images across platforms

RED FLAGS TO LOOK FOR:
✗ Same image appears on stock photo sites
✗ Image used for multiple different identities
✗ No EXIF camera data (AI generated or screenshot)
✗ Different images across platforms
✗ AI generation artifacts (perfect symmetry, warped backgrounds)
✗ Very recent profile with professional headshot
""")

print("=" * 100)
