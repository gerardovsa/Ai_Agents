"""
Check what threads exist and which one might be assigned to agent-2
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("="*80)
print("ALL THREADS IN SESSIONS.DB")
print("="*80)

conn = sqlite3.connect(sessions_db)
cursor = conn.cursor()

# Get all threads
sql, params = convert_sql_placeholders("""
    SELECT id, thread_slug, name, user_id, location, created_at
    FROM threads
    ORDER BY id DESC
    LIMIT 20
""")

threads = cursor.fetchall()

print(f"\nFound {len(threads)} threads (showing last 20):")
print("-" * 80)

for row in threads:
    # Count messages for this thread
    sql, params = convert_sql_placeholders("SELECT COUNT(*) FROM messages WHERE thread_id = ?", (row[0],))

    cursor.execute(sql, params)
    msg_count = cursor.fetchone()[0]
    
    print(f"\nThread ID: {row[0]}")
    print(f"  Slug: {row[1]}")
    print(f"  Name: {row[2]}")
    print(f"  User: {row[3]}")
    print(f"  Location: {row[4]}")
    print(f"  Created: {row[5]}")
    print(f"  Messages: {msg_count}")

# Check the backend assignments format
print("\n" + "="*80)
print("WHAT IS '1762411564661'?")
print("="*80)

# This looks like a timestamp
import time
from datetime import datetime

timestamp = 1762411564661
# Try as milliseconds
dt_ms = datetime.fromtimestamp(timestamp / 1000)
print(f"\nAs milliseconds timestamp: {dt_ms}")

# Try as seconds
try:
    dt_s = datetime.fromtimestamp(timestamp)
    print(f"As seconds timestamp: {dt_s}")
except:
    print("Not a valid seconds timestamp")

# Check if any thread has this in metadata or as a slug
cursor.execute("""
    SELECT id, thread_slug, name, metadata, location
    FROM threads
    WHERE thread_slug LIKE '%1762411564661%'
       OR metadata LIKE '%1762411564661%'
""")

matching = cursor.fetchall()
if matching:
    print(f"\n✅ Found threads matching '1762411564661':")
    for row in matching:
        print(f"  Thread {row[0]}: {row[1]} - {row[2]} (location: {row[4]})")
else:
    print(f"\n⚠️  No threads found with '1762411564661' in slug or metadata")

# Check thread_assignments in ai_infrastructure.db
print("\n" + "="*80)
print("THREAD ASSIGNMENTS (ai_infrastructure.db)")
print("="*80)

ai_db = root_dir / 'data' / 'ai_infrastructure.db'
ai_conn = sqlite3.connect(ai_db)
ai_cursor = ai_conn.cursor()

ai_cursor.execute("""
    SELECT id, user_id, session_id, location, created_at
    FROM thread_assignments
    ORDER BY created_at DESC
""")

assignments = ai_cursor.fetchall()

if assignments:
    print(f"\nFound {len(assignments)} thread assignments:")
    for row in assignments:
        print(f"\n  Assignment {row[0]}:")
        print(f"    User: {row[1]}")
        print(f"    Session/Thread ID: {row[2]}")
        print(f"    Location: {row[3]}")
        print(f"    Created: {row[4]}")
        
        # Check if this thread exists in sessions.db
        cursor.execute("""
            SELECT id, name FROM threads 
            WHERE id = ? OR thread_slug = ?
        """, (row[2], row[2]))

cursor.execute(sql, params)
        
        thread_match = cursor.fetchone()
        if thread_match:
            print(f"    → Links to: Thread {thread_match[0]} - {thread_match[1]}")
        else:
            print(f"    → ⚠️  Thread not found in sessions.db!")
else:
    print("\n  No thread assignments found")

ai_conn.close()

# Check sessions table (old system)
print("\n" + "="*80)
print("SESSIONS TABLE (old session system)")
print("="*80)

cursor.execute("""
    SELECT session_id, ui_context, agent_id, created_at
    FROM sessions
    ORDER BY created_at DESC
    LIMIT 10
""")

sessions = cursor.fetchall()
print(f"\nFound {len(sessions)} sessions (showing 10):")
for row in sessions:
    print(f"  {row[0]} - {row[1]} (agent: {row[2]}) - {row[3]}")

conn.close()

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)
print("""
The ID '1762411564661' appears to be:
  - A milliseconds timestamp (Nov 5, 2025 ~7:46 PM)
  - Possibly a session_id from the old sessions table
  - NOT a thread ID from the threads table
  
The backend is showing this as assigned to 'agent-2' but:
  - No thread_assignments record exists for agent-2
  - No thread in threads table matches this ID
  - This is likely a frontend-only assignment (localStorage)
  
RECOMMENDATION:
  Check the frontend localStorage for 'threadAssignments' to see
  where this mapping is coming from.
""")
