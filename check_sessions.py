"""
Check sessions for printing@inhouseprint.com.au
"""
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 80)
print("SESSIONS FOR printing@inhouseprint.com.au")
print("=" * 80)

# First, find the user_id for this email
cursor.execute("""
    SELECT id, email, username, created_at 
    FROM users 
    WHERE email = 'printing@inhouseprint.com.au'
""")
user = cursor.fetchone()

if not user:
    print("\n❌ No user found with email: printing@inhouseprint.com.au")
    conn.close()
    exit()

user_id, email, username, created_at = user
print(f"\n✅ User found:")
print(f"   ID: {user_id}")
print(f"   Email: {email}")
print(f"   Username: {username}")
print(f"   Created: {created_at}")

# Check sessions.db
print("\n" + "=" * 80)
print("CHECKING sessions.db")
print("=" * 80)

try:
    sessions_conn = sqlite3.connect('data/sessions.db')
    sessions_cursor = sessions_conn.cursor()
    
    sessions_cursor.execute("""
        SELECT session_id, user_id, created_at, last_accessed, data
        FROM sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (user_id,))
    
    sessions = sessions_cursor.fetchall()
    
    if sessions:
        print(f"\n✅ Found {len(sessions)} sessions:\n")
        for i, (session_id, uid, created, accessed, data) in enumerate(sessions, 1):
            print(f"{i}. Session ID: {session_id}")
            print(f"   Created: {created}")
            print(f"   Last Accessed: {accessed}")
            print(f"   Data length: {len(data) if data else 0} bytes")
            print()
    else:
        print(f"\n⚠️ No sessions found in sessions.db for user_id {user_id}")
    
    sessions_conn.close()
except Exception as e:
    print(f"\n❌ Error checking sessions.db: {e}")

# Check ai_infrastructure.db for conversation sessions
print("=" * 80)
print("CHECKING ai_infrastructure.db - conversation_sessions")
print("=" * 80)

cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE '%session%'
""")
session_tables = cursor.fetchall()

print(f"\nSession-related tables: {[t[0] for t in session_tables]}")

# Try to find conversation sessions
try:
    cursor.execute("""
        SELECT session_id, user_id, agent_id, created_at, updated_at, message_count
        FROM conversation_sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (user_id,))
    
    conv_sessions = cursor.fetchall()
    
    if conv_sessions:
        print(f"\n✅ Found {len(conv_sessions)} conversation sessions:\n")
        for i, (sess_id, uid, agent_id, created, updated, msg_count) in enumerate(conv_sessions, 1):
            print(f"{i}. Session ID: {sess_id}")
            print(f"   Agent ID: {agent_id}")
            print(f"   Created: {created}")
            print(f"   Updated: {updated}")
            print(f"   Messages: {msg_count}")
            print()
    else:
        print(f"\n⚠️ No conversation sessions found for user_id {user_id}")
except Exception as e:
    print(f"\n⚠️ conversation_sessions table doesn't exist or error: {e}")

# Check for threads
print("=" * 80)
print("CHECKING threads table")
print("=" * 80)

try:
    cursor.execute("""
        SELECT thread_id, title, created, updated, message_count, archived
        FROM threads
        WHERE user_id = ?
        ORDER BY created DESC
        LIMIT 20
    """, (user_id,))
    
    threads = cursor.fetchall()
    
    if threads:
        print(f"\n✅ Found {len(threads)} threads:\n")
        for i, (thread_id, title, created, updated, msg_count, archived) in enumerate(threads, 1):
            print(f"{i}. Thread ID: {thread_id}")
            print(f"   Title: {title}")
            print(f"   Created: {created}")
            print(f"   Updated: {updated}")
            print(f"   Messages: {msg_count}")
            print(f"   Archived: {archived}")
            print()
    else:
        print(f"\n⚠️ No threads found for user_id {user_id}")
except Exception as e:
    print(f"\n⚠️ threads table doesn't exist or error: {e}")

# Check thread assignments
print("=" * 80)
print("CHECKING thread_assignments table")
print("=" * 80)

try:
    cursor.execute("""
        SELECT thread_id, agent_id, assigned_at
        FROM thread_assignments
        WHERE user_id = ?
        ORDER BY assigned_at DESC
        LIMIT 20
    """, (user_id,))
    
    assignments = cursor.fetchall()
    
    if assignments:
        print(f"\n✅ Found {len(assignments)} thread assignments:\n")
        for i, (thread_id, agent_id, assigned_at) in enumerate(assignments, 1):
            print(f"{i}. Thread ID: {thread_id}")
            print(f"   Agent ID: {agent_id}")
            print(f"   Assigned: {assigned_at}")
            print()
    else:
        print(f"\n⚠️ No thread assignments found for user_id {user_id}")
except Exception as e:
    print(f"\n⚠️ thread_assignments table doesn't exist or error: {e}")

conn.close()

print("=" * 80)
print("DONE")
print("=" * 80)
