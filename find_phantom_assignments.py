"""
Find where the phantom thread assignments are actually stored
"""

import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent

# Check ai_infrastructure.db
print("="*60)
print("CHECKING AI_INFRASTRUCTURE.DB")
print("="*60)
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Check users table metadata
print("\n1. Users table metadata:")
cursor.execute("SELECT id, email, metadata FROM users WHERE id = 12")
user = cursor.fetchone()
if user and user['metadata']:
    metadata = json.loads(user['metadata'])
    print(f"   User: {user['email']}")
    print(f"   Raw metadata: {user['metadata'][:200]}...")
    if 'thread_assignments' in metadata:
        print(f"   thread_assignments: {metadata['thread_assignments']}")
    else:
        print("   No thread_assignments key in metadata")
else:
    print("   No metadata found")

# 2. Check user_sessions table structure first
print("\n2. User_sessions table:")
cursor.execute("PRAGMA table_info(user_sessions)")
cols = cursor.fetchall()
col_names = [col['name'] for col in cols]
print(f"   Columns: {col_names}")

cursor.execute("""
    SELECT * 
    FROM user_sessions 
    WHERE user_id = 12 
    ORDER BY created_at DESC 
    LIMIT 5
""")
sessions = cursor.fetchall()
print(f"   Found {len(sessions)} sessions for user_id=12")
for session in sessions:
    if 'metadata' in dict(session).keys() and session['metadata']:
        try:
            meta = json.loads(session['metadata'])
            if 'thread_assignments' in meta:
                print(f"   [FOUND] id={session['id']}")
                print(f"   thread_assignments: {meta['thread_assignments']}")
        except:
            pass

# 3. Check threads.location (primary source per architectural decision)
print("\n3. Thread locations (from threads.location in sessions.db):")
sessions_conn = sqlite3.connect(str(root_dir / 'data' / 'sessions.db'))
sessions_conn.row_factory = sqlite3.Row
sessions_cursor = sessions_conn.cursor()
sessions_cursor.execute("""
    SELECT id, thread_slug, name, location 
    FROM threads 
    WHERE location IS NOT NULL AND location != 'prime'
    ORDER BY updated_at DESC
""")
thread_locations = sessions_cursor.fetchall()
print(f"   Found {len(thread_locations)} threads with agent assignments")
for row in thread_locations:
    print(f"   - thread_slug: {row['thread_slug']}, name: {row['name']}, location: {row['location']}")

conn.close()

# Check sessions.db
print("\n" + "="*60)
print("CHECKING SESSIONS.DB")
print("="*60)
db_path = root_dir / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Check sessions table metadata
print("\n1. Sessions table:")
cursor.execute("""
    SELECT session_id, metadata, created_at 
    FROM sessions 
    ORDER BY created_at DESC 
    LIMIT 10
""")
sessions = cursor.fetchall()
print(f"   Found {len(sessions)} recent sessions")
for session in sessions[:5]:
    if session['metadata']:
        try:
            meta = json.loads(session['metadata'])
            if 'thread_assignments' in meta:
                print(f"   [FOUND] session_id={session['session_id']}")
                print(f"   thread_assignments: {meta['thread_assignments']}")
        except:
            pass

# 2. Check users table
print("\n2. Users table in sessions.db:")
cursor.execute("SELECT id, username, metadata FROM users WHERE id = 12")
user = cursor.fetchone()
if user:
    print(f"   User: {user['username']}")
    if user['metadata']:
        try:
            metadata = json.loads(user['metadata'])
            print(f"   Raw metadata keys: {list(metadata.keys())}")
            if 'thread_assignments' in metadata:
                print(f"   thread_assignments: {metadata['thread_assignments']}")
        except Exception as e:
            print(f"   Error parsing metadata: {e}")
    else:
        print("   No metadata")
else:
    print("   User 12 not found")

conn.close()

print("\n" + "="*60)
print("DONE")
print("="*60)
