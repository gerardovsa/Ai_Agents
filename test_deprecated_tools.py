#!/usr/bin/env python3
"""Test the 28 newly fixed deprecated tools"""
import sys
sys.path.insert(0, 'tools')

from registry_v3 import RegistryV3

r = RegistryV3()

test_tools = {
    'automation': [
        'automation_parse_visual_flow',
        'automation_create_refined_version',
        'automation_save',
        'automation_list',
        'automation_load',
        'automation_activate_schedule',
        'automation_deactivate',
        'automation_delete',
        'automation_export_to_canvas'
    ],
    'synergy': [
        'synergy_create_session_complete',
        'synergy_create_synergy_doc',
        'synergy_resolve_reference',
        'synergy_export_synergy_doc',
        'synergy_get_synergy_doc',
        'synergy_update_synergy_doc',
        'synergy_get_dashboard_url'
    ],
    'pinecone': [
        'pinecone_explain_strategies',
        'pinecone_query_namespaces',
        'pinecone_fetch_by_metadata',
        'pinecone_search_summaries',
        'pinecone_get_vector_details',
        'pinecone_search_and_retrieve'
    ],
    'google_calendar': [
        'google_calendar_get_calendar',
        'google_calendar_get_event',
        'google_calendar_quick_add',
        'google_calendar_move_event',
        'google_calendar_add_reminder',
        'google_calendar_get_colors'
    ]
}

print("=" * 80)
print("TESTING DEPRECATED TOOL ALIASES")
print("=" * 80)
print()

total = 0
working = 0

for category, tools in test_tools.items():
    cat_working = 0
    for tool in tools:
        func = r.get_tool_function(tool)
        if func:
            cat_working += 1
            working += 1
        total += 1
    
    status = "✅" if cat_working == len(tools) else "❌"
    print(f"{status} {category.upper():20s} | {cat_working}/{len(tools)} working")

print()
print("=" * 80)
print(f"TOTAL: {working}/{total} tools now have implementations")
print("=" * 80)

if working == total:
    print("\n🎉 ALL DEPRECATED TOOLS FIXED!")
else:
    print(f"\n⚠️  Still missing {total - working} tools")
