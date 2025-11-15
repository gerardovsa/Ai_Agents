"""
Check specific thread ID: 1762592718945
"""

import sqlite3
from pathlib import Path
import json

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

thread_id = '1762592718945'

print("="*80)
print(f"CHECKING THREAD ID: {thread_id}")
print("="*80)

conn = sqlite3.connect(sessions_db)
cursor = conn.cursor()

# Check threads table
print("\n1. THREADS TABLE:")
print("-" * 80)
cursor.execute("""
    SELECT id, thread_slug, name, user_id, location, created_at, metadata, 
           tags, synergy_card_id, parent_thread_id
    FROM threads
    WHERE id = ? OR thread_slug = ?
""", (thread_id, thread_id))

thread = cursor.fetchone()

if thread:
    print(f"✅ Thread Found!")
    print(f"  Internal ID: {thread[0]}")
    print(f"  Thread Slug: {thread[1]}")
    print(f"  Name: {thread[2]}")
    print(f"  User ID: {thread[3]}")
    print(f"  Location: {thread[4]}")
    print(f"  Created: {thread[5]}")
    print(f"  Metadata: {thread[6]}")
    print(f"  Tags: {thread[7]}")
    print(f"  Synergy Card: {thread[8]}")
    print(f"  Parent Thread: {thread[9]}")
    
    internal_id = thread[0]
else:
    print(f"❌ Thread NOT found in threads table")
    internal_id = None

# Check messages
print(f"\n2. MESSAGES FOR THREAD {thread_id}:")
print("-" * 80)

if internal_id:
    cursor.execute("""
        SELECT id, role, content, created_at, tool_calls, tokens_used, response_time_ms
        FROM messages
        WHERE thread_id = ?
        ORDER BY created_at ASC
    """, (internal_id,))
    
    messages = cursor.fetchall()
    
    if messages:
        print(f"✅ Found {len(messages)} messages:")
        for i, msg in enumerate(messages, 1):
            print(f"\n  Message {i}:")
            print(f"    ID: {msg[0]}")
            print(f"    Role: {msg[1]}")
            print(f"    Content Preview: {msg[2][:150]}...")
            print(f"    Created: {msg[3]}")
            print(f"    Tool Calls: {msg[4]}")
            print(f"    Tokens: {msg[5]}")
            print(f"    Response Time: {msg[6]}ms")
    else:
        print(f"  ⚠️  No messages found for internal ID {internal_id}")

# Also check by session_id
cursor.execute("""
    SELECT COUNT(*) FROM messages WHERE session_id = ?
""", (thread_id,))
session_msg_count = cursor.fetchone()[0]

if session_msg_count > 0:
    print(f"\n  ℹ️  Found {session_msg_count} messages with session_id = {thread_id}")

# Check saved_threads
print(f"\n3. SAVED_THREADS TABLE:")
print("-" * 80)

cursor.execute("""
    SELECT thread_id, thread_name, message_count, conversation, saved_at
    FROM saved_threads
    WHERE thread_id LIKE '%' || ? || '%'
    ORDER BY saved_at DESC
    LIMIT 5
""", (thread_id,))

saved = cursor.fetchall()

if saved:
    print(f"✅ Found {len(saved)} saved thread(s):")
    for row in saved:
        print(f"\n  Thread ID: {row[0]}")
        print(f"    Name: {row[1]}")
        print(f"    Message Count: {row[2]}")
        print(f"    Saved At: {row[4]}")
        
        # Parse conversation
        try:
            conv = json.loads(row[3])
            print(f"    Conversation Messages: {len(conv)}")
            if conv:
                print(f"    Sample Message: {conv[0].get('role', 'unknown')}: {conv[0].get('content', '')[:100]}...")
        except:
            print(f"    Conversation: [Unable to parse]")
else:
    print(f"  ⚠️  No saved threads found")

conn.close()

# Convert timestamp
from datetime import datetime
try:
    ts_ms = int(thread_id)
    dt = datetime.fromtimestamp(ts_ms / 1000)
    print(f"\n4. TIMESTAMP INFO:")
    print("-" * 80)
    print(f"  As milliseconds: {dt}")
    print(f"  Date: {dt.strftime('%Y-%m-%d')}")
    print(f"  Time: {dt.strftime('%H:%M:%S')}")
except:
    print(f"\n4. Not a valid timestamp")

print("\n" + "="*80)
