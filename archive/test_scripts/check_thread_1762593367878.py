"""Check thread 1762593367878 details"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path
import json

# Database paths
root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("CHECKING THREAD: 1762593367878")
print("=" * 80)

# Connect to sessions.db
conn = sqlite3.connect(str(sessions_db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check in threads table
print("\n1. THREADS TABLE:")
print("-" * 80)
sql, params = convert_sql_placeholders("""
    SELECT * FROM threads 
    WHERE id = ? OR id = ? OR id = ?
""", (1762593367878, '1762593367878', 'prime_1762593367878'))

cursor.execute(sql, params)

thread = cursor.fetchone()
if thread:
    print("FOUND IN THREADS TABLE!")
    for key in thread.keys():
        value = thread[key]
        if key == 'conversation' and value:
            try:
                parsed = json.loads(value)
                print(f"  {key}: {len(parsed)} items in conversation")
            except:
                print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else value)
        else:
            print(f"  {key}: {value}")
else:
    print("NOT FOUND in threads table")

# Check in saved_threads table
print("\n2. SAVED_THREADS TABLE:")
print("-" * 80)
sql, params = convert_sql_placeholders("""
    SELECT * FROM saved_threads 
    WHERE thread_id = ? OR thread_id = ? OR thread_id = ?
""", (1762593367878, '1762593367878', 'prime_1762593367878'))

cursor.execute(sql, params)

saved_thread = cursor.fetchone()
if saved_thread:
    print("FOUND IN SAVED_THREADS TABLE!")
    for key in saved_thread.keys():
        value = saved_thread[key]
        if key == 'conversation' and value:
            try:
                parsed = json.loads(value)
                print(f"  {key}: {len(parsed)} messages")
                print("\n  CONVERSATION PREVIEW:")
                for i, msg in enumerate(parsed[:3], 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"    Message {i} ({role}): {preview}")
            except Exception as e:
                print(f"  {key}: Error parsing - {e}")
        else:
            print(f"  {key}: {value}")
else:
    print("NOT FOUND in saved_threads table")

# Check messages linked to this thread
print("\n3. MESSAGES TABLE:")
print("-" * 80)
sql, params = convert_sql_placeholders("""
    SELECT id, thread_id, role, content, created_at 
    FROM messages 
    WHERE thread_id = ? OR thread_id = ? OR thread_id = ?
    ORDER BY created_at DESC
    LIMIT 10
""", (1762593367878, '1762593367878', 'prime_1762593367878'))

cursor.execute(sql, params)

messages = cursor.fetchall()
if messages:
    print(f"FOUND {len(messages)} MESSAGES:")
    for msg in messages:
        content_preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"  ID: {msg['id']}, Role: {msg['role']}, Created: {msg['created_at']}")
        print(f"    Content: {content_preview}")
        print()
else:
    print("NO MESSAGES FOUND for this thread")

# Check thread assignments
print("\n4. THREAD ASSIGNMENTS:")
print("-" * 80)
ai_db = root_dir / 'data' / 'ai_infrastructure.db'
ai_conn = sqlite3.connect(str(ai_db))
ai_conn.row_factory = sqlite3.Row
ai_cursor = ai_conn.cursor()

ai_cursor.execute("""
    SELECT * FROM thread_assignments 
    WHERE thread_id = ? OR thread_id = ? OR thread_id = ?
""", (1762593367878, '1762593367878', 'prime_1762593367878'))

assignments = ai_cursor.fetchall()
if assignments:
    print(f"FOUND {len(assignments)} ASSIGNMENTS:")
    for assign in assignments:
        for key in assign.keys():
            print(f"  {key}: {assign[key]}")
        print()
else:
    print("NO ASSIGNMENTS FOUND for this thread")

# Summary
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"In threads table: {'YES' if thread else 'NO'}")
print(f"In saved_threads table: {'YES' if saved_thread else 'NO'}")
print(f"Messages count: {len(messages)}")
print(f"Assignments count: {len(assignments)}")

conn.close()
ai_conn.close()
