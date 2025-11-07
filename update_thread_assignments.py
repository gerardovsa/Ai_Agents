"""
Update thread assignments in users.metadata from User 1 to User 14
"""

import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("UPDATING THREAD ASSIGNMENTS")
print("=" * 80)

conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()

# Step 1: Check User 1 metadata
print("\n[1] Checking User 1 (gerardo@vetsuccessacademy.com) metadata...")
cursor.execute("SELECT id, metadata FROM users WHERE id = 1")
user_1 = cursor.fetchone()

if user_1:
    user_1_metadata = json.loads(user_1[1] or '{}')
    user_1_assignments = user_1_metadata.get('thread_assignments', {})
    
    print(f"  User 1 metadata: {user_1_metadata}")
    print(f"  Thread assignments: {user_1_assignments}")
    
    if user_1_assignments:
        print(f"\n  Found {len(user_1_assignments)} thread assignments to transfer:")
        for agent, thread_id in user_1_assignments.items():
            print(f"    {agent}: {thread_id}")
    else:
        print("  No thread assignments found in User 1 metadata")
else:
    print("  User 1 not found")
    user_1_assignments = {}

# Step 2: Check User 14 metadata
print("\n[2] Checking User 14 (printing@inhouseprint.com.au) metadata...")
cursor.execute("SELECT id, metadata FROM users WHERE id = 14")
user_14 = cursor.fetchone()

if user_14:
    user_14_metadata = json.loads(user_14[1] or '{}')
    user_14_assignments = user_14_metadata.get('thread_assignments', {})
    
    print(f"  User 14 metadata: {user_14_metadata}")
    print(f"  Thread assignments: {user_14_assignments}")
else:
    print("  User 14 not found!")
    conn.close()
    exit(1)

# Step 3: Transfer assignments if User 1 had any
if user_1_assignments:
    print("\n[3] Transferring thread assignments...")
    
    # Clear User 1 assignments
    user_1_metadata['thread_assignments'] = {}
    cursor.execute("""
        UPDATE users 
        SET metadata = ? 
        WHERE id = 1
    """, (json.dumps(user_1_metadata),))
    
    # Add to User 14 assignments (merge with existing if any)
    user_14_metadata['thread_assignments'] = {**user_14_assignments, **user_1_assignments}
    cursor.execute("""
        UPDATE users 
        SET metadata = ? 
        WHERE id = 14
    """, (json.dumps(user_14_metadata),))
    
    conn.commit()
    
    print(f"  SUCCESS: Transferred {len(user_1_assignments)} thread assignments")
    print(f"\n  User 14 now has {len(user_14_metadata['thread_assignments'])} thread assignments:")
    for agent, thread_id in user_14_metadata['thread_assignments'].items():
        print(f"    {agent}: {thread_id}")
else:
    print("\n[3] No thread assignments to transfer")

# Step 4: Verify final state
print("\n[4] Final verification...")
cursor.execute("SELECT id, email, metadata FROM users WHERE id IN (1, 14)")
users = cursor.fetchall()

for user in users:
    user_id, email, metadata = user
    metadata_obj = json.loads(metadata or '{}')
    assignments = metadata_obj.get('thread_assignments', {})
    
    print(f"\n  User {user_id} ({email}):")
    print(f"    Thread assignments: {len(assignments)}")
    if assignments:
        for agent, thread_id in assignments.items():
            print(f"      {agent}: {thread_id}")

conn.close()

print("\n" + "=" * 80)
print("THREAD ASSIGNMENTS UPDATE COMPLETE")
print("=" * 80)
print("\nSUMMARY:")
print("  All threads now belong to printing@inhouseprint.com.au (User 14)")
print("  Thread assignments transferred to User 14's metadata")
print("\nREADY TO TEST:")
print("  1. Login as printing@inhouseprint.com.au")
print("  2. Refresh browser")
print("  3. You should see all 6 threads in the threads list")
print("  4. Any agent column assignments should be preserved")
