import sqlite3
from pathlib import Path

# Connect to database
db_path = Path('data/ai_infrastructure.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# List all tables
print('\n=== TABLES IN DATABASE ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f'- {table[0]}')

# Check for chat_sessions table
print('\n=== CHECKING CHAT_SESSIONS TABLE ===')
try:
    cursor.execute('SELECT id, thread_slug, name, user_id, created_at, updated_at FROM chat_sessions WHERE user_id = 14 ORDER BY updated_at DESC')
    sessions = cursor.fetchall()
    print(f'\nFound {len(sessions)} sessions for user 14:')
    for session in sessions:
        print(f'\nID: {session[0]}')
        print(f'Thread Slug: {session[1]}')
        print(f'Name: {session[2]}')
        print(f'User ID: {session[3]}')
        print(f'Created: {session[4]}')
        print(f'Updated: {session[5]}')
        print('---')
except Exception as e:
    print(f'Error: {e}')

# Check messages for these sessions
print('\n=== CHECKING MESSAGES ===')
try:
    cursor.execute('''
        SELECT cs.id, cs.name, COUNT(m.id) as message_count
        FROM chat_sessions cs
        LEFT JOIN messages m ON cs.id = m.session_id
        WHERE cs.user_id = 14
        GROUP BY cs.id
        ORDER BY cs.updated_at DESC
    ''')
    sessions_with_counts = cursor.fetchall()
    print(f'\nSessions with message counts:')
    for session in sessions_with_counts:
        print(f'- {session[1]}: {session[2]} messages')
except Exception as e:
    print(f'Error: {e}')

conn.close()
print('\n=== COMPLETE ===')
