"""Check thread_assignments table in sessions.db"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("CHECKING THREAD_ASSIGNMENTS TABLE IN SESSIONS.DB")
print("=" * 80)

conn = sqlite3.connect(str(sessions_db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check if table exists
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='thread_assignments'
""")

table_exists = cursor.fetchone()

if table_exists:
    print("\nTable EXISTS in sessions.db")
    
    # Get schema
    cursor.execute("PRAGMA table_info(thread_assignments)")
    columns = cursor.fetchall()
    
    print("\nSchema:")
    for col in columns:
        print(f"  - {col['name']} ({col['type']}) {'NOT NULL' if col['notnull'] else 'NULL'}")
    
    # Get all data
    cursor.execute("SELECT * FROM thread_assignments")
    rows = cursor.fetchall()
    
    print(f"\nTotal rows: {len(rows)}")
    if rows:
        print("\nData:")
        for row in rows:
            print(f"  ID: {row['id']}")
            for key in row.keys():
                if key != 'id':
                    print(f"    {key}: {row[key]}")
            print()
else:
    print("\nTable DOES NOT EXIST in sessions.db")
    print("\nNeed to create it. Checking if it exists in ai_infrastructure.db...")
    
    # Check ai_infrastructure.db
    ai_db = root_dir / 'data' / 'ai_infrastructure.db'
    ai_conn = sqlite3.connect(str(ai_db))
    ai_conn.row_factory = sqlite3.Row
    ai_cursor = ai_conn.cursor()
    
    ai_cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='thread_assignments'
    """)
    
    ai_table = ai_cursor.fetchone()
    
    if ai_table:
        print("\n✅ Table EXISTS in ai_infrastructure.db")
        
        # Get schema
        ai_cursor.execute("PRAGMA table_info(thread_assignments)")
        columns = ai_cursor.fetchall()
        
        print("\nSchema:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']}) {'NOT NULL' if col['notnull'] else 'NULL'}")
        
        # Get all data
        ai_cursor.execute("SELECT * FROM thread_assignments")
        rows = ai_cursor.fetchall()
        
        print(f"\nTotal rows: {len(rows)}")
        if rows:
            print("\nData:")
            for row in rows:
                print(f"  ID: {row['id']}")
                for key in row.keys():
                    if key != 'id':
                        print(f"    {key}: {row[key]}")
                print()
    else:
        print("\n❌ Table DOES NOT EXIST in ai_infrastructure.db either")
        print("\nTable structure from earlier schema analysis:")
        print("  - id (INTEGER PRIMARY KEY)")
        print("  - user_id (INTEGER)")
        print("  - session_id (TEXT)")
        print("  - location (TEXT)")
        print("  - created_at (TIMESTAMP)")
        print("  - updated_at (TIMESTAMP)")
    
    ai_conn.close()

conn.close()
