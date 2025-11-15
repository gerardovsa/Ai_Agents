"""Clean ALL duplicate messages from the database"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("="*60)
print("CLEANING ALL DUPLICATE MESSAGES")
print("="*60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all threads
cursor.execute("SELECT id, thread_slug, name FROM threads")
threads = cursor.fetchall()

print(f"\nFound {len(threads)} threads\n")

total_deleted = 0

for thread in threads:
    thread_id, thread_slug, name = thread
    
    # Get all messages for this thread
    cursor.execute("""
        SELECT id, role, content, created_at 
        FROM messages 
        WHERE thread_id = ? 
        ORDER BY created_at
    """, (thread_id,))
    messages = cursor.fetchall()
    
    if len(messages) == 0:
        continue
    
    print(f"Thread: {name} ({thread_slug})")
    print(f"  Messages: {len(messages)}")
    
    # Find duplicates (same role + content)
    seen = {}
    to_delete = []
    
    for msg_id, role, content, created_at in messages:
        # Use role + first 200 chars of content as key
        key = (role, content[:200])
        
        if key in seen:
            # This is a duplicate - mark for deletion (keep the oldest one)
            to_delete.append(msg_id)
        else:
            # First occurrence - keep it
            seen[key] = (msg_id, created_at)
    
    if to_delete:
        print(f"  Duplicates found: {len(to_delete)}")
        placeholders = ','.join('?' * len(to_delete))
        cursor.execute(f"DELETE FROM messages WHERE id IN ({placeholders})", to_delete)
        total_deleted += len(to_delete)
        print(f"  ✅ Deleted {len(to_delete)} duplicates")
    else:
        print(f"  ✅ No duplicates")

conn.commit()
conn.close()

print("\n" + "="*60)
print(f"TOTAL DUPLICATES DELETED: {total_deleted}")
print("="*60)
print("\n✅ Database cleaned! Restart Flask and refresh browser.")
