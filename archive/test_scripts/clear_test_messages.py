"""Clear the old test messages from database"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("CLEARING TEST MESSAGES")
print("="*60)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find the TEST 1 thread
cursor.execute("SELECT id, thread_slug FROM threads WHERE name = 'TEST 1'")
thread = cursor.fetchone()

if not thread:
    print("❌ Thread 'TEST 1' not found")
    conn.close()
    exit(0)

thread_id = thread['id']
thread_slug = thread['thread_slug']

print(f"\n📍 Thread: {thread_slug} (ID: {thread_id})")

# Show current messages
sql, params = convert_sql_placeholders("SELECT id, role, content FROM messages WHERE thread_id = ? ORDER BY created_at", (thread_id,))

cursor.execute(sql, params)
messages = cursor.fetchall()

print(f"\n📊 Current messages ({len(messages)}):")
for msg in messages:
    preview = msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content']
    print(f"   {msg['id']}. [{msg['role']}] {preview}")

# Identify test messages (the fake ones)
test_message_ids = []
for msg in messages:
    content = msg['content'].lower()
    if 'first test message' in content or 'hello! i am the ai response' in content or 'this is a real test message from python' in content:
        test_message_ids.append(msg['id'])

if test_message_ids:
    print(f"\n🗑️  Found {len(test_message_ids)} test messages to delete:")
    for msg_id in test_message_ids:
        msg = next(m for m in messages if m['id'] == msg_id)
        preview = msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content']
        print(f"   {msg_id}. [{msg['role']}] {preview}")
    
    confirm = input("\n⚠️  Delete these messages? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        # Delete test messages
        placeholders = ','.join('?' * len(test_message_ids))
        cursor.execute(f"DELETE FROM messages WHERE id IN ({placeholders})", test_message_ids)
        conn.commit()
        
        print(f"\n✅ Deleted {len(test_message_ids)} test messages")
        
        # Show remaining messages
        sql, params = convert_sql_placeholders("SELECT id, role, content FROM messages WHERE thread_id = ? ORDER BY created_at", (thread_id,))

        cursor.execute(sql, params)
        remaining = cursor.fetchall()
        
        print(f"\n📊 Remaining messages ({len(remaining)}):")
        for msg in remaining:
            preview = msg['content'][:70] + '...' if len(msg['content']) > 70 else msg['content']
            print(f"   {msg['id']}. [{msg['role']}] {preview}")
    else:
        print("\n❌ Cancelled")
else:
    print("\n✅ No test messages found to delete")

conn.close()

print("\n" + "="*60)
print("DONE")
print("="*60)
