import sqlite3
from pathlib import Path

db_path = Path('c:/Users/gpoli/GIT/AI_agents/data/synergy_sessions.db')

if not db_path.exists():
    print(f"❌ Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=" * 70)
print("SYNERGY DATABASE SCHEMA")
print("=" * 70)
print(f"\nDatabase: {db_path}")
print(f"Tables: {[t[0] for t in tables]}")

# Get sessions table schema
if tables:
    cursor.execute("PRAGMA table_info(sessions)")
    columns = cursor.fetchall()
    
    print("\nSessions Table Columns:")
    for col in columns:
        print(f"  {col[1]:30s} {col[2]:15s} {'NOT NULL' if col[3] else ''}")
    
    # Count sessions
    cursor.execute("SELECT COUNT(*) FROM sessions")
    count = cursor.fetchone()[0]
    print(f"\nTotal Sessions: {count}")
    
    if count > 0:
        # Show sample
        cursor.execute("SELECT session_id, title, kanban_column, status FROM sessions LIMIT 5")
        samples = cursor.fetchall()
        print("\nSample Sessions:")
        for s in samples:
            print(f"  {s[0]}: {s[1]} [{s[2]}] ({s[3]})")

conn.close()
print("\n" + "=" * 70)
