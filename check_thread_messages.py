"""
Check thread and message counts in sessions.db
"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / 'data' / 'sessions.db'

if not db_path.exists():
    print(f"❌ Database not found at: {db_path}")
    exit(1)

print(f"📂 Checking database: {db_path}\n")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check threads table
print("=" * 80)
print("THREADS TABLE")
print("=" * 80)

cursor.execute("""
    SELECT id, thread_slug, name, location, created_at, updated_at
    FROM threads
    ORDER BY created_at DESC
    LIMIT 10
""")

threads = cursor.fetchall()
print(f"Total threads in database: {len(threads)}")
print(f"\nFirst 10 threads:\n")

for thread in threads:
    print(f"  ID: {thread['id']}")
    print(f"  Slug: {thread['thread_slug']}")
    print(f"  Name: {thread['name']}")
    print(f"  Location: {thread['location']}")
    print(f"  Created: {thread['created_at']}")
    print(f"  Updated: {thread['updated_at']}")
    
    # Count messages for this thread
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM messages 
        WHERE thread_id = ?
    """, (thread['id'],))
    msg_count = cursor.fetchone()['count']
    print(f"  📊 Messages: {msg_count}")
    print()

# Check messages table
print("\n" + "=" * 80)
print("MESSAGES TABLE")
print("=" * 80)

cursor.execute("SELECT COUNT(*) as count FROM messages")
total_messages = cursor.fetchone()['count']
print(f"Total messages in database: {total_messages}\n")

if total_messages > 0:
    # Show message distribution by thread_id
    cursor.execute("""
        SELECT thread_id, COUNT(*) as count
        FROM messages
        GROUP BY thread_id
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("Message distribution by thread_id:")
    for row in cursor.fetchall():
        print(f"  Thread ID {row['thread_id']}: {row['count']} messages")
    
    # Show recent messages
    print("\n" + "=" * 80)
    print("RECENT MESSAGES (last 5)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT id, thread_id, role, 
               substr(content, 1, 50) as content_preview,
               tokens_used, response_time_ms,
               created_at
        FROM messages
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    for msg in cursor.fetchall():
        print(f"\n  Message ID: {msg['id']}")
        print(f"  Thread ID: {msg['thread_id']}")
        print(f"  Role: {msg['role']}")
        print(f"  Content: {msg['content_preview']}...")
        print(f"  Tokens: {msg['tokens_used']}")
        print(f"  Response Time: {msg['response_time_ms']}ms")
        print(f"  Created: {msg['created_at']}")

# Check thread-message linkage
print("\n" + "=" * 80)
print("THREAD-MESSAGE LINKAGE CHECK")
print("=" * 80)

cursor.execute("""
    SELECT 
        (SELECT COUNT(*) FROM threads) as thread_count,
        (SELECT COUNT(*) FROM messages) as message_count,
        (SELECT COUNT(DISTINCT thread_id) FROM messages) as threads_with_messages
""")

stats = cursor.fetchone()
print(f"Threads in database: {stats['thread_count']}")
print(f"Messages in database: {stats['message_count']}")
print(f"Threads with messages: {stats['threads_with_messages']}")

if stats['threads_with_messages'] == 0 and stats['message_count'] > 0:
    print("\n⚠️  WARNING: Messages exist but aren't linked to any threads!")
    print("   This means thread_id values in messages don't match threads.id")
    
    # Show what thread_id values exist in messages
    cursor.execute("""
        SELECT DISTINCT thread_id 
        FROM messages 
        LIMIT 10
    """)
    
    print("\n   Thread IDs found in messages table:")
    for row in cursor.fetchall():
        print(f"     - {row['thread_id']}")
    
    print("\n   Thread IDs found in threads table:")
    cursor.execute("SELECT id FROM threads LIMIT 10")
    for row in cursor.fetchall():
        print(f"     - {row['id']}")

conn.close()

print("\n" + "=" * 80)
print("✅ Check complete")
print("=" * 80)
