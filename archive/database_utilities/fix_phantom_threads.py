"""
Fix phantom thread assignments in sessions.db
from shared.database_utils import convert_sql_placeholders

This script:
1. Shows current threads in sessions table
2. Shows thread assignments
3. Removes assignments for threads that don't exist
"""

import sqlite3
from pathlib import Path

# Connect to ai_infrastructure.db (where thread_assignments lives)
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print(f"Connecting to: {db_path}")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n" + "="*60)
print("CURRENT STATE")
print("="*60)

# 1. Check threads table
cursor.execute("SELECT id, user_id, session_id, created_at FROM threads WHERE user_id = 12 ORDER BY created_at DESC")
threads = cursor.fetchall()
print(f"\n1. Threads table ({len(threads)} rows) for user_id=12:")
for row in threads:
    print(f"   - id: {row['id']}, session_id: {row['session_id']}, created: {row['created_at']}")

# 2. Check thread_assignments table (if present), otherwise show threads with location
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_assignments'")
if cursor.fetchone():
    try:
        cursor.execute("SELECT agent_id, session_id, assigned_at FROM thread_assignments ORDER BY assigned_at DESC")
        assignments = cursor.fetchall()
        print(f"\n2. Thread assignments ({len(assignments)} rows):")
        for row in assignments:
            print(f"   - agent_id: {row['agent_id']}, session_id: {row['session_id']}, assigned: {row['assigned_at']}")
    except Exception as e:
        print(f"[WARN] Failed to read thread_assignments: {e}")
        assignments = []
else:
    print('\n[INFO] thread_assignments table not found - deriving assignments from threads.location')
    # Attempt to derive assignments from threads.location
    # Note: threads table may live in sessions.db - try to open sessions.db if available
    try:
        import sqlite3 as _sqlite3
        sess_conn = _sqlite3.connect('data/sessions.db')
        sess_conn.row_factory = _sqlite3.Row
        sc = sess_conn.cursor()
        sc.execute("SELECT id, thread_slug, location FROM threads WHERE location IS NOT NULL")
        assignments = []
        for r in sc.fetchall():
            assignments.append({'agent_id': r['location'], 'session_id': str(r['id']), 'assigned_at': None})
            print(f"   - derived agent: {r['location']}, session_id: {r['id']}")
        sess_conn.close()
    except Exception as ex:
        print(f"[ERROR] Could not derive assignments from threads.location: {ex}")
        assignments = []

# 3. Find phantom assignments (assignments without matching threads)
thread_session_ids = set(row['session_id'] for row in threads)
print(f"\n3. Valid thread session IDs: {thread_session_ids}")

phantom_count = 0
for assignment in assignments:
    if assignment['session_id'] not in thread_session_ids:
        print(f"   [PHANTOM] agent_id={assignment['agent_id']}, session_id={assignment['session_id']}")
        phantom_count += 1

if phantom_count == 0:
    print("   [OK] No phantom assignments found!")
else:
    print(f"\n[WARNING] Found {phantom_count} phantom assignments!")
    
    # Ask user if they want to clean up
    print("\n" + "="*60)
    print("CLEANUP OPTIONS")
    print("="*60)
    print("1. Delete ALL thread assignments (clean slate)")
    print("2. Delete ONLY phantom assignments (keep valid ones)")
    print("3. Cancel (no changes)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        cursor.execute("DELETE FROM thread_assignments")
        conn.commit()
        print(f"\n[OK] Deleted ALL {len(assignments)} thread assignments")
    elif choice == "2":
        deleted = 0
        for assignment in assignments:
            if assignment['session_id'] not in thread_session_ids:
                sql, params = convert_sql_placeholders("DELETE FROM thread_assignments WHERE agent_id = ? AND session_id = ?", (assignment['agent_id'], assignment['session_id']))

                cursor.execute(sql, params)
                deleted += 1
        conn.commit()
        print(f"\n[OK] Deleted {deleted} phantom assignments")
    else:
        print("\n[CANCELLED] No changes made")

# Show final state
print("\n" + "="*60)
print("FINAL STATE")
print("="*60)

if cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_assignments'").fetchone():
    cursor.execute("SELECT agent_id, session_id FROM thread_assignments")
    final_assignments = cursor.fetchall()
    print(f"\nThread assignments remaining: {len(final_assignments)}")
    for row in final_assignments:
        print(f"   - agent_id: {row['agent_id']}, session_id: {row['session_id']}")
else:
    print('\n[INFO] No thread_assignments table - final assignments derived from threads.location shown above (if any)')

conn.close()
print("\n[DONE]")
