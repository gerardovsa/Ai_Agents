"""Query specific synergy session to understand card structure"""
import sqlite3
from pathlib import Path
import json

root = Path('C:/Users/gpoli/GIT/AI_agents')
db = root / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Query the specific session
cursor.execute("""
    SELECT * FROM synergy_sessions 
    WHERE session_id LIKE ?
""", ('%email_thread_quote%',))

row = cursor.fetchone()

print("=" * 80)
print("SYNERGY CARD STRUCTURE - Session Fields")
print("=" * 80)

if row:
    print(f"\nSession ID: {row['session_id']}\n")
    print("Column Name".ljust(25), "Value".ljust(40), "Type")
    print("-" * 80)
    
    for key in row.keys():
        value = row[key]
        value_str = str(value)[:50] if value else 'NULL'
        
        # Try to parse JSON fields
        if value and key in ['platforms_involved', 'tags', 'documents', 'links', 
                             'next_steps', 'assignees', 'recent_activity', 'checklist',
                             'thread_ids', 'assigned_agents']:
            try:
                parsed = json.loads(value)
                value_type = f"JSON Array ({len(parsed)} items)" if isinstance(parsed, list) else "JSON Object"
                value_str = json.dumps(parsed, indent=2)[:100]
            except:
                value_type = "TEXT (invalid JSON)"
        else:
            value_type = "TEXT" if isinstance(value, str) else type(value).__name__
        
        print(f"{key.ljust(25)} {value_str.ljust(40)} {value_type}")
else:
    print("No matching session found")
    print("\nAll available sessions:")
    cursor.execute("SELECT session_id, title FROM synergy_sessions LIMIT 5")
    for s in cursor.fetchall():
        print(f"  - {s['session_id']}: {s['title']}")

conn.close()

print("\n" + "=" * 80)
print("DATABASE SCHEMA")
print("=" * 80)

# Get schema
conn = sqlite3.connect(str(db))
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(synergy_sessions)")
schema = cursor.fetchall()

print("\nColumn Name".ljust(25), "Type".ljust(15), "Not Null", "Default")
print("-" * 80)
for col in schema:
    col_name = col[1]
    col_type = col[2]
    not_null = "YES" if col[3] else "NO"
    default = col[4] if col[4] else "None"
    print(f"{col_name.ljust(25)} {col_type.ljust(15)} {not_null.ljust(8)} {default}")

conn.close()
