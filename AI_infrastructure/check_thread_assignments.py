from shared.database_utils import execute_query

# Check if table exists
result = execute_query("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'sessions' 
    AND table_name = 'thread_assignments'
""", fetch_mode='all')

print(f"✅ Table exists: {len(result) > 0}")
if result:
    print(f"   Found table: {result[0]}")

# Check columns
columns = execute_query("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'sessions' 
    AND table_name = 'thread_assignments'
    ORDER BY ordinal_position
""", fetch_mode='all')

print(f"\n📋 Columns ({len(columns)}):")
for col in columns:
    print(f"   - {col['column_name']}: {col['data_type']}")
