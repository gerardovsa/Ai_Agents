"""
Check which user_id owns the threads in sessions.db
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()

print("=" * 80)
print("THREAD OWNERSHIP IN SESSIONS.DB")
print("=" * 80)

# Get all threads
cursor.execute("""
    SELECT id, user_id, thread_slug, name, location, created_at 
    FROM threads 
    ORDER BY user_id, created_at DESC
""")
threads = cursor.fetchall()

print(f"\nTotal threads: {len(threads)}")

# Group by user_id
user_threads = {}
for thread in threads:
    thread_id, user_id, slug, name, location, created_at = thread
    if user_id not in user_threads:
        user_threads[user_id] = []
    user_threads[user_id].append({
        'id': thread_id,
        'slug': slug,
        'name': name,
        'location': location,
        'created_at': created_at
    })

print("\n" + "=" * 80)
print("THREADS BY USER")
print("=" * 80)

for user_id, user_thread_list in user_threads.items():
    # Get user email
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    user_email = user_row[0] if user_row else "UNKNOWN"
    
    print(f"\nUser ID {user_id} ({user_email}): {len(user_thread_list)} threads")
    for thread in user_thread_list:
        print(f"  - [{thread['location']}] {thread['name'][:50]}")
        print(f"    Slug: {thread['slug']} | Created: {thread['created_at']}")

# Check User 14 specifically
print("\n" + "=" * 80)
print("USER 14 (printing@inhouseprint.com.au) THREADS")
print("=" * 80)

cursor.execute("SELECT id, email FROM users WHERE id = 14")
user_14 = cursor.fetchone()
if user_14:
    print(f"User 14 exists: {user_14[1]}")
else:
    print("User 14 NOT FOUND!")

cursor.execute("SELECT COUNT(*) FROM threads WHERE user_id = 14")
count = cursor.fetchone()[0]
print(f"Threads for User 14: {count}")

if count == 0:
    print("\nPROBLEM: User 14 has no threads!")
    print("\nPOSSIBLE CAUSES:")
    print("1. Threads were created before user was synced")
    print("2. Threads belong to User 1 (gerardo@vetsuccessacademy.com)")
    print("3. Threads were created with wrong user_id")
    print("\nOPTIONS:")
    print("A. Assign existing threads to User 14")
    print("B. Create new threads for User 14")
    print("C. Check if frontend is using wrong user_id")

conn.close()

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("\n1. If threads belong to User 1 but should be User 14:")
print("   Run: UPDATE threads SET user_id = 14 WHERE user_id = 1;")
print("\n2. If User 14 should have separate threads:")
print("   Create new threads via frontend while logged in as printing@")
print("\n3. Check frontend to see what user_id is being used")
