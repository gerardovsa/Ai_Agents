"""Keep only the real conversation (hello what time is it)"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("KEEPING ONLY REAL CONVERSATION")
print("="*60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Find the TEST 1 thread
cursor.execute("SELECT id, thread_slug FROM threads WHERE name = 'TEST 1'")
thread = cursor.fetchone()

thread_id = thread[0]
thread_slug = thread[1]

print(f"\n📍 Thread: {thread_slug} (ID: {thread_id})")

# Delete all test messages
print("\n🗑️  Deleting test messages...")

# Delete "First test message"
cursor.execute("DELETE FROM messages WHERE thread_id = ? AND content = 'First test message'", (thread_id,))
print(f"   - Deleted {cursor.rowcount} 'First test message' messages")

# Delete "Hello! I am the AI response"
cursor.execute("DELETE FROM messages WHERE thread_id = ? AND content = 'Hello! I am the AI response'", (thread_id,))
print(f"   - Deleted {cursor.rowcount} 'Hello! I am the AI response' messages")

# Delete "THIS IS A REAL TEST MESSAGE FROM PYTHON SCRIPT"
cursor.execute("DELETE FROM messages WHERE thread_id = ? AND content LIKE '%THIS IS A REAL TEST MESSAGE%'", (thread_id,))
print(f"   - Deleted {cursor.rowcount} Python test messages")

# Keep only unique messages by created_at (remove duplicates)
print("\n🔄 Removing duplicates...")

# Get all remaining messages
sql, params = convert_sql_placeholders("""
    SELECT id, role, content, created_at 
    FROM messages 
    WHERE thread_id = ? 
    ORDER BY created_at
""", (thread_id,))

cursor.execute(sql, params)
messages = cursor.fetchall()

# Track seen content+role combinations
seen = set()
to_delete = []

for msg_id, role, content, created_at in messages:
    key = (role, content[:100])  # Use first 100 chars as key
    if key in seen:
        to_delete.append(msg_id)
    else:
        seen.add(key)

if to_delete:
    placeholders = ','.join('?' * len(to_delete))
    cursor.execute(f"DELETE FROM messages WHERE id IN ({placeholders})", to_delete)
    print(f"   - Deleted {cursor.rowcount} duplicate messages")

conn.commit()

# Show remaining messages
sql, params = convert_sql_placeholders("""
    SELECT id, role, content, created_at 
    FROM messages 
    WHERE thread_id = ? 
    ORDER BY created_at
""", (thread_id,))

cursor.execute(sql, params)
final_messages = cursor.fetchall()

print(f"\n✅ FINAL MESSAGES ({len(final_messages)}):")
for msg_id, role, content, created_at in final_messages:
    preview = content[:70] + '...' if len(content) > 70 else content
    print(f"\n   {msg_id}. [{role}]")
    print(f"      {preview}")
    print(f"      Created: {created_at}")

conn.close()

print("\n" + "="*60)
print("✅ Database cleaned! Refresh browser to see clean thread.")
print("="*60)
