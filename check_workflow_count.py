"""
Check workflow count and status distribution in database
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_db_connection

conn = get_db_connection('ai_infrastructure')
cursor = conn.cursor()

# Total count
cursor.execute('SELECT COUNT(*) FROM visual_automations WHERE user_id = 1')
total = cursor.fetchone()[0]
print(f'\n{"="*70}')
print(f'TOTAL WORKFLOWS IN DATABASE: {total}')
print(f'{"="*70}')

# Status breakdown
cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM visual_automations
    WHERE user_id = 1
    GROUP BY status
    ORDER BY count DESC
""")
status_rows = cursor.fetchall()

print('\nSTATUS BREAKDOWN:')
for row in status_rows:
    status = row[0] or 'NULL'
    count = row[1]
    print(f'  {status:15} : {count} workflows')

# Top 10 most recent
cursor.execute("""
    SELECT automation_id, title, status, category, updated_at
    FROM visual_automations
    WHERE user_id = 1
    ORDER BY updated_at DESC
    LIMIT 10
""")
workflows = cursor.fetchall()

print('\nTOP 10 MOST RECENT WORKFLOWS:')
for i, w in enumerate(workflows, 1):
    auto_id = w[0][:40] if w[0] else 'N/A'
    title = w[1][:50] if w[1] else 'Untitled'
    status = w[2] or 'NULL'
    category = w[3] or 'N/A'
    updated = str(w[4])[:19] if w[4] else 'N/A'
    print(f'  {i:2}. {title:50} | {status:10} | {category:12} | {updated}')

# Check what backend would return
cursor.execute("""
    SELECT automation_id, title, status
    FROM visual_automations
    WHERE user_id = 1
    ORDER BY updated_at DESC
    LIMIT 50
""")
backend_rows = cursor.fetchall()

print(f'\n{"="*70}')
print(f'WHAT BACKEND API RETURNS (LIMIT 50):')
print(f'{"="*70}')
print(f'Total returned: {len(backend_rows)} workflows')

print('\nSTATUS DISTRIBUTION IN API RESPONSE:')
status_counts = {}
for row in backend_rows:
    status = row[2] or 'NULL'
    status_counts[status] = status_counts.get(status, 0) + 1

for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    print(f'  {status:15} : {count} workflows')

conn.close()

print(f'\n{"="*70}')
print('ANALYSIS COMPLETE')
print(f'{"="*70}\n')
