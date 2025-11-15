"""Check what tables exist in sessions.db"""
import sqlite3

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print('Tables in sessions.db:')
for table in tables:
    print(f'  - {table[0]}')
    
    # Count rows
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'    Rows: {count}')

conn.close()
