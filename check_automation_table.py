"""Check automation_workflows table details"""
import os
import sys

os.environ['USE_SUPABASE'] = 'true'
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Get column details
cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'automation_workflows' 
    ORDER BY ordinal_position
""")

cols = cursor.fetchall()

print('\n=== AUTOMATION_WORKFLOWS TABLE STRUCTURE ===\n')
print('  Columns:')
for col in cols:
    print(f"    {col['column_name']:25} {col['data_type']:20} NULL={col['is_nullable']}")

# Get row count
cursor.execute("SELECT COUNT(*) as count FROM automation_workflows")
count = cursor.fetchone()['count']
print(f'\n  Total records: {count}')

# Get sample records
if count > 0:
    cursor.execute("""
        SELECT workflow_id, name, slug, enabled, created_at 
        FROM automation_workflows 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print('\n  Sample records:')
    for row in rows:
        print(f"    - {row['name']}")
        print(f"      Slug: {row['slug']}")
        print(f"      Enabled: {row['enabled']}")
        print(f"      Created: {row['created_at']}")
        print()

conn.close()
print('=== COMPLETE ===\n')
