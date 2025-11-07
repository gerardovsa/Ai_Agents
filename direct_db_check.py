import requests
import json
import sqlite3
from pathlib import Path

DB_PATH = Path('data/synergy_sessions.db')

def check_db_value(session_id):
    """Check the next_steps value directly in the database"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT next_steps FROM synergy_sessions WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]) if row[0] else []
    return None

# Create test session
session_data = {
    'title': 'Direct DB Check Test',
    'next_steps': [{'description': 'Test step', 'completed': False}]
}

r = requests.post('http://localhost:5001/api/synergy/create', json=session_data)
result = r.json()
sid = result['session_id']
print(f'\n1. Created session: {sid}')

# Check initial value in DB
initial_db = check_db_value(sid)
print(f'2. Initial DB value: {initial_db}')

# Update via API
update = {
    'updates': {
        'next_steps': [{'description': 'Test step', 'completed': True}]
    }
}

r2 = requests.patch(f'http://localhost:5001/api/synergy/{sid}', json=update)
print(f'3. Update API response: {r2.json()}')

# Check DB value immediately after update
updated_db = check_db_value(sid)
print(f'4. DB value after update: {updated_db}')

# Get via API to compare
r3 = requests.get(f'http://localhost:5001/api/synergy/{sid}')
api_value = r3.json()['session']['next_steps']
print(f'5. API GET value: {api_value}')

# Comparison
if updated_db and updated_db[0]['completed'] == True:
    print('\n SUCCESS: Update persisted to database!')
else:
    print('\n FAIL: Update did not persist to database')
    print(f'   Expected: completed=True')
    print(f'   Got: completed={updated_db[0]["completed"] if updated_db else "None"}')

# Cleanup
requests.delete(f'http://localhost:5001/api/synergy/{sid}')
