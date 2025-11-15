"""Check message counts for threads"""
import sqlite3
from pathlib import Path

db_path = Path('data/sessions.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('\n=== Messages Table Structure ===')
cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()
for col in columns:
    print(f'  {col["name"]} ({col["type"]})')

print('\n=== Message Counts by thread_id ===')
cursor.execute('''
    SELECT thread_id, COUNT(*) as msg_count 
    FROM messages 
    WHERE thread_id IS NOT NULL
    GROUP BY thread_id
    ORDER BY msg_count DESC 
    LIMIT 20
''')

results = cursor.fetchall()
if results:
    for row in results:
        print(f'  Thread {row[0]}: {row[1]} messages')
else:
    print('  No messages found with session_id')

print('\n=== Threads with matching session IDs ===')
cursor.execute('''
    SELECT t.thread_slug, t.name, 
           (SELECT COUNT(*) FROM messages m WHERE m.session_id = t.thread_slug) as msg_count
    FROM threads t
    WHERE t.user_id = 14
    ORDER BY msg_count DESC
    LIMIT 20
''')

results = cursor.fetchall()
if results:
    for row in results:
        print(f'  Thread "{row[1]}" ({row[0]}): {row[2]} messages')
else:
    print('  No matching threads found')

print('\n=== Total Messages ===')
cursor.execute('SELECT COUNT(*) FROM messages')
total = cursor.fetchone()[0]
print(f'  Total messages: {total}')

print('\n=== Total Threads ===')
cursor.execute('SELECT COUNT(*) FROM threads')
total_threads = cursor.fetchone()[0]
print(f'  Total threads: {total_threads}')

conn.close()
