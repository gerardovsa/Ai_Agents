"""
Explain the difference between thread id and thread_slug
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("="*60)
print("THREAD ID vs THREAD_SLUG")
print("="*60)

# 1. Show table structure
print("\n1. THREADS TABLE STRUCTURE:")
cursor.execute("PRAGMA table_info(threads)")
cols = cursor.fetchall()

for col in cols:
    pk_marker = " [PRIMARY KEY]" if col['pk'] else ""
    print(f"   - {col['name']}: {col['type']}{pk_marker}")

# 2. Show example data
print("\n2. EXAMPLE DATA:")
cursor.execute("SELECT id, thread_slug, name, user_id, created_at FROM threads LIMIT 5")
threads = cursor.fetchall()

if not threads:
    print("   (no threads)")
else:
    for thread in threads:
        print(f"\n   Thread: {thread['name']}")
        print(f"     - id (database ID):  {thread['id']} ← Sequential, internal use only")
        print(f"     - thread_slug:       {thread['thread_slug']} ← Unique ID for frontend/API")
        print(f"     - user_id:          {thread['user_id']}")
        print(f"     - created:          {thread['created_at']}")

conn.close()

print("\n" + "="*60)
print("EXPLANATION")
print("="*60)

print("""
┌─────────────────────────────────────────────────────────┐
│ FIELD        │ PURPOSE                    │ EXAMPLE    │
├─────────────────────────────────────────────────────────┤
│ id           │ Database primary key       │ 1, 2, 3... │
│ (INTEGER)    │ Sequential auto-increment  │ (internal) │
│              │ Used for JOINs with        │            │
│              │ messages table             │            │
├─────────────────────────────────────────────────────────┤
│ thread_slug  │ Public-facing unique ID    │ 176261478… │
│ (TEXT)       │ Timestamp-based            │ (external) │
│              │ Used by frontend/API       │            │
│              │ Safe to expose to users    │            │
└─────────────────────────────────────────────────────────┘

WHY TWO IDS?
============

1. **id (Database ID)**
   - Sequential: 1, 2, 3, 4...
   - Used internally for database relationships
   - NOT exposed in UI (security/privacy)
   - Fast for JOINs and indexes

2. **thread_slug (Public ID)**
   - Timestamp-based: 1762614784052 (milliseconds since epoch)
   - Used in URLs and frontend
   - Safe to expose to users
   - Unique and unpredictable
   - Compatible with localStorage/session IDs

CURRENT ISSUE IN YOUR UI:
=========================

Your screenshot showed "#1" which is displaying the **database ID** 
instead of the **thread_slug**. 

The database ID is just a sequential counter (1, 2, 3...) and should 
NOT be shown to users. Instead, you should see:

  ✅ CORRECT: # 1762614784052 (thread_slug)
  ❌ WRONG:   # 1 (database id)

This has been fixed in the code to use thread.id (which maps to 
thread_slug) instead of thread.thread_id (which maps to database id).
""")
