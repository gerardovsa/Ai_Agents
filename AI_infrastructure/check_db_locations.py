import sqlite3
import os

# Check both possible locations
locations = [
    'ai_infrastructure.db',
    '../ai_infrastructure.db'
]

for loc in locations:
    if os.path.exists(loc):
        print(f"\nChecking: {os.path.abspath(loc)}")
        conn = sqlite3.connect(loc)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables ({len(tables)}): {tables}")
        conn.close()
