"""
Add debug logging to list_automations endpoint to see why only 3 workflows are returned
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection
import json

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

query = """
    SELECT automation_id, slug, title, description, category, status,
           ui_json, execution_json, is_scheduled, schedule_cron,
           created_at, updated_at, last_executed_at, execution_count
    FROM visual_automations
    WHERE user_id = %s
    ORDER BY updated_at DESC LIMIT %s
"""

cursor.execute(query, (1, 50))
rows = cursor.fetchall()

print(f'\n{"="*70}')
print(f'BACKEND TRANSFORMATION SIMULATION')
print(f'{"="*70}')
print(f'Total rows from SQL: {len(rows)}\n')

automations = []
errors = []

for i, row in enumerate(rows, 1):
    try:
        # Parse JSON fields (same as backend)
        ui_json = json.loads(row['ui_json']) if isinstance(row['ui_json'], str) else row['ui_json']
        execution_json = json.loads(row['execution_json']) if isinstance(row['execution_json'], str) else row['execution_json']
        
        # Check if JSON fields are valid
        if not isinstance(ui_json, dict):
            errors.append(f"Row {i} ({row['title']}): ui_json is not a dict, type={type(ui_json)}")
            continue
        
        if not isinstance(execution_json, dict):
            errors.append(f"Row {i} ({row['title']}): execution_json is not a dict, type={type(execution_json)}")
            continue
        
        # Successfully processed
        automations.append({
            'automation_id': row['automation_id'],
            'title': row['title'],
            'status': row['status']
        })
        
    except Exception as e:
        errors.append(f"Row {i} ({row.get('title', 'UNKNOWN')}): {type(e).__name__}: {str(e)}")

print(f'Successfully transformed: {len(automations)} workflows')
print(f'Errors encountered: {len(errors)}\n')

if errors:
    print('ERRORS:')
    for error in errors[:20]:  # Show first 20
        print(f'  ❌ {error}')

if automations:
    print(f'\nSUCCESSFULLY TRANSFORMED WORKFLOWS:')
    for auto in automations[:10]:
        print(f'  ✅ {auto["title"][:60]} | {auto["status"]} | {auto["automation_id"][:30]}...')

conn.close()

print(f'\n{"="*70}')
print(f'CONCLUSION:')
print(f'{"="*70}')
print(f'SQL returns: {len(rows)} rows')
print(f'Transformation succeeds: {len(automations)} workflows')
print(f'Transformation fails: {len(errors)} workflows')
print(f'API response should have count: {len(automations)}')
print(f'Console shows API response count: 3')
print(f'\n⚠️  If transformation succeeds for all {len(rows)} but API returns 3,')
print('the issue is AFTER transformation (filtering, truncation, or response building)')
