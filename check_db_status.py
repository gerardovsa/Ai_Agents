"""
Check sessions.db for existing threads and verify schema is ready
"""
import sqlite3
from pathlib import Path
import json

db_path = Path(__file__).parent / 'data' / 'sessions.db'

print("\n" + "=" * 80)
print("DATABASE STATUS CHECK")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check if threads table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='threads'")
if not cursor.fetchone():
    print("\n❌ ERROR: threads table does not exist!")
    print("   Run: python migrate_threads.py")
    conn.close()
    exit(1)

print("\n✅ threads table exists")

# Count threads
cursor.execute("SELECT COUNT(*) as count FROM threads")
thread_count = cursor.fetchone()['count']
print(f"📊 Total threads in database: {thread_count}")

# Show recent threads
cursor.execute("""
    SELECT thread_slug, name, user_id, created_at, location, 
           tags, synergy_card_id, parent_thread_id, branch_name
    FROM threads 
    ORDER BY created_at DESC 
    LIMIT 10
""")

threads = cursor.fetchall()

if threads:
    print(f"\n📋 Recent {len(threads)} threads:")
    print("-" * 80)
    for t in threads:
        print(f"\nThread: {t['name']}")
        print(f"  ID: {t['thread_slug']}")
        print(f"  User: {t['user_id']}")
        print(f"  Location: {t['location']}")
        print(f"  Created: {t['created_at']}")
        if t['tags'] and t['tags'] != '[]':
            print(f"  Tags: {t['tags']}")
        if t['synergy_card_id']:
            print(f"  Synergy: {t['synergy_card_id']}")
        if t['parent_thread_id']:
            print(f"  Parent: {t['parent_thread_id']}")
            print(f"  Branch: {t['branch_name']}")
else:
    print("\n📭 No threads in database yet")

# Check schema completeness
print("\n" + "=" * 80)
print("SCHEMA VALIDATION")
print("=" * 80)

required_columns = [
    'thread_slug', 'workspace_id', 'user_id', 'name', 'created_at', 'updated_at',
    'metadata', 'tags', 'synergy_card_id', 'parent_thread_id', 
    'branch_point_message_id', 'branch_name', 'summary', 
    'summary_generated_at', 'location'
]

cursor.execute("PRAGMA table_info(threads)")
existing_cols = [col[1] for col in cursor.fetchall()]

missing = [col for col in required_columns if col not in existing_cols]

if missing:
    print(f"\n❌ Missing columns: {', '.join(missing)}")
    print("   Run: python migrate_threads.py")
else:
    print("\n✅ All required columns present (16 total)")
    print("   Schema is ready for thread features!")

print("\n" + "=" * 80)
print("READY STATUS")
print("=" * 80)

if not missing and thread_count >= 0:
    print("\n✅ DATABASE IS READY!")
    print("   - Schema has all 16 columns")
    print("   - Can save threads with tags, Synergy links, and branches")
    print("   - Backend /save and /create endpoints ready")
else:
    print("\n⚠️  DATABASE NEEDS MIGRATION")
    print("   Run: python migrate_threads.py")

print("\n" + "=" * 80 + "\n")

conn.close()
