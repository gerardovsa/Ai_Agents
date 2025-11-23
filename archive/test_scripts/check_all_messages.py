"""
Check ALL messages in sessions.db regardless of thread
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("ALL MESSAGES CHECK")
print("="*60)
print(f"\nDatabase: {db_path}\n")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Check ALL messages (any thread)
print("1. ALL MESSAGES IN DATABASE:")
sql, params = convert_sql_placeholders("""
    SELECT id, thread_id, session_id, role, 
           substr(content, 1, 80) as content_preview,
           created_at
    FROM messages
    ORDER BY created_at DESC
    LIMIT 20
""")
messages = cursor.fetchall()

if not messages:
    print("   ❌ No messages in database at all")
else:
    print(f"   ✅ Found {len(messages)} message(s):")
    for msg in messages:
        print(f"\n   Message ID: {msg['id']}")
        print(f"   Thread ID: {msg['thread_id']}")
        print(f"   Session ID: {msg['session_id']}")
        print(f"   Role: {msg['role']}")
        print(f"   Time: {msg['created_at']}")
        print(f"   Content: {msg['content_preview']}...")

# 2. Check ALL threads
print("\n2. ALL THREADS:")
cursor.execute("""
    SELECT id, thread_slug, name, user_id, location, created_at
    FROM threads
    ORDER BY created_at DESC
    LIMIT 10
""")
threads = cursor.fetchall()

print(f"   Found {len(threads)} thread(s):")
for thread in threads:
    print(f"   - ID: {thread['id']}, Slug: {thread['thread_slug']}, Name: {thread['name']}, Location: {thread['location']}")
    
    # Count messages for this thread
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM messages
        WHERE thread_id = ? OR session_id = ?
    """, (thread['id'], thread['thread_slug']))

cursor.execute(sql, params)
    count = cursor.fetchone()['count']
    print(f"     Messages: {count}")

# 3. Check sessions table
print("\n3. ALL SESSIONS:")
cursor.execute("""
    SELECT session_id, agent_id, created_at, last_active,
           length(conversation) as conv_length
    FROM sessions
    ORDER BY created_at DESC
    LIMIT 10
""")
sessions = cursor.fetchall()

if not sessions:
    print("   ❌ No sessions found")
else:
    print(f"   ✅ Found {len(sessions)} session(s):")
    for session in sessions:
        print(f"   - ID: {session['session_id']}, Agent: {session['agent_id']}, Conversation length: {session['conv_length']} bytes")

conn.close()

print("\n" + "="*60)
print("ANALYSIS")
print("="*60)

if len(messages) == 0 and len(threads) > 0:
    print("\n⚠️  ISSUE DETECTED:")
    print("   - Threads exist but NO messages are being saved")
    print("   - This suggests the message saving endpoint might not be working")
    print("\n💡 POSSIBLE CAUSES:")
    print("   1. Messages stored in memory only (not persisted)")
    print("   2. Different database being used")
    print("   3. Message save endpoint not being called")
    print("\n🔍 CHECK:")
    print("   - Browser console for save errors")
    print("   - Flask logs for message save attempts")
elif len(messages) > 0:
    print(f"\n✅ Messages are being saved correctly!")
    print(f"   Total messages in database: {len(messages)}")
