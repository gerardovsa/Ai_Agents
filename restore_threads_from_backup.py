"""
Restore threads and messages from backup to current sessions.db

This script safely copies:
1. Threads from backup
2. Messages from backup
3. Preserves all relationships (thread_id linkage)

Safe approach:
- Reads from backup (read-only)
- Inserts into current db (won't break existing data)
- Handles ID conflicts gracefully
- Preserves message-to-thread relationships
"""

import sqlite3
from pathlib import Path
from datetime import datetime

root_dir = Path(__file__).parent
backup_db = root_dir / 'data' / 'sessions_corrupted_backup.db'
current_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("RESTORING THREADS FROM BACKUP")
print("=" * 80)
print(f"\nBackup: {backup_db.name}")
print(f"Target: {current_db.name}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connect to both databases
backup_conn = sqlite3.connect(str(backup_db))
backup_conn.row_factory = sqlite3.Row
backup_cursor = backup_conn.cursor()

current_conn = sqlite3.connect(str(current_db))
current_cursor = current_conn.cursor()

# Get threads from backup
print("📋 Step 1: Reading threads from backup...")
backup_cursor.execute("""
    SELECT id, thread_slug, workspace_id, user_id, name, 
           created_at, updated_at, metadata, location, tags, 
           synergy_card_id, parent_thread_id, branch_name, archived
    FROM threads
    ORDER BY created_at
""")

threads = backup_cursor.fetchall()
print(f"Found {len(threads)} threads in backup\n")

# Display threads
for thread in threads:
    print(f"  - {thread['thread_slug']} : {thread['name']} (location: {thread['location']})")

# Get messages from backup
print(f"\n💬 Step 2: Reading messages from backup...")
backup_cursor.execute("SELECT COUNT(*) FROM messages")
message_count = backup_cursor.fetchone()[0]
print(f"Found {message_count} messages in backup\n")

# Confirm before proceeding
print("=" * 80)
print("READY TO RESTORE")
print("=" * 80)
print(f"\nWill copy:")
print(f"  ✓ {len(threads)} threads")
print(f"  ✓ {message_count} messages")
print("\nThis operation:")
print("  ✓ Will NOT delete existing data")
print("  ✓ Will handle ID conflicts safely")
print("  ✓ Will preserve thread-message relationships")
print("\nProceeding in 2 seconds...")

import time
time.sleep(2)

print("\n" + "=" * 80)
print("COPYING DATA")
print("=" * 80)

# Create mapping of old thread IDs to new thread IDs (in case of conflicts)
thread_id_map = {}
threads_copied = 0
threads_skipped = 0

print("\n📋 Copying threads...")
for thread in threads:
    try:
        # Check if thread_slug already exists
        current_cursor.execute(
            "SELECT id FROM threads WHERE thread_slug = ?", 
            [thread['thread_slug']]
        )
        existing = current_cursor.fetchone()
        
        if existing:
            print(f"  ⚠️  Thread {thread['thread_slug']} already exists, skipping")
            thread_id_map[thread['id']] = existing[0]
            threads_skipped += 1
            continue
        
        # Insert thread (let SQLite auto-generate new ID)
        current_cursor.execute("""
            INSERT INTO threads (
                thread_slug, workspace_id, user_id, name, 
                created_at, updated_at, metadata, location, tags,
                synergy_card_id, parent_thread_id, branch_name, archived,
                branch_point_message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """, (
            thread['thread_slug'],
            thread['workspace_id'],
            thread['user_id'],
            thread['name'],
            thread['created_at'],
            thread['updated_at'],
            thread['metadata'],
            thread['location'],
            thread['tags'],
            thread['synergy_card_id'],
            thread['parent_thread_id'],
            thread['branch_name'],
            thread['archived']
        ))
        
        new_id = current_cursor.lastrowid
        thread_id_map[thread['id']] = new_id
        
        print(f"  ✅ {thread['thread_slug']} : {thread['name']}")
        threads_copied += 1
        
    except Exception as e:
        print(f"  ❌ Error copying thread {thread['thread_slug']}: {e}")
        threads_skipped += 1

current_conn.commit()

print(f"\n✅ Threads copied: {threads_copied}")
print(f"⚠️  Threads skipped: {threads_skipped}")

# Now copy messages using the thread_id_map
print(f"\n💬 Copying messages...")

backup_cursor.execute("""
    SELECT id, thread_id, role, content, timestamp, tool_calls
    FROM messages
    ORDER BY timestamp
""")

messages = backup_cursor.fetchall()
messages_copied = 0
messages_skipped = 0

for msg in messages:
    try:
        # Map old thread_id to new thread_id
        old_thread_id = msg['thread_id']
        
        if old_thread_id not in thread_id_map:
            # Thread wasn't copied, skip message
            messages_skipped += 1
            continue
        
        new_thread_id = thread_id_map[old_thread_id]
        
        # Insert message with new thread_id (only common columns)
        current_cursor.execute("""
            INSERT INTO messages (
                thread_id, role, content, timestamp, tool_calls
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            new_thread_id,
            msg['role'],
            msg['content'],
            msg['timestamp'],
            msg['tool_calls']
        ))
        
        messages_copied += 1
        
        # Show progress every 10 messages
        if messages_copied % 10 == 0:
            print(f"  ... {messages_copied} messages copied")
        
    except Exception as e:
        print(f"  ❌ Error copying message {msg['id']}: {e}")
        messages_skipped += 1

current_conn.commit()

print(f"\n✅ Messages copied: {messages_copied}")
print(f"⚠️  Messages skipped: {messages_skipped}")

# Verify the restore
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

current_cursor.execute("SELECT COUNT(*) FROM threads")
thread_count = current_cursor.fetchone()[0]

current_cursor.execute("SELECT COUNT(*) FROM messages")
message_count = current_cursor.fetchone()[0]

print(f"\n📊 Current database now has:")
print(f"  Threads: {thread_count}")
print(f"  Messages: {message_count}")

# Show sample threads
current_cursor.execute("""
    SELECT thread_slug, name, location, 
           (SELECT COUNT(*) FROM messages WHERE thread_id = threads.id) as msg_count
    FROM threads
    ORDER BY created_at DESC
    LIMIT 10
""")

print(f"\n📋 Recent threads with message counts:")
for row in current_cursor.fetchall():
    print(f"  - {row[0]} : {row[1]} (location: {row[2]}, messages: {row[3]})")

# Close connections
backup_conn.close()
current_conn.close()

print("\n" + "=" * 80)
print("RESTORE COMPLETE!")
print("=" * 80)
print(f"\n✅ Successfully restored:")
print(f"   {threads_copied} threads")
print(f"   {messages_copied} messages")
print(f"\n💡 Flask server should now show all restored threads and messages!")
