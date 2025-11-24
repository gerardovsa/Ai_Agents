import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

# Connect and query
conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Check visual_automations count
cursor.execute('SELECT COUNT(*) as count FROM visual_automations WHERE user_id = 1')
result = cursor.fetchone()
count = result['count'] if result else 0
print(f'\n=== VISUAL_AUTOMATIONS TABLE (canvas designs) ===')
print(f'Total rows for user_id=1: {count}')

if count > 0:
    cursor.execute('''
        SELECT automation_id, slug, title, status, category, 
               LENGTH(ui_json::text) as ui_json_len,
               LENGTH(execution_json::text) as exec_json_len
        FROM visual_automations 
        WHERE user_id = 1 
        ORDER BY updated_at DESC 
        LIMIT 10
    ''')
    rows = cursor.fetchall()
    print(f'\nFirst 10 workflows:')
    for i, r in enumerate(rows, 1):
        print(f'  {i}. ID={r["automation_id"]}, slug={r["slug"]}')
        print(f'     title="{r["title"]}", status={r["status"]}, category={r["category"]}')
        print(f'     ui_json_len={r["ui_json_len"]}, exec_json_len={r["exec_json_len"]}')
else:
    print('  (table is empty for user_id=1)')

# Check automation_workflows count (production table)
cursor.execute('SELECT COUNT(*) as count FROM automation_workflows WHERE user_id = 1')
result = cursor.fetchone()
count2 = result['count'] if result else 0
print(f'\n=== AUTOMATION_WORKFLOWS TABLE (production/execution) ===')
print(f'Total rows for user_id=1: {count2}')

if count2 > 0:
    cursor.execute('''
        SELECT workflow_id, slug, name, enabled, run_count
        FROM automation_workflows 
        WHERE user_id = 1 
        ORDER BY updated_at DESC 
        LIMIT 5
    ''')
    rows = cursor.fetchall()
    print(f'\nFirst 5 workflows:')
    for i, r in enumerate(rows, 1):
        print(f'  {i}. ID={r["workflow_id"]}, slug={r["slug"]}')
        print(f'     name="{r["name"]}", enabled={r["enabled"]}, run_count={r["run_count"]}')
else:
    print('  (table is empty for user_id=1)')

conn.close()
print('\n=== DIAGNOSIS ===')
if count == 0 and count2 == 0:
    print('ISSUE: Both tables are empty!')
    print('SOLUTION: You need to create workflows first.')
    print('  - Use automation_create_workflow() tool to create workflows')
    print('  - Or import sample workflows from templates')
elif count == 0 and count2 > 0:
    print('ISSUE: Data exists in automation_workflows but NOT in visual_automations!')
    print('SOLUTION: The canvas renders from visual_automations.')
    print('  - Need to migrate/copy workflows from automation_workflows → visual_automations')
    print('  - Or the workflow creation process should write to visual_automations')
elif count > 0:
    print(f'SUCCESS: Found {count} workflows in visual_automations!')
    print('  - These should appear in the canvas')
    print('  - If they don\'t, check transformation logic in automation_routes.py')
