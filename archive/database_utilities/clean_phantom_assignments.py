"""
Clean phantom thread assignments from users.metadata in ai_infrastructure.db

The frontend loads old thread assignments from users.metadata JSON field,
but those threads no longer exist. This script cleans them up.
"""

import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print(f"Connecting to: {db_path}\n")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get user_id=12's metadata
cursor.execute("SELECT id, email, metadata FROM users WHERE id = 12")
user = cursor.fetchone()

if not user:
    print("[ERROR] User 12 not found")
    conn.close()
    exit(1)

print("="*60)
print(f"USER: {user['email']} (ID: {user['id']})")
print("="*60)

# Parse metadata
metadata = json.loads(user['metadata']) if user['metadata'] else {}
assignments = metadata.get('thread_assignments', {})

print(f"\nCurrent thread_assignments in metadata:")
if not assignments:
    print("  (empty)")
else:
    for agent_id, session_id in assignments.items():
        print(f"  - {agent_id}: {session_id}")

# Get actual existing threads from sessions.db
sessions_db = root_dir / 'data' / 'sessions.db'
sessions_conn = sqlite3.connect(str(sessions_db))
sessions_conn.row_factory = sqlite3.Row
sessions_cursor = sessions_conn.cursor()

sessions_cursor.execute("""
    SELECT id, thread_slug, name 
    FROM threads 
    WHERE user_id = 12
""")
real_threads = sessions_cursor.fetchall()
sessions_conn.close()

real_thread_ids = set()
print(f"\nReal threads in database:")
if not real_threads:
    print("  (no threads)")
else:
    for thread in real_threads:
        print(f"  - ID: {thread['id']}, slug: {thread['thread_slug']}, name: {thread['name']}")
        real_thread_ids.add(str(thread['id']))
        real_thread_ids.add(thread['thread_slug'])

# Find phantom assignments
phantom_agents = []
for agent_id, session_id in assignments.items():
    if session_id not in real_thread_ids:
        phantom_agents.append(agent_id)
        print(f"\n[PHANTOM] {agent_id} -> {session_id} (thread doesn't exist)")

# Clean up
if phantom_agents:
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    print(f"Found {len(phantom_agents)} phantom assignments")
    
    choice = input("\nDelete phantom assignments? (y/n): ").strip().lower()
    
    if choice == 'y':
        # Remove phantom assignments
        for agent_id in phantom_agents:
            del assignments[agent_id]
        
        # Update metadata
        metadata['thread_assignments'] = assignments
        new_metadata = json.dumps(metadata)
        
        cursor.execute("UPDATE users SET metadata = ? WHERE id = 12", (new_metadata,))
        conn.commit()
        
        print(f"\n[OK] Deleted {len(phantom_agents)} phantom assignments")
        print(f"Remaining assignments: {len(assignments)}")
        for agent_id, session_id in assignments.items():
            print(f"  - {agent_id}: {session_id}")
    else:
        print("\n[CANCELLED] No changes made")
else:
    print("\n[OK] No phantom assignments found")

conn.close()
print("\n[DONE]")
