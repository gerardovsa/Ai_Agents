"""Check users table schema"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Check id column
cursor.execute("""
    SELECT column_name, column_default, is_nullable, data_type
    FROM information_schema.columns 
    WHERE table_schema = 'ai_infrastructure' 
    AND table_name = 'users' 
    AND column_name = 'id'
""")
row = cursor.fetchone()

print(f"Column: {row['column_name']}")
print(f"Default: {row['column_default']}")
print(f"Nullable: {row['is_nullable']}")
print(f"Type: {row['data_type']}")

conn.close()
