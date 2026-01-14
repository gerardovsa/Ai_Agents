import sqlite3
from pathlib import Path

db = Path('data/sessions.db')
conn = sqlite3.connect(str(db))
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM threads')
print(f'Threads: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM messages')
print(f'Messages: {cursor.fetchone()[0]}')

cursor.execute('SELECT thread_slug, name, location FROM threads ORDER BY created_at DESC LIMIT 5')
print('\nRecent threads:')
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]} ({row[2]})')

conn.close()
