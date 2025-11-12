"""Check threads and messages to verify everything is working"""

import sqlite3
from pathlib import Path
import json

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("CHECKING THREADS AND MESSAGES")
print("=" * 80)

conn = sqlite3.connect(str(sessions_db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check threads
print("\n📋 THREADS TABLE:")
print("-" * 80)
cursor.execute("""
    SELECT id, thread_slug, name, user_id, created_at, location, 
           parent_thread_id, branch_point_message_id, branch_name
    FROM threads 
    ORDER BY created_at DESC 
    LIMIT 10
""")

threads = cursor.fetchall()
print(f"Found {len(threads)} recent threads:\n")

for thread in threads:
    print(f"Thread ID: {thread['thread_slug']}")
    print(f"  Name: {thread['name']}")
    print(f"  Location: {thread['location']}")
    print(f"  User: {thread['user_id']}")
    print(f"  Created: {thread['created_at']}")
    if thread['parent_thread_id']:
        print(f"  Branch from: {thread['parent_thread_id']} (message: {thread['branch_point_message_id']})")
        print(f"  Branch name: {thread['branch_name']}")
    
    # Count messages for this thread
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM messages 
        WHERE thread_id = ?
    """, [thread['id']])
    msg_count = cursor.fetchone()['count']
    print(f"  Messages: {msg_count}")
    print()

# Check messages
print("\n💬 MESSAGES TABLE:")
print("-" * 80)
cursor.execute("""
    SELECT m.id, m.thread_id, m.role, m.content, m.timestamp, t.thread_slug, t.name
    FROM messages m
    JOIN threads t ON m.thread_id = t.id
    ORDER BY m.timestamp DESC
    LIMIT 10
""")

messages = cursor.fetchall()
print(f"Found {len(messages)} recent messages:\n")

for msg in messages:
    content_preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
    print(f"Message {msg['id']} in thread {msg['thread_slug']} ({msg['name']})")
    print(f"  Role: {msg['role']}")
    print(f"  Content: {content_preview}")
    print(f"  Time: {msg['timestamp']}")
    print()

# Check thread schema
print("\n🔍 THREADS TABLE SCHEMA:")
print("-" * 80)
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()
for col in columns:
    if col['name'] in ['branch_point_message_id', 'parent_thread_id', 'branch_name']:
        print(f"✅ {col['name']:<30} {col['type']:<15}")
    else:
        print(f"   {col['name']:<30} {col['type']:<15}")

# Check if any users have thread assignments
print("\n📍 THREAD ASSIGNMENTS (from users.metadata):")
print("-" * 80)

ai_db = root_dir / 'data' / 'ai_infrastructure.db'
ai_conn = sqlite3.connect(str(ai_db))
ai_conn.row_factory = sqlite3.Row
ai_cursor = ai_conn.cursor()

ai_cursor.execute("SELECT id, username, metadata FROM users WHERE metadata IS NOT NULL AND metadata != '{}'")
users = ai_cursor.fetchall()

if users:
    for user in users:
        try:
            metadata = json.loads(user['metadata'])
            assignments = metadata.get('thread_assignments', {})
            if assignments:
                print(f"\nUser {user['id']} ({user['username']}):")
                for location, thread_id in assignments.items():
                    print(f"  {location}: {thread_id}")
        except json.JSONDecodeError:
            pass
else:
    print("No thread assignments found")

ai_conn.close()
conn.close()

print("\n" + "=" * 80)
print("CHECK COMPLETE")
print("=" * 80)
