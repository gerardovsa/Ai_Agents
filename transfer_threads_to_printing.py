"""
Transfer all threads from User 1 to User 14 (printing@inhouseprint.com.au)
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("TRANSFERRING THREADS TO printing@inhouseprint.com.au")
print("=" * 80)

conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()

# Step 1: Verify users exist
print("\n[1] Verifying users...")
cursor.execute("SELECT id, email FROM users WHERE id IN (1, 14)")
users = cursor.fetchall()

print(f"  Found {len(users)} users:")
for user in users:
    print(f"    User ID {user[0]}: {user[1]}")

if len(users) < 2:
    print("\n  ERROR: Both users must exist!")
    conn.close()
    exit(1)

# Step 2: Show threads before transfer
print("\n[2] Threads BEFORE transfer:")
cursor.execute("""
    SELECT id, user_id, thread_slug, name, location 
    FROM threads 
    WHERE user_id IN (1, 14)
    ORDER BY user_id, created_at DESC
""")
threads_before = cursor.fetchall()

for thread in threads_before:
    print(f"  Thread {thread[0]}: User {thread[1]} -> [{thread[4]}] {thread[2]} - {thread[3]}")

# Step 3: Count threads to transfer
cursor.execute("SELECT COUNT(*) FROM threads WHERE user_id = 1")
count_user_1 = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM threads WHERE user_id = 14")
count_user_14 = cursor.fetchone()[0]

print(f"\n  User 1 (gerardo@vetsuccessacademy.com): {count_user_1} threads")
print(f"  User 14 (printing@inhouseprint.com.au): {count_user_14} threads")

# Step 4: Transfer threads
print("\n[3] Transferring threads from User 1 to User 14...")

cursor.execute("""
    UPDATE threads 
    SET user_id = 14 
    WHERE user_id = 1
""")

affected_rows = cursor.rowcount
conn.commit()

print(f"  SUCCESS: Transferred {affected_rows} threads to User 14")

# Step 5: Also transfer messages (if any)
print("\n[4] Transferring messages...")
cursor.execute("""
    UPDATE messages 
    SET user_id = 14 
    WHERE user_id = 1
""")

messages_affected = cursor.rowcount
conn.commit()

print(f"  SUCCESS: Transferred {messages_affected} messages to User 14")

# Step 6: Verify transfer
print("\n[5] Threads AFTER transfer:")
cursor.execute("""
    SELECT id, user_id, thread_slug, name, location 
    FROM threads 
    WHERE user_id IN (1, 14)
    ORDER BY user_id, created_at DESC
""")
threads_after = cursor.fetchall()

for thread in threads_after:
    print(f"  Thread {thread[0]}: User {thread[1]} -> [{thread[4]}] {thread[2]} - {thread[3]}")

# Final counts
cursor.execute("SELECT COUNT(*) FROM threads WHERE user_id = 1")
final_count_user_1 = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM threads WHERE user_id = 14")
final_count_user_14 = cursor.fetchone()[0]

print(f"\n  User 1 (gerardo@vetsuccessacademy.com): {final_count_user_1} threads")
print(f"  User 14 (printing@inhouseprint.com.au): {final_count_user_14} threads")

conn.close()

print("\n" + "=" * 80)
print("TRANSFER COMPLETE!")
print("=" * 80)
print("\nSUMMARY:")
print(f"  Threads transferred: {affected_rows}")
print(f"  Messages transferred: {messages_affected}")
print(f"\n  printing@inhouseprint.com.au now has {final_count_user_14} threads:")
print("    - Outlook - Email Quotes")
print("    - New Chat")
print("    - Outlook Emails - Quotes (2x)")
print("    - Test Thread - Budget Analysis Q4")
print("    - Test Thread - Budget Analysis")
print("\nNEXT STEPS:")
print("1. Test API endpoint:")
print('   curl "http://localhost:5001/api/threads/list?user_id=14"')
print("\n2. Test in browser:")
print("   - Login as printing@inhouseprint.com.au")
print("   - Refresh the page")
print("   - All 6 threads should now appear in the threads list")
print("\n3. Check thread assignments in users.metadata")
print("   (may need to be updated if threads were assigned to agent columns)")
