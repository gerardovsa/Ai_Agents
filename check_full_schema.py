"""Check prompt_library table full definition"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cur = conn.cursor()

# Get table definition
cur.execute("""
    SELECT 
        column_name,
        data_type,
        column_default,
        is_nullable
    FROM information_schema.columns
    WHERE table_name='prompt_library' AND table_schema='ai_infrastructure'
    ORDER BY ordinal_position
""")

cols = cur.fetchall()

print("\n=== prompt_library FULL SCHEMA ===\n")
for col in cols:
    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
    default = f"DEFAULT {col['column_default']}" if col['column_default'] else "NO DEFAULT"
    print(f"{col['column_name']:20s} {col['data_type']:20s} {nullable:10s} {default}")

# Check for sequences
print("\n=== SEQUENCES ===\n")
cur.execute("""
    SELECT sequence_name
    FROM information_schema.sequences
    WHERE sequence_schema='ai_infrastructure'
""")
seqs = cur.fetchall()
for seq in seqs:
    print(f"  - {seq['sequence_name']}")

conn.close()
