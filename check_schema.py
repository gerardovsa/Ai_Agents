"""Check prompt_library table schema"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name='prompt_library' AND table_schema='ai_infrastructure'
    ORDER BY ordinal_position
""")

cols = cur.fetchall()

print("\n=== prompt_library TABLE SCHEMA ===\n")
for col in cols:
    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
    print(f"  {col['column_name']:20s} {col['data_type']:15s} {nullable}")

conn.close()
