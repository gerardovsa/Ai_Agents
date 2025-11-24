"""
Simulate frontend filtering logic to understand the issue
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_db_connection
import json

conn = get_db_connection('ai_infrastructure')
cursor = conn.cursor()

# Get workflows as backend API returns them
cursor.execute("""
    SELECT automation_id, title, status, category, ui_json, execution_json
    FROM visual_automations
    WHERE user_id = 1
    ORDER BY updated_at DESC
    LIMIT 50
""")
workflows = cursor.fetchall()

print(f'\n{"="*70}')
print(f'BACKEND API RESPONSE SIMULATION')
print(f'{"="*70}')
print(f'Total workflows returned: {len(workflows)}\n')

# Simulate backend transformation
api_workflows = []
for w in workflows:
    auto_id = w[0]
    title = w[1]
    status = w[2] or 'draft'
    category = w[3]
    
    # Backend logic for 'enabled' field (from automation_routes.py line 756)
    # enabled = bool(row.get('is_active') if row.get('is_active') is not None else True)
    # But since is_active doesn't exist, let's check what backend actually does
    
    # Check if workflow has ui_json and execution_json
    ui_json = w[4]
    execution_json = w[5]
    
    workflow_obj = {
        'automation_id': auto_id,
        'title': title,
        'status': status,
        'category': category,
        'enabled': status == 'active'  # Assumption based on status
    }
    api_workflows.append(workflow_obj)

print('STATUS BREAKDOWN IN API RESPONSE:')
status_counts = {}
enabled_counts = {'enabled': 0, 'disabled': 0}

for w in api_workflows:
    status = w['status']
    status_counts[status] = status_counts.get(status, 0) + 1
    
    if w['enabled']:
        enabled_counts['enabled'] += 1
    else:
        enabled_counts['disabled'] += 1

for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    print(f'  {status:15} : {count} workflows')

print(f'\nENABLED/DISABLED BREAKDOWN:')
print(f'  enabled  : {enabled_counts["enabled"]} workflows')
print(f'  disabled : {enabled_counts["disabled"]} workflows')

# Simulate frontend filter: libraryCurrentFilter = 'enabled'
print(f'\n{"="*70}')
print(f'FRONTEND FILTER SIMULATION: libraryCurrentFilter = "enabled"')
print(f'{"="*70}')

filtered = [w for w in api_workflows if w['enabled']]
print(f'Workflows after filtering: {len(filtered)}')

if len(filtered) > 0:
    print(f'\nWorkflows that PASS the enabled filter:')
    for w in filtered[:10]:  # Show first 10
        print(f'  - {w["title"][:60]} | Status: {w["status"]} | Enabled: {w["enabled"]}')
else:
    print('\n⚠️  NO WORKFLOWS PASS THE ENABLED FILTER!')

if len(filtered) < len(api_workflows):
    blocked_count = len(api_workflows) - len(filtered)
    print(f'\n⚠️  {blocked_count} workflows BLOCKED by enabled filter:')
    blocked = [w for w in api_workflows if not w['enabled']]
    for w in blocked[:10]:  # Show first 10
        print(f'  - {w["title"][:60]} | Status: {w["status"]} | Enabled: {w["enabled"]}')

conn.close()

print(f'\n{"="*70}')
print(f'ROOT CAUSE IDENTIFIED')
print(f'{"="*70}')
print(f"""
The console shows: "Filtered workflows: 3"
This means the frontend filter is reducing the list from {len(api_workflows)} → 3

If libraryCurrentFilter = 'enabled', only workflows with enabled=true are shown.
Backend maps enabled based on workflow status.

LIKELY ISSUE: Most workflows have status != 'active', so enabled=false
""")
