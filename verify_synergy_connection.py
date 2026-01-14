"""
Verify Synergy Sessions Database Connection
Check that we're connected to the correct Supabase schema and tables
"""
import sys
sys.path.insert(0, 'c:\\Users\\gpoli\\GIT\\AI_agents\\AI_infrastructure')

from shared.database_utils import get_synergy_sessions_connection, is_using_supabase

print("=" * 70)
print("SYNERGY SESSIONS DATABASE CONNECTION VERIFICATION")
print("=" * 70)

print(f"\nUsing Supabase: {is_using_supabase()}")

conn = get_synergy_sessions_connection()
cursor = conn.cursor()

# Check current schema
cursor.execute('SELECT current_schema()')
current_schema = cursor.fetchone()
print(f"Current schema: {current_schema}")

# Check search path
cursor.execute('SHOW search_path')
search_path = cursor.fetchone()
print(f"Search path: {search_path}")

# List tables in synergy_sessions schema
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'synergy_sessions' 
    ORDER BY table_name
""")
tables = cursor.fetchall()

print("\n" + "=" * 70)
print("TABLES IN synergy_sessions SCHEMA:")
print("=" * 70)
for table in tables:
    table_name = table['table_name'] if isinstance(table, dict) else table[0]
    print(f"  ✅ {table_name}")

# Check record counts
print("\n" + "=" * 70)
print("RECORD COUNTS:")
print("=" * 70)

table_queries = [
    ('synergy_sessions', 'SELECT COUNT(*) FROM synergy_sessions.synergy_sessions'),
    ('synergy_internal_docs', 'SELECT COUNT(*) FROM synergy_sessions.synergy_internal_docs'),
    ('milestones', 'SELECT COUNT(*) FROM synergy_sessions.milestones'),
    ('tasks', 'SELECT COUNT(*) FROM synergy_sessions.tasks'),
    ('subtasks', 'SELECT COUNT(*) FROM synergy_sessions.subtasks'),
]

for table_name, query in table_queries:
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        count = result['count'] if isinstance(result, dict) else result[0]
        print(f"  {table_name}: {count} records")
    except Exception as e:
        print(f"  {table_name}: ERROR - {e}")

# Test a sample query without schema prefix (relying on search_path)
print("\n" + "=" * 70)
print("TEST: Query WITHOUT schema prefix (relying on search_path)")
print("=" * 70)

try:
    cursor.execute("SELECT COUNT(*) FROM synergy_sessions")
    result = cursor.fetchone()
    count = result['count'] if isinstance(result, dict) else result[0]
    print(f"✅ SUCCESS: Found {count} records in 'synergy_sessions' table")
    print("   (search_path is working correctly)")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("   (search_path NOT working - need explicit schema prefix)")

conn.close()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
