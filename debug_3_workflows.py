"""Debug why only 3 workflows are returned"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Check what status the new workflows have
cursor.execute("""
    SELECT automation_id, title, status, category, created_at
    FROM visual_automations 
    WHERE user_id = 1
    ORDER BY created_at DESC
    LIMIT 10
""")

rows = cursor.fetchall()

print('\n' + '='*70)
print('TOP 10 WORKFLOWS (by creation date)')
print('='*70 + '\n')

for i, row in enumerate(rows, 1):
    is_new = 'wf_' in row['automation_id'] and '1763946900' in row['automation_id']
    marker = '🆕 NEW' if is_new else ''
    print(f"{i}. {row['title']} {marker}")
    print(f"   Status: {row['status']}")
    print(f"   Category: {row['category']}")
    print(f"   Created: {row['created_at']}")
    print(f"   ID: {row['automation_id'][:40]}...")
    print()

# Check status distribution
cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM visual_automations 
    WHERE user_id = 1
    GROUP BY status
    ORDER BY count DESC
""")

status_rows = cursor.fetchall()

print('='*70)
print('STATUS DISTRIBUTION')
print('='*70 + '\n')

for row in status_rows:
    print(f"  {row['status']}: {row['count']} workflows")

print()

# Check if there's a filter by category or status
cursor.execute("""
    SELECT automation_id, title, status
    FROM visual_automations 
    WHERE user_id = 1 AND status != 'draft'
    ORDER BY updated_at DESC
""")

active_rows = cursor.fetchall()

print('='*70)
print(f'NON-DRAFT WORKFLOWS: {len(active_rows)}')
print('='*70 + '\n')

if len(active_rows) == 3:
    print('⚠️  FOUND THE ISSUE! Only 3 workflows are NOT draft status')
    print('   Your 4 new workflows are status="draft"')
    print('   The UI is probably filtering OUT draft workflows!\n')
    for row in active_rows:
        print(f"  - {row['title']} (status: {row['status']})")
else:
    print(f'Found {len(active_rows)} non-draft workflows')

conn.close()
