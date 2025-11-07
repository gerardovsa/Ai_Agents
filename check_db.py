import sqlite3
import os
from pathlib import Path

# Check sessions.db
db_path = Path('data/sessions.db')
print(f"Database path: {db_path}")
print(f"Exists: {db_path.exists()}")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables in sessions.db:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check if saved_threads exists
    if any(t[0] == 'saved_threads' for t in tables):
        cursor.execute("PRAGMA table_info(saved_threads)")
        columns = cursor.fetchall()
        print(f"\nColumns in saved_threads:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
else:
    print("Database does not exist yet!")
