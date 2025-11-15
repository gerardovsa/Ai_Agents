"""Check all tables in both databases"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent

# Check ai_infrastructure.db
print("="*60)
print("AI_INFRASTRUCTURE.DB")
print("="*60)
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print(f"\nTables ({len(tables)}):")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  - {table[0]} ({count} rows)")
conn.close()

# Check sessions.db
print("\n" + "="*60)
print("SESSIONS.DB")
print("="*60)
db_path = root_dir / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print(f"\nTables ({len(tables)}):")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  - {table[0]} ({count} rows)")
conn.close()

# Check synergy_sessions.db
print("\n" + "="*60)
print("SYNERGY_SESSIONS.DB")
print("="*60)
db_path = root_dir / 'data' / 'synergy_sessions.db'
try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\nTables ({len(tables)}):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]} ({count} rows)")
    conn.close()
except Exception as e:
    print(f"[ERROR] {e}")
