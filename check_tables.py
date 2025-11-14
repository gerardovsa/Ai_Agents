import sqlite3
from pathlib import Path

# Check both databases
databases = [
    'data/ai_infrastructure.db',
    'data/sessions.db'
]

for db_path in databases:
    if not Path(db_path).exists():
        print(f"\n{db_path} - NOT FOUND")
        continue
        
    print(f"\n{db_path}:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"  Tables ({len(tables)}):")
    for table in tables:
        print(f"    - {table[0]}")
        
        # Check if it's the threads table
        if table[0] == 'threads':
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"      Columns ({len(columns)}):")
            for col in columns:
                has_lock = 'locked' in col[1].lower()
                marker = " <-- LOCK COLUMN" if has_lock else ""
                print(f"        {col[1]} ({col[2]}){marker}")
    
    conn.close()
