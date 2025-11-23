"""
Check messages in the agent-2 assigned thread
Thread ID: 1762411564661
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("="*80)
print("CHECKING AGENT-2 THREAD ASSIGNMENT")
print("="*80)

conn = sqlite3.connect(sessions_db)
cursor = conn.cursor()

# First, check thread_assignments in ai_infrastructure.db
ai_infra_db = root_dir / 'data' / 'ai_infrastructure.db'
ai_conn = sqlite3.connect(ai_infra_db)
ai_cursor = ai_conn.cursor()

print("\n1. THREAD ASSIGNMENTS (ai_infrastructure.db):")
print("-" * 80)
ai_cursor.execute("""
    SELECT id, user_id, session_id, location, created_at
    FROM thread_assignments
    WHERE location = 'agent-2'
""")
assignments = ai_cursor.fetchall()

if assignments:
    for row in assignments:
        print(f"Assignment ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Session/Thread ID: {row[2]}")
        print(f"  Location: {row[3]}")
        print(f"  Created: {row[4]}")
        print()
else:
    print("  No thread assignments for agent-2")

ai_conn.close()

# Check for the specific thread ID
thread_id = '1762411564661'

print(f"\n2. THREAD DETAILS (sessions.db) - Thread ID: {thread_id}:")
print("-" * 80)

# Check threads table
sql, params = convert_sql_placeholders("""
    SELECT id, thread_slug, name, user_id, location, created_at, updated_at
    FROM threads
    WHERE id = ? OR thread_slug = ?
""", (thread_id, thread_id))

cursor.execute(sql, params)

thread_row = cursor.fetchone()

if thread_row:
    print(f"Thread Found:")
    print(f"  ID: {thread_row[0]}")
    print(f"  Thread Slug: {thread_row[1]}")
    print(f"  Name: {thread_row[2]}")
    print(f"  User ID: {thread_row[3]}")
    print(f"  Location: {thread_row[4]}")
    print(f"  Created: {thread_row[5]}")
    print(f"  Updated: {thread_row[6]}")
    
    thread_internal_id = thread_row[0]
else:
    print(f"  Thread {thread_id} NOT FOUND in threads table")
    thread_internal_id = None

print(f"\n3. MESSAGES FOR THREAD {thread_id}:")
print("-" * 80)

# Try multiple ways to find messages
queries = [
    ("By thread_id (INTEGER)", "SELECT COUNT(*) FROM messages WHERE thread_id = ?", (thread_id,)),
    ("By session_id (TEXT)", "SELECT COUNT(*) FROM messages WHERE session_id = ?", (thread_id,)),
]

if thread_internal_id:
    queries.append(
        ("By internal thread ID", "SELECT COUNT(*) FROM messages WHERE thread_id = ?", (thread_internal_id,))
    )

message_count_total = 0

for query_name, query, params in queries:
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    print(f"  {query_name}: {count} messages")
    message_count_total += count

if message_count_total == 0:
    print("\n  ⚠️  NO MESSAGES FOUND FOR THIS THREAD!")
    
    # Let's check what threads DO have messages
    print("\n4. THREADS WITH MESSAGES (for comparison):")
    print("-" * 80)
    sql, params = convert_sql_placeholders("""
        SELECT thread_id, COUNT(*) as msg_count
        FROM messages
        WHERE thread_id IS NOT NULL
        GROUP BY thread_id
        ORDER BY msg_count DESC
        LIMIT 10
    """)
    
    threads_with_msgs = cursor.fetchall()
    if threads_with_msgs:
        for row in threads_with_msgs:
            sql, params = convert_sql_placeholders("SELECT name FROM threads WHERE id = ?", (row[0],))

            cursor.execute(sql, params)
            thread_name = cursor.fetchone()
            name = thread_name[0] if thread_name else "Unknown"
            print(f"  Thread ID {row[0]} ({name}): {row[1]} messages")
    else:
        print("  No threads have messages linked to them")
    
    # Check for orphaned messages
    print("\n5. ORPHANED MESSAGES (thread_id IS NULL):")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM messages WHERE thread_id IS NULL")
    orphaned = cursor.fetchone()[0]
    print(f"  {orphaned} messages with thread_id = NULL")
    
else:
    print(f"\n  ✅ TOTAL: {message_count_total} messages found!")
    
    # Show sample messages
    print(f"\n4. SAMPLE MESSAGES FROM THREAD {thread_id}:")
    print("-" * 80)
    
    if thread_internal_id:
        cursor.execute("""
            SELECT id, role, content, created_at
            FROM messages
            WHERE thread_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (thread_internal_id,))

    cursor.execute(sql, params)
    else:
        sql, params = convert_sql_placeholders("""
            SELECT id, role, content, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (thread_id,))

        cursor.execute(sql, params)
    
    messages = cursor.fetchall()
    
    for msg in messages:
        content_preview = msg[2][:100] + "..." if len(msg[2]) > 100 else msg[2]
        print(f"  [{msg[3]}] {msg[1].upper()}: {content_preview}")

# Check saved_threads table too
print(f"\n6. SAVED_THREADS TABLE:")
print("-" * 80)
sql, params = convert_sql_placeholders("""
    SELECT thread_id, thread_name, message_count, saved_at
    FROM saved_threads
    WHERE thread_id LIKE '%' || ? || '%'
    ORDER BY saved_at DESC
""", (thread_id,))

cursor.execute(sql, params)

saved = cursor.fetchall()
if saved:
    for row in saved:
        print(f"  Thread: {row[0]}")
        print(f"    Name: {row[1]}")
        print(f"    Messages: {row[2]}")
        print(f"    Saved: {row[3]}")
        print()
else:
    print("  No saved threads found with this ID")

conn.close()

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Thread ID: {thread_id}")
print(f"Assigned to: agent-2")
print(f"Messages found: {message_count_total}")
print("="*80)
