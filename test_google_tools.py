"""Test that Google Workspace tools are visible via meta-tools"""

import sys

# Force reload
for mod in list(sys.modules.keys()):
    if 'registry' in mod or 'meta_tools' in mod:
        del sys.modules[mod]

from tools.implementations.meta_tools import list_available_platforms, list_platform_tools, search_tools

print(f"\n{'='*70}")
print("TEST 1: list_available_platforms() - Check if Google platforms exist")
print(f"{'='*70}")

result = list_available_platforms()
print(f"Success: {result['success']}")
print(f"Total platforms: {result['platform_count']}")
print(f"Total tools: {result['total_tools']}")

# Check for Google platforms
google_platforms = [p for p in result['platforms'] if 'google' in p.lower() or 'gmail' in p.lower()]
print(f"\nGoogle-related platforms found: {len(google_platforms)}")
for p in sorted(google_platforms):
    print(f"  {p}: {result['tool_counts'][p]} tools")

expected_google = ['google_docs', 'google_sheets', 'google_forms', 'google_drive', 
                   'google_calendar', 'google_tasks', 'google_slides', 'google_meet',
                   'google_analytics', 'gmail']
missing = [p for p in expected_google if p not in google_platforms]

if missing:
    print(f"\n  MISSING: {missing}")
else:
    print("\n  All major Google platforms present!")

print(f"\n{'='*70}")
print("TEST 2: list_platform_tools('google') - Check alias resolution")
print(f"{'='*70}")

result2 = list_platform_tools(platform='google')
if result2.get('success'):
    print(f"Success: Found {len(result2.get('tools', []))} tools")
    print(f"Guidance provided: {'guidance' in result2}")
    # Show first 5 tools
    for tool in result2.get('tools', [])[:5]:
        print(f"  - {tool['name']}")
    print(f"  ... and {len(result2.get('tools', [])) - 5} more")
else:
    print(f"FAILED: {result2.get('error')}")

print(f"\n{'='*70}")
print("TEST 3: list_platform_tools('gmail') - Check specific platform")
print(f"{'='*70}")

result3 = list_platform_tools(platform='gmail')
if result3.get('success'):
    print(f"Success: Found {len(result3.get('tools', []))} Gmail tools")
    # Show first 10 tools
    for tool in result3.get('tools', [])[:10]:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")
else:
    print(f"FAILED: {result3.get('error')}")

print(f"\n{'='*70}")
print("TEST 4: search_tools('google sheets') - Check search functionality")
print(f"{'='*70}")

result4 = search_tools(query='google sheets')
if result4.get('success'):
    print(f"Success: Found {result4.get('match_count')} matching tools")
    for tool in result4.get('tools', [])[:5]:
        print(f"  - {tool['name']}")
else:
    print(f"FAILED: {result4.get('error')}")

print(f"\n{'='*70}")
print("TEST 5: Verify platform fields in registry")
print(f"{'='*70}")

from tools.registry_v3 import get_registry
registry = get_registry()

# Check Gmail tools
gmail_tools_sample = [name for name in registry.tools.keys() if name.startswith('gmail_')][:5]
print("Sample Gmail tools platform fields:")
for tool_name in gmail_tools_sample:
    tool = registry.tools[tool_name]
    platform = tool.get('platform', 'NO_PLATFORM')
    print(f"  {tool_name}: platform='{platform}'")

# Check Google Docs tools
gdocs_tools_sample = [name for name in registry.tools.keys() if name.startswith('google_docs_')][:5]
print("\nSample Google Docs tools platform fields:")
for tool_name in gdocs_tools_sample:
    tool = registry.tools[tool_name]
    platform = tool.get('platform', 'NO_PLATFORM')
    print(f"  {tool_name}: platform='{platform}'")

# Check Google Sheets tools
gsheets_tools_sample = [name for name in registry.tools.keys() if name.startswith('google_sheets_')][:5]
print("\nSample Google Sheets tools platform fields:")
for tool_name in gsheets_tools_sample:
    tool = registry.tools[tool_name]
    platform = tool.get('platform', 'NO_PLATFORM')
    print(f"  {tool_name}: platform='{platform}'")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
total_google_tools = sum(result['tool_counts'][p] for p in google_platforms)
print(f"Total Google Workspace tools: {total_google_tools}")
print(f"Google platforms: {len(google_platforms)}")
print(f"Status: {'✅ ALL TESTS PASSED' if not missing and result2.get('success') and result3.get('success') else '❌ SOME TESTS FAILED'}")
print(f"{'='*70}\n")
