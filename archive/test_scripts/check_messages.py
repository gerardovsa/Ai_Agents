"""
Check messages in sessions.db for the TEST 1 thread
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("MESSAGE STORAGE CHECK")
print("="*60)
print(f"\nDatabase: {db_path}\n")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Find the TEST 1 thread
print("1. FINDING YOUR THREAD:")
sql, params = convert_sql_placeholders("""
    SELECT id, thread_slug, name, user_id, created_at, location
    FROM threads
    WHERE name LIKE '%TEST%'
    ORDER BY created_at DESC
    LIMIT 5
""")
threads = cursor.fetchall()

if not threads:
    print("   ❌ No threads found with 'TEST' in the name")
    conn.close()
    exit(0)

print(f"   Found {len(threads)} thread(s):")
for thread in threads:
    print(f"   - ID: {thread['id']}, Slug: {thread['thread_slug']}, Name: {thread['name']}, Location: {thread['location']}")

# Use the most recent thread
test_thread = threads[0]
thread_id = test_thread['id']
thread_slug = test_thread['thread_slug']

print(f"\n   Using thread: {thread_slug} (ID: {thread_id})")

# 2. Check messages table structure
print("\n2. MESSAGES TABLE STRUCTURE:")
cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()
print(f"   Columns: {[col['name'] for col in columns]}")

# 3. Find messages for this thread (check both session_id and thread_id)
print("\n3. MESSAGES IN THIS THREAD:")
cursor.execute("""
    SELECT id, thread_id, session_id, role, content, created_at, tool_calls
    FROM messages
    WHERE thread_id = ? OR session_id = ?
    ORDER BY created_at ASC
""", (thread_id, thread_slug))

cursor.execute(sql, params)
messages = cursor.fetchall()

if not messages:
    print(f"   ❌ No messages found for thread {thread_slug}")
    print(f"   (Messages are saved when you send a chat, not when creating the thread)")
else:
    print(f"   ✅ Found {len(messages)} message(s):")
    for msg in messages:
        content_preview = msg['content'][:100] if msg['content'] else "(empty)"
        print(f"\n   Message ID: {msg['id']}")
        print(f"   Role: {msg['role']}")
        print(f"   Time: {msg['created_at']}")
        print(f"   Content: {content_preview}...")
        if msg['tool_calls']:
            print(f"   Tools: {msg['tool_calls'][:50]}...")

# 4. Check sessions table
print("\n4. SESSION DATA:")
sql, params = convert_sql_placeholders("""
    SELECT session_id, agent_id, created_at, last_active, conversation
    FROM sessions
    WHERE session_id = ?
""", (thread_slug,))

cursor.execute(sql, params)
session = cursor.fetchone()

if session:
    print(f"   ✅ Session found:")
    print(f"   - session_id: {session['session_id']}")
    print(f"   - agent_id: {session['agent_id']}")
    print(f"   - created: {session['created_at']}")
    print(f"   - last_active: {session['last_active']}")
    if session['conversation']:
        conv = session['conversation']
        print(f"   - conversation length: {len(conv)} chars")
else:
    print(f"   ❌ No session data found")

conn.close()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"\n📝 Thread exists: ✅")
print(f"💬 Messages stored: {len(messages) if messages else '0 (send a message to create one)'}")
print(f"🗄️  Database location: {db_path}")
print("\n✅ Messages are saved to: data/sessions.db → messages table")
print("   Each message has: id, thread_id, session_id, role, content, created_at, tool_calls")
