import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in sessions.db:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
