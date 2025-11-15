"""Final comprehensive test of both Microsoft and Google tools"""

import sys

# Force reload
for mod in list(sys.modules.keys()):
    if 'registry' in mod or 'meta_tools' in mod:
        del sys.modules[mod]

from tools.implementations.meta_tools import list_available_platforms

result = list_available_platforms()

print(f"\n{'='*80}")
print("FINAL COMPREHENSIVE TEST - ALL PLATFORMS")
print(f"{'='*80}\n")

print(f"Total platforms: {result['platform_count']}")
print(f"Total tools: {result['total_tools']}")

# Microsoft platforms
microsoft_platforms = [p for p in result['platforms'] if 'microsoft' in p.lower()]
print(f"\n{'='*80}")
print(f"MICROSOFT 365 PLATFORMS: {len(microsoft_platforms)}")
print(f"{'='*80}")
for p in sorted(microsoft_platforms):
    print(f"  ✅ {p:<30} {result['tool_counts'][p]:>3} tools")

microsoft_total = sum(result['tool_counts'][p] for p in microsoft_platforms)
print(f"\n  📊 Total Microsoft tools: {microsoft_total}")

expected_microsoft = ['microsoft_calendar', 'microsoft_excel', 'microsoft_forms', 
                      'microsoft_onedrive', 'microsoft_onenote', 'microsoft_outlook',
                      'microsoft_sharepoint', 'microsoft_teams', 'microsoft_todo', 
                      'microsoft_word']
missing_microsoft = [p for p in expected_microsoft if p not in microsoft_platforms]

if missing_microsoft:
    print(f"  ❌ MISSING: {missing_microsoft}")
else:
    print(f"  ✅ All 10 Microsoft platforms present!")

# Google platforms
google_platforms = [p for p in result['platforms'] if 'google' in p.lower() or 'gmail' in p.lower()]
print(f"\n{'='*80}")
print(f"GOOGLE WORKSPACE PLATFORMS: {len(google_platforms)}")
print(f"{'='*80}")
for p in sorted(google_platforms):
    print(f"  ✅ {p:<30} {result['tool_counts'][p]:>3} tools")

google_total = sum(result['tool_counts'][p] for p in google_platforms)
print(f"\n  📊 Total Google tools: {google_total}")

expected_google = ['google_docs', 'google_sheets', 'google_forms', 'google_drive',
                   'google_calendar', 'google_tasks', 'google_slides', 'google_meet',
                   'gmail']
missing_google = [p for p in expected_google if p not in google_platforms]

if missing_google:
    print(f"  ❌ MISSING: {missing_google}")
else:
    print(f"  ✅ All 9 major Google platforms present!")

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"  Microsoft 365: {microsoft_total} tools across {len(microsoft_platforms)} platforms")
print(f"  Google Workspace: {google_total} tools across {len(google_platforms)} platforms")
print(f"  Combined: {microsoft_total + google_total} tools")
print(f"  Other platforms: {result['total_tools'] - microsoft_total - google_total} tools")

if not missing_microsoft and not missing_google:
    print(f"\n  ✅✅✅ ALL TESTS PASSED! ✅✅✅")
else:
    print(f"\n  ❌ TESTS FAILED - Missing platforms")

print(f"{'='*80}\n")
