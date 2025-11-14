"""Quick script to get synergy_sessions schema"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'synergy_sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== SYNERGY DATABASE TABLES ===")
for table in tables:
    print(f"\nTable: {table[0]}")
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table[0]}'")
    schema = cursor.fetchone()
    if schema:
        print(schema[0])
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"\nColumns ({len(columns)}):")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")

conn.close()
