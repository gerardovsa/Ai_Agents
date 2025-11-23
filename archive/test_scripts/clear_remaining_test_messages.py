"""Clear remaining test messages"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("CLEARING REMAINING TEST MESSAGES")
print("="*60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Find the TEST 1 thread
cursor.execute("SELECT id, thread_slug FROM threads WHERE name = 'TEST 1'")
thread = cursor.fetchone()

thread_id = thread[0]
thread_slug = thread[1]

print(f"\n📍 Thread: {thread_slug} (ID: {thread_id})")

# Delete messages with "THIS IS THE AI RESPONSE TO THE TEST"
sql, params = convert_sql_placeholders("""
    DELETE FROM messages 
    WHERE thread_id = ? 
    AND content LIKE '%THIS IS THE AI RESPONSE TO THE TEST%'
""", (thread_id,))

cursor.execute(sql, params)

deleted = cursor.rowcount
conn.commit()

print(f"\n✅ Deleted {deleted} messages containing 'THIS IS THE AI RESPONSE TO THE TEST'")

# Show remaining messages
sql, params = convert_sql_placeholders("SELECT id, role, content, created_at FROM messages WHERE thread_id = ? ORDER BY created_at", (thread_id,))

cursor.execute(sql, params)
messages = cursor.fetchall()

print(f"\n📊 Remaining messages ({len(messages)}):")
for msg in messages:
    msg_id, role, content, created_at = msg
    preview = content[:70] + '...' if len(content) > 70 else content
    print(f"   {msg_id}. [{role}] {preview}")
    print(f"      Created: {created_at}")

conn.close()

print("\n" + "="*60)
print("DONE - Refresh browser to see clean thread!")
print("="*60)
