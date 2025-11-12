"""Test that Microsoft tools are now visible via meta-tools"""

import sys

# Force reload
for mod in list(sys.modules.keys()):
    if 'registry' in mod or 'meta_tools' in mod:
        del sys.modules[mod]

from tools.implementations.meta_tools import list_available_platforms

result = list_available_platforms()

print(f"\n{'='*60}")
print("META-TOOL TEST: list_available_platforms()")
print(f"{'='*60}")
print(f"Success: {result['success']}")
print(f"Total platforms: {result['platform_count']}")
print(f"Total tools: {result['total_tools']}")

# Check for Microsoft
microsoft_platforms = [p for p in result['platforms'] if 'microsoft' in p.lower()]
print(f"\nMicrosoft platforms found: {len(microsoft_platforms)}")
for p in sorted(microsoft_platforms):
    print(f"  {p}: {result['tool_counts'][p]} tools")

expected = ['microsoft_calendar', 'microsoft_excel', 'microsoft_forms', 'microsoft_onedrive', 
            'microsoft_onenote', 'microsoft_outlook', 'microsoft_sharepoint', 'microsoft_teams', 
            'microsoft_todo', 'microsoft_word']
missing = [p for p in expected if p not in microsoft_platforms]

if missing:
    print(f"\n  MISSING: {missing}")
    print("  FIX FAILED")
else:
    print("\n  ALL Microsoft platforms present!")
    print("  FIX SUCCESSFUL")

print(f"{'='*60}\n")
