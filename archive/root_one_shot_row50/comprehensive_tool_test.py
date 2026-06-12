#!/usr/bin/env python3
"""Comprehensive tool testing - verify all tool categories"""
import sys
sys.path.insert(0, 'tools')

from registry_v3 import RegistryV3

r = RegistryV3()

# Group tools by platform/category
categories = {}
for tool_name in r.tools.keys():
    # Extract category prefix
    if '_' in tool_name:
        prefix = tool_name.split('_')[0]
        if prefix not in categories:
            categories[prefix] = []
        categories[prefix].append(tool_name)

# Test each category
print("=" * 80)
print("COMPREHENSIVE TOOL REGISTRY TEST")
print("=" * 80)
print()

total_tools = 0
total_working = 0
total_missing = 0
category_issues = {}

for category in sorted(categories.keys()):
    tools = categories[category]
    working = []
    missing = []
    
    for tool in tools:
        func = r.get_tool_function(tool)
        if func:
            working.append(tool)
        else:
            missing.append(tool)
    
    total_tools += len(tools)
    total_working += len(working)
    total_missing += len(missing)
    
    status = "✅" if len(missing) == 0 else "❌"
    print(f"{status} {category.upper():20s} | Total: {len(tools):4d} | Working: {len(working):4d} | Missing: {len(missing):4d}")
    
    if missing:
        category_issues[category] = missing

print()
print("=" * 80)
print(f"SUMMARY: {total_working}/{total_tools} tools working ({100*total_working/total_tools:.1f}%)")
print("=" * 80)
print()

if category_issues:
    print("⚠️  CATEGORIES WITH MISSING IMPLEMENTATIONS:")
    print()
    for category, missing_tools in category_issues.items():
        print(f"  {category.upper()} ({len(missing_tools)} missing):")
        for tool in missing_tools[:10]:  # Show first 10
            print(f"    - {tool}")
        if len(missing_tools) > 10:
            print(f"    ... and {len(missing_tools) - 10} more")
        print()
else:
    print("🎉 ALL TOOLS HAVE IMPLEMENTATIONS!")
    print()
    print("Top 10 Categories by Tool Count:")
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for i, (cat, tools) in enumerate(sorted_categories, 1):
        print(f"  {i:2d}. {cat:20s} - {len(tools):4d} tools")
