"""Analyze ai_infrastructure.db contents"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("="*70)
print("AI_INFRASTRUCTURE.DB ANALYSIS")
print("="*70)
print()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"Found {len(tables)} tables:\n")

for table_name in tables:
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"📊 {table_name}: {row_count} rows")
    print(f"   Columns: {', '.join([col[1] for col in columns])}")
    
    # Show sample data for non-empty tables
    if row_count > 0 and row_count <= 5:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        print(f"   Sample data:")
        for row in rows:
            print(f"     {dict(row)}")
    elif row_count > 5:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print(f"   First 3 rows:")
        for row in rows:
            print(f"     {dict(row)}")
    
    print()

conn.close()
