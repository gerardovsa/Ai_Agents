import sqlite3
from pathlib import Path

# Check sessions.db instead (threads are stored there)
db_path = Path(__file__).parent / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# List all tables
print("=== Database Tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
for t in tables:
    print(f"  - {t[0]}")

# Look for threads table
thread_tables = [t[0] for t in tables if 'thread' in t[0].lower()]
print(f"\n=== Thread-related tables: {thread_tables}")

if thread_tables:
    table_name = thread_tables[0]
    print(f"\n=== Columns in '{table_name}' table ===")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    print(f"\n=== Searching in '{table_name}' for 'Test 4' ===")
    
    # Try to find the right columns
    col_names = [col[1] for col in columns]
    
    # Build query based on available columns
    if 'name' in col_names:
        cursor.execute(f"SELECT id, thread_slug, name, location, created_at, updated_at FROM {table_name} WHERE name LIKE '%Test 4%' ORDER BY created_at DESC LIMIT 5")
    else:
        # Just get recent threads
        cursor.execute(f"SELECT id, thread_slug, name, location, created_at, updated_at FROM {table_name} ORDER BY created_at DESC LIMIT 10")
    
    results = cursor.fetchall()
    
    if results:
        print(f"\nFound {len(results)} thread(s):")
        for r in results:
            print(f"\nThread: {r}")
            print("---")
    else:
        print("No threads found")
else:
    print("\nNo thread table found!")

conn.close()
