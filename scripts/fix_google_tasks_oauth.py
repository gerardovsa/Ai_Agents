"""
Script to add _user_id and _injected_credentials parameters to all Google Tasks functions
and update their build_tasks_service() calls
"""

import re

# Read the file
with open(r'C:\Users\gpoli\GIT\AI_agents\google_workspace\google_tasks.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Update function signatures - simple pattern
# Replace `def function_name(params):` with `def function_name(params, _user_id=None, _injected_credentials=None):`
replacements = [
    # Simple signatures (no trailing comma)
    (
        r"def google_tasks_create_task_list\(title\):",
        "def google_tasks_create_task_list(title, _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_get_task_list\(task_list_id\):",
        "def google_tasks_get_task_list(task_list_id, _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_delete_task_list\(task_list_id\):",
        "def google_tasks_delete_task_list(task_list_id, _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_list_tasks\(task_list_id='@default', show_completed=False, show_hidden=False\):",
        "def google_tasks_list_tasks(task_list_id='@default', show_completed=False, show_hidden=False, _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_create_task\(title, task_list_id='@default', notes=None, due=None, parent=None\):",
        "def google_tasks_create_task(title, task_list_id='@default', notes=None, due=None, parent=None, _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_complete_task\(task_id, task_list_id='@default'\):",
        "def google_tasks_complete_task(task_id, task_list_id='@default', _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_delete_task\(task_id, task_list_id='@default'\):",
        "def google_tasks_delete_task(task_id, task_list_id='@default', _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_smart_bulk_complete\(task_ids, task_list_id='@default'\):",
        "def google_tasks_smart_bulk_complete(task_ids, task_list_id='@default', _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_smart_organize_by_priority\(task_list_id='@default'\):",
        "def google_tasks_smart_organize_by_priority(task_list_id='@default', _user_id=None, _injected_credentials=None):"
    ),
]

# Multi-line signatures (with trailing parameters)
multiline_replacements = [
    (
        r"def google_tasks_update_task\(task_id, task_list_id='@default', title=None, notes=None, \n                             due=None, status=None\):",
        "def google_tasks_update_task(task_id, task_list_id='@default', title=None, notes=None, \n                             due=None, status=None, _user_id=None, _injected_credentials=None):"
    ),
    (
        r"def google_tasks_smart_create_project\(project_name, tasks_list, task_list_id='@default', \n                                       auto_number=True\):",
        "def google_tasks_smart_create_project(project_name, tasks_list, task_list_id='@default', \n                                       auto_number=True, _user_id=None, _injected_credentials=None):"
    ),
]

# Apply all replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

for pattern, replacement in multiline_replacements:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Pattern 2: Update all build_tasks_service() calls to pass _user_id
# Replace `service = build_tasks_service()` with `service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)`
content = re.sub(
    r'service = build_tasks_service\(\)',
    'service = build_tasks_service(_user_id=_user_id, _injected_credentials=_injected_credentials)',
    content
)

# Write the updated content
with open(r'C:\Users\gpoli\GIT\AI_agents\google_workspace\google_tasks.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated all Google Tasks functions with _user_id parameters")
print("✅ Updated all build_tasks_service() calls to pass _user_id")
print("\nModified functions:")
print("  - google_tasks_create_task_list")
print("  - google_tasks_get_task_list")
print("  - google_tasks_delete_task_list")
print("  - google_tasks_list_tasks")
print("  - google_tasks_create_task")
print("  - google_tasks_update_task")
print("  - google_tasks_complete_task")
print("  - google_tasks_delete_task")
print("  - google_tasks_smart_create_project")
print("  - google_tasks_smart_bulk_complete")
print("  - google_tasks_smart_organize_by_priority")
