import sqlite3
from pathlib import Path
import json

# Check sessions.db
print('\n=== CHECKING sessions.db ===')
db_path = Path('data/sessions.db')
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('\nTables:')
    for table in tables:
        print(f'- {table[0]}')
        
    # Check for threads/sessions for user 14
    for table in ['chat_sessions', 'threads', 'sessions', 'user_sessions']:
        try:
            cursor.execute(f"SELECT * FROM {table[0]} WHERE user_id = 14 LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                print(f'\n=== Found data in {table[0]} for user 14 ===')
                print(f'Count: {len(rows)}')
                for row in rows:
                    print(row)
        except:
            pass
    
    conn.close()
else:
    print('sessions.db not found')

# Check thread_assignments in ai_infrastructure.db
print('\n=== CHECKING thread_assignments ===')
db_path = Path('data/ai_infrastructure.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute('SELECT * FROM thread_assignments WHERE user_id = 14')
assignments = cursor.fetchall()
print(f'\nFound {len(assignments)} thread assignments for user 14:')
for assignment in assignments:
    print(assignment)

conn.close()

# Check backend API endpoint
print('\n=== BACKEND API CHECK ===')
print('Thread loading happens via API: /api/threads/list')
print('Check if Flask backend is running and if the endpoint returns threads for user 14')
