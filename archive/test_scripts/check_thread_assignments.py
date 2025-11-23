"""Check thread assignments for specific threads"""
import sqlite3
from pathlib import Path
from shared.database_utils import convert_sql_placeholders

# Database paths
infrastructure_db = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
sessions_db = Path(__file__).parent / 'data' / 'sessions.db'

# Threads to check
threads_to_check = ['1762828793392', '1762851232975', '1762828476509']

# Connect to sessions database
conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()

print('\n' + '='*60)
print('THREAD ASSIGNMENTS CHECK')
print('='*60 + '\n')

print(f'Database: {sessions_db}\n')

# First, check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print('Available tables:')
for table in tables:
    print(f'  • {table[0]}')
print()

# Check threads table schema
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()
print('Threads table columns:')
for col in columns:
    print(f'  • {col[1]} ({col[2]})')
print()

# Check specific threads
print('-'*60)
print('REQUESTED THREADS:')
print('-'*60 + '\n')

for thread_id in threads_to_check:
    sql, params = convert_sql_placeholders('''
        SELECT thread_slug, user_id, name, location, created_at, updated_at
        FROM threads 
        WHERE thread_slug = ?
    ''', (thread_id,))

    cursor.execute(sql, params)
    
    result = cursor.fetchone()
    
    print(f'Thread: {thread_id}')
    if result:
        print(f'  ✅ FOUND')
        print(f'  📋 Name: {result[2][:60] if result[2] else "Untitled"}')
        print(f'  👤 User ID: {result[1]}')
        print(f'  📍 Location: {result[3] if result[3] else "NULL/prime (default)"}')
        print(f'  📅 Created: {result[4]}')
        print(f'  🕐 Updated: {result[5]}')
    else:
        print(f'  ❌ NOT FOUND in database')
    print()

conn.close()

print('='*60)
print('Check complete!')
print('='*60)
