"""
Direct database query to check what backend SQL actually returns
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Exact query from automation_routes.py lines 638-660
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
print(f'EXACT BACKEND SQL QUERY RESULT')
print(f'{"="*70}')
print(f'Query returned: {len(rows)} rows\n')

print('FIRST 10 WORKFLOWS:')
for i, row in enumerate(rows[:10], 1):
    auto_id = row['automation_id'][:40] if row['automation_id'] else 'N/A'
    slug = row['slug'][:30] if row['slug'] else 'N/A'
    title = row['title'][:50] if row['title'] else 'Untitled'
    status = row['status'] or 'NULL'
    updated = str(row['updated_at'])[:19] if row['updated_at'] else 'N/A'
    
    print(f'{i:2}. {title:50} | {status:10} | {updated}')

# Check if there's a WHERE clause issue
cursor.execute("SELECT COUNT(*) FROM visual_automations WHERE user_id = 1")
total = cursor.fetchone()[0]

print(f'\n{"="*70}')
print(f'DATABASE TOTALS:')
print(f'{"="*70}')
print(f'Total workflows for user_id=1: {total}')
print(f'Workflows returned by API query: {len(rows)}')

if total != len(rows):
    print(f'\n⚠️  DISCREPANCY: Database has {total} but query returns {len(rows)}!')
    print('Checking for NULL or problematic values...')
    
    cursor.execute("""
        SELECT automation_id, title, 
               CASE WHEN ui_json IS NULL THEN 'NULL' ELSE 'HAS_DATA' END as ui_json_status,
               CASE WHEN execution_json IS NULL THEN 'NULL' ELSE 'HAS_DATA' END as exec_json_status
        FROM visual_automations
        WHERE user_id = 1 AND (ui_json IS NULL OR execution_json IS NULL)
    """)
    null_rows = cursor.fetchall()
    
    if null_rows:
        print(f'\nFound {len(null_rows)} workflows with NULL JSON fields:')
        for row in null_rows:
            print(f'  - {row[1][:50]} | ui_json: {row[2]} | execution_json: {row[3]}')

conn.close()

print(f'\n{"="*70}')
print('CONCLUSION:')
print(f'{"="*70}')
print(f"""
Console shows API returned: count: 3
Database query shows: {len(rows)} workflows match the WHERE clause

If these numbers DON'T match, there's a backend filtering/error issue.
If these numbers MATCH but are less than {total}, the query has a problem.
""")
