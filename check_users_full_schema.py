"""Check users table definition"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Get table definition
cursor.execute("""
    SELECT 
        column_name, 
        data_type, 
        column_default, 
        is_nullable,
        character_maximum_length
    FROM information_schema.columns 
    WHERE table_schema = 'ai_infrastructure' 
    AND table_name = 'users'
    ORDER BY ordinal_position
""")

print("Users table columns:")
print("-" * 80)
for row in cursor.fetchall():
    print(f"Column: {row['column_name']}")
    print(f"  Type: {row['data_type']}")
    print(f"  Default: {row['column_default']}")
    print(f"  Nullable: {row['is_nullable']}")
    if row['character_maximum_length']:
        print(f"  Max Length: {row['character_maximum_length']}")
    print()

# Check for sequence
cursor.execute("""
    SELECT 
        schemaname, 
        sequencename, 
        last_value
    FROM pg_sequences
    WHERE schemaname = 'ai_infrastructure'
    AND sequencename LIKE '%users%'
""")

print("\nSequences for users table:")
print("-" * 80)
sequences = cursor.fetchall()
if sequences:
    for row in sequences:
        print(f"Sequence: {row['schemaname']}.{row['sequencename']}")
        print(f"  Last value: {row['last_value']}")
else:
    print("No sequences found for users table!")

conn.close()
