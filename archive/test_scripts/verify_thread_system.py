"""
Verify the thread system is working correctly

Checks:
1. sessions.db has threads table
2. ai_infrastructure.db has thread_assignments table
3. Shows current threads for user_id=12
4. Shows current thread assignments
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent

print("="*60)
print("THREAD SYSTEM VERIFICATION")
print("="*60)

# 1. Check threads in sessions.db
print("\n1. THREADS (sessions.db):")
db_path = root_dir / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# First check table structure
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()
print("   Columns:", [col['name'] for col in columns])

# Get threads
cursor.execute("""
    SELECT * 
    FROM threads 
    WHERE user_id = 12 
    ORDER BY created_at DESC
""")
threads = cursor.fetchall()

print(f"\n   Found {len(threads)} threads for user_id=12:")
for thread in threads:
    print(f"   - ID: {thread['id']}, Created: {thread['created_at']}")
    # Print all columns for first thread to see structure
    if threads.index(thread) == 0:
        print(f"     Full data: {dict(thread)}")

conn.close()

# 2. Check thread assignments in ai_infrastructure.db
print("\n2. THREAD ASSIGNMENTS (ai_infrastructure.db):")
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT id, user_id, session_id, location, agent_name, updated_at
    FROM thread_assignments
    WHERE user_id = 12
    ORDER BY updated_at DESC
""")
assignments = cursor.fetchall()

print(f"   Found {len(assignments)} thread assignments for user_id=12:")
for assignment in assignments:
    print(f"   - session_id: {assignment['session_id']}, location: {assignment['location']}, agent: {assignment['agent_name']}")

conn.close()

# 3. Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"✓ Threads in database: {len(threads)}")
print(f"✓ Thread assignments: {len(assignments)}")

if len(threads) == 0:
    print("\n[OK] No threads exist - system should show empty state")
elif len(assignments) == 0:
    print("\n[OK] Threads exist but no assignments - ready for user to assign")
else:
    print(f"\n[INFO] {len(assignments)} threads are assigned to agents")

print("\n[DONE]")
