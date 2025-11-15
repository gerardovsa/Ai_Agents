import sqlite3
from pathlib import Path
import json

# Check threads in sessions.db
print('\n=== THREADS FOR USER 14 (sessions.db) ===')
db_path = Path('data/sessions.db')
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# First check table structure
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()
print('\n=== THREADS TABLE STRUCTURE ===')
for col in columns:
    print(f'- {col["name"]}: {col["type"]}')

# Get threads for user 14 - use only columns that exist
cursor.execute('''
    SELECT *
    FROM threads 
    WHERE user_id = 14 
    ORDER BY updated_at DESC
''')
threads = cursor.fetchall()

print(f'\nFound {len(threads)} threads for user 14:\n')
for thread in threads:
    print(f'Thread ID: {thread["id"]}')
    print(f'  Name: {thread["name"]}')
    print(f'  Slug: {thread["thread_slug"]}')
    print(f'  Created: {thread["created_at"]}')
    print(f'  Updated: {thread["updated_at"]}')
    print(f'  Location: {thread["location"] if thread["location"] else "None"}')
    print(f'  Tags: {thread["tags"] if thread["tags"] else "None"}')
    print(f'  Synergy: {thread["synergy_card_id"] if thread["synergy_card_id"] else "None"}')
    
    # Get message count
    cursor.execute('SELECT COUNT(*) FROM messages WHERE thread_id = ?', (thread["id"],))
    msg_count = cursor.fetchone()[0]
    print(f'  Messages: {msg_count}')
    print('---')

# Check messages table structure
print('\n=== MESSAGES TABLE STRUCTURE ===')
cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()
for col in columns:
    print(f'- {col["name"]}: {col["type"]}')

# Check if there are any threads for other users
print('\n=== ALL THREADS IN DATABASE ===')
cursor.execute('SELECT user_id, COUNT(*) as count FROM threads GROUP BY user_id')
user_counts = cursor.fetchall()
for row in user_counts:
    print(f'User {row["user_id"]}: {row["count"]} threads')

conn.close()
print('\n=== COMPLETE ===')
