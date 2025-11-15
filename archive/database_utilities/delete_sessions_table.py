"""
Delete sessions table - NO MIGRATION
"""
import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"Current tables: {tables}")

if 'sessions' in tables:
    print(f"\nDeleting 'sessions' table...")
    cursor.execute('DROP TABLE sessions')
    conn.commit()
    print(f"DELETED: sessions table")
else:
    print(f"\nSKIP: sessions table does not exist")

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
final_tables = [row[0] for row in cursor.fetchall()]

print(f"\nFinal tables: {final_tables}")

# Count rows in synergy_sessions
cursor.execute('SELECT COUNT(*) FROM synergy_sessions')
count = cursor.fetchone()[0]
print(f"\nsynergy_sessions has {count} rows")

conn.close()
print(f"\nDONE")
