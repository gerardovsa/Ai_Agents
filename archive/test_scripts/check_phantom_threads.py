"""
Check where phantom thread assignments are coming from
"""

import sqlite3
import json
from pathlib import Path

# Connect to sessions.db
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print(f"Checking: {db_path}")
print("=" * 60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check all users
cursor.execute("SELECT id, username, metadata FROM users ORDER BY id")
users = cursor.fetchall()

print(f"\nFound {len(users)} users:\n")

for user_id, username, metadata_json in users:
    print(f"User {user_id} ({username}):")
    
    if metadata_json:
        metadata = json.loads(metadata_json)
        assignments = metadata.get('thread_assignments', {})
        
        if assignments:
            print(f"  THREAD ASSIGNMENTS FOUND:")
            for location, thread_id in assignments.items():
                print(f"    {location} → {thread_id}")
        else:
            print(f"  No thread assignments")
    else:
        print(f"  No metadata")
    
    print()

# Check if those threads actually exist
print("\n" + "=" * 60)
print("CHECKING IF THREADS EXIST IN DATABASE:")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM threads")
thread_count = cursor.fetchone()[0]

print(f"\nFound {thread_count} threads in database:")
if thread_count > 0:
    cursor.execute("SELECT * FROM threads LIMIT 1")
    print(f"  Sample thread columns: {[desc[0] for desc in cursor.description]}")
else:
    print("  (NO THREADS IN DATABASE)")

conn.close()

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("If users have thread_assignments in metadata BUT no threads")
print("exist in the threads table, the UI will show phantom threads.")
print("\nSOLUTION: Clear the thread_assignments from user metadata.")
