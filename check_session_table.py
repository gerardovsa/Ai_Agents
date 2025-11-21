from AI_infrastructure.shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

print("\nChecking for session tables in ai_infrastructure schema:")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'ai_infrastructure' 
    AND table_name LIKE '%session%'
""")

tables = cursor.fetchall()
if tables:
    for row in tables:
        table_name = row['table_name'] if isinstance(row, dict) else row[0]
        print(f"  - {table_name}")
else:
    print("  NO session tables found!")

print("\nTrying to access ai_infrastructure.user_sessions:")
try:
    cursor.execute("SELECT COUNT(*) as count FROM ai_infrastructure.user_sessions")
    result = cursor.fetchone()
    count = result['count'] if isinstance(result, dict) else result[0]
    print(f"  ✅ Table exists with {count} records")
except Exception as e:
    print(f"  ❌ Error: {e}")

conn.close()
