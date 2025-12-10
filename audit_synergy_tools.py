#!/usr/bin/env python3
"""
Audit Synergy Tools - Find mismatches between schema, implementation, and UI
"""

import json
import re
import os

# Load schema
with open('tools/schemas/synergy_tools.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Load implementation
with open('tools/implementations/synergy.py', 'r', encoding='utf-8') as f:
    impl_code = f.read()

# Extract function definitions from implementation
impl_functions = set(re.findall(r'^def (synergy_\w+)\(', impl_code, re.MULTILINE))

# Extract tool names from schema
schema_tools = {tool['name'] for tool in schema['tools']}

print("=" * 80)
print("SYNERGY TOOL SUITE AUDIT")
print("=" * 80)

print(f"\n📊 SUMMARY:")
print(f"   Schema Tools: {len(schema_tools)}")
print(f"   Implementation Functions: {len(impl_functions)}")

# Find missing implementations
missing_impl = schema_tools - impl_functions
if missing_impl:
    print(f"\n❌ MISSING IMPLEMENTATIONS ({len(missing_impl)}):")
    for tool in sorted(missing_impl):
        print(f"   - {tool}")
else:
    print(f"\n✅ All schema tools have implementations")

# Find extra implementations (not in schema)
extra_impl = impl_functions - schema_tools
if extra_impl:
    print(f"\n⚠️  EXTRA IMPLEMENTATIONS ({len(extra_impl)}):")
    for func in sorted(extra_impl):
        print(f"   - {func}")

# Check UI capabilities that need tools
print(f"\n\n🎯 CRITICAL UI CAPABILITIES CHECK:")
print(f"=" * 80)

ui_capabilities = {
    "Milestone Management": [
        ("synergy_create_milestone", "CREATE milestone"),
        ("synergy_update_milestone", "UPDATE milestone fields"),
        ("synergy_delete_milestone", "DELETE milestone"),
        ("synergy_get_milestones", "LIST milestones"),
        ("synergy_set_milestone_blocker", "BLOCK/UNBLOCK milestone"),
        ("synergy_add_milestone_document", "ADD document to milestone"),
        ("synergy_add_milestone_link", "ADD link to milestone"),
    ],
    "Task Management": [
        ("synergy_create_task", "CREATE task in milestone"),
        ("synergy_update_task", "UPDATE task fields"),
        ("synergy_delete_task", "DELETE task"),
        ("synergy_update_task_field", "UPDATE individual task field"),
        ("synergy_set_task_blocker", "BLOCK/UNBLOCK task"),
    ],
    "Subtask Management": [
        ("synergy_create_subtask", "CREATE subtask in task"),
        ("synergy_update_subtask", "UPDATE subtask fields"),
        ("synergy_delete_subtask", "DELETE subtask"),
        ("synergy_update_subtask_field", "UPDATE individual subtask field"),
    ],
    "Document Management": [
        ("synergy_add_document", "ADD document to session"),
        ("synergy_remove_document", "REMOVE document from session"),
        ("synergy_add_milestone_document", "ADD document to milestone"),
        ("synergy_create_internal_doc", "CREATE Synergy internal document"),
        ("synergy_update_internal_doc", "UPDATE Synergy internal document"),
        ("synergy_get_internal_doc", "GET Synergy internal document"),
        ("synergy_export_internal_doc", "EXPORT Synergy internal document"),
    ],
    "Link Management": [
        ("synergy_add_link", "ADD link to session"),
        ("synergy_remove_link", "REMOVE link from session"),
        ("synergy_add_milestone_link", "ADD link to milestone"),
    ],
    "Thread/Agent Integration": [
        ("synergy_link_thread", "LINK AI thread to session"),
        ("synergy_assign_agent", "ASSIGN agent to session"),
    ],
    "Session Management": [
        ("synergy_create_session", "CREATE new session"),
        ("synergy_update_session", "UPDATE session"),
        ("synergy_delete_session", "DELETE session"),
        ("synergy_move_session", "MOVE session between columns"),
        ("synergy_get_session", "GET session details"),
        ("synergy_list_sessions", "LIST all sessions"),
        ("synergy_search_sessions", "SEARCH sessions"),
    ],
}

missing_tools = []
for category, tools in ui_capabilities.items():
    print(f"\n{category}:")
    for tool_name, description in tools:
        status = "✅" if tool_name in impl_functions else "❌"
        in_schema = "📄" if tool_name in schema_tools else "⚠️ "
        print(f"   {status} {in_schema} {tool_name:40s} - {description}")
        if tool_name not in impl_functions or tool_name not in schema_tools:
            missing_tools.append((category, tool_name, description))

# Summary of issues
print(f"\n\n{'=' * 80}")
print(f"🔍 ISSUES FOUND:")
print(f"{'=' * 80}")

if missing_tools:
    print(f"\n❌ MISSING or INCOMPLETE TOOLS ({len(missing_tools)}):")
    for category, tool, desc in missing_tools:
        in_impl = "✅ Impl" if tool in impl_functions else "❌ Impl"
        in_schema = "✅ Schema" if tool in schema_tools else "❌ Schema"
        print(f"\n   {tool}")
        print(f"      Category: {category}")
        print(f"      Purpose: {desc}")
        print(f"      Status: {in_impl} | {in_schema}")
else:
    print(f"\n✅ All critical UI capabilities have tool support!")

# Check for drag-and-drop support
print(f"\n\n🎯 DRAG-AND-DROP SUPPORT:")
print(f"{'=' * 80}")
drag_drop_tools = [
    "synergy_move_session",  # Move between columns
    # Note: Milestone/task/subtask reordering might need additional tools
]
print(f"Session drag-and-drop (between columns):")
if "synergy_move_session" in impl_functions:
    print(f"   ✅ synergy_move_session - EXISTS")
else:
    print(f"   ❌ synergy_move_session - MISSING")

print(f"\nMilestone/Task/Subtask reordering:")
print(f"   ⚠️  May need additional tools for drag-and-drop reordering within lists")
print(f"   Suggestion: Add synergy_reorder_milestones(), synergy_reorder_tasks(), synergy_reorder_subtasks()")

print(f"\n\n{'=' * 80}")
print(f"RECOMMENDATIONS:")
print(f"{'=' * 80}")

recommendations = []

if missing_impl:
    recommendations.append("1. Implement missing functions in synergy.py")

if extra_impl:
    recommendations.append("2. Add schemas for extra implementations OR remove unused code")

if missing_tools:
    recommendations.append("3. Fix missing/incomplete tools to match UI capabilities")

# Check for specific UI features
ui_features_needing_tools = [
    ("Inline editing", "Need update_task_field, update_subtask_field, update_milestone_field"),
    ("Drag-and-drop reordering", "Need reorder_milestones, reorder_tasks, reorder_subtasks"),
    ("Batch operations", "Need batch_update_tasks, batch_create_subtasks"),
]

for feature, need in ui_features_needing_tools:
    recommendations.append(f"4. {feature}: {need}")

if recommendations:
    for rec in recommendations:
        print(f"\n{rec}")
else:
    print(f"\n✅ No critical issues found!")

print(f"\n{'=' * 80}\n")
