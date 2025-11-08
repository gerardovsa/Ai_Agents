"""
CLEAR ALL DATA from sessions.db database

This will:
1. Delete ALL threads
2. Delete ALL messages
3. Delete ALL sessions
4. Delete ALL saved_threads
5. Reset users metadata (including thread_assignments)

USE WITH CAUTION - THIS WILL DELETE EVERYTHING!
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("CLEAR SESSIONS DATABASE")
print("="*60)
print(f"\nDatabase: {db_path}")
print("\n⚠️  WARNING: This will DELETE ALL DATA from sessions.db!")
print("This includes:")
print("  - All threads")
print("  - All messages")
print("  - All sessions")
print("  - All saved threads")
print("  - User metadata (thread assignments)")
print("\n" + "="*60)

choice = input("\nType 'DELETE ALL' to proceed (or anything else to cancel): ").strip()

if choice != "DELETE ALL":
    print("\n[CANCELLED] No changes made")
    exit(0)

print("\n🔥 DELETING ALL DATA...")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Show before state
print("\n📊 Before deletion:")
for table in ['threads', 'messages', 'sessions', 'saved_threads', 'users']:
    try:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"  - {table}: {count} rows")
    except:
        print(f"  - {table}: (table doesn't exist)")

# Delete all data
print("\n🔥 Deleting data...")

# 1. Delete all messages
cursor.execute("DELETE FROM messages")
deleted_messages = cursor.rowcount
print(f"  ✓ Deleted {deleted_messages} messages")

# 2. Delete all threads
cursor.execute("DELETE FROM threads")
deleted_threads = cursor.rowcount
print(f"  ✓ Deleted {deleted_threads} threads")

# 3. Delete all sessions
cursor.execute("DELETE FROM sessions")
deleted_sessions = cursor.rowcount
print(f"  ✓ Deleted {deleted_sessions} sessions")

# 4. Delete all saved threads
cursor.execute("DELETE FROM saved_threads")
deleted_saved = cursor.rowcount
print(f"  ✓ Deleted {deleted_saved} saved threads")

# 5. Clear user metadata (thread_assignments)
cursor.execute("SELECT id, username, metadata FROM users")
users = cursor.fetchall()
for user in users:
    if user['metadata']:
        cursor.execute("UPDATE users SET metadata = '{}' WHERE id = ?", (user['id'],))
        print(f"  ✓ Cleared metadata for user {user['username']} (id={user['id']})")

# 6. Reset sqlite_sequence (auto-increment counters)
cursor.execute("DELETE FROM sqlite_sequence")
print(f"  ✓ Reset auto-increment counters")

conn.commit()

# Show after state
print("\n📊 After deletion:")
for table in ['threads', 'messages', 'sessions', 'saved_threads']:
    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
    count = cursor.fetchone()['count']
    print(f"  - {table}: {count} rows")

cursor.execute("SELECT id, username, metadata FROM users")
users = cursor.fetchall()
print(f"  - users: {len(users)} users (metadata cleared)")

conn.close()

print("\n" + "="*60)
print("✅ SESSIONS DATABASE CLEARED SUCCESSFULLY")
print("="*60)
print("\nThe database is now completely empty.")
print("Restart your Flask server and refresh the browser.")
