import sqlite3
from pathlib import Path

DB_PATH = Path('data/synergy_sessions.db')

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Get all session IDs
cursor.execute('SELECT session_id FROM synergy_sessions LIMIT 5')
rows = cursor.fetchall()

print('Session IDs in database:')
for row in rows:
    print(f'  {row[0]}')

# Try manual update
test_sid = rows[0][0] if rows else None
if test_sid:
    print(f'\nTesting manual update on: {test_sid}')
    
    # Get current value
    cursor.execute('SELECT next_steps FROM synergy_sessions WHERE session_id = ?', (test_sid,))
    before = cursor.fetchone()[0]
    print(f'Before: {before}')
    
    # Update
    import json
    new_value = json.dumps([{'description': 'Manual test', 'completed': True}])
    cursor.execute('UPDATE synergy_sessions SET next_steps = ? WHERE session_id = ?', (new_value, test_sid))
    conn.commit()
    print(f'Rows affected: {cursor.rowcount}')
    
    # Check after
    cursor.execute('SELECT next_steps FROM synergy_sessions WHERE session_id = ?', (test_sid,))
    after = cursor.fetchone()[0]
    print(f'After: {after}')

conn.close()
