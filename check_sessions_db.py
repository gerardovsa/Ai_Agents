"""Check threads table in sessions.db"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()

print("Threads table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check for workflow columns
column_names = [col[1] for col in columns]
print(f"\nHas workflow_slug: {'workflow_slug' in column_names}")
print(f"Has workflow_title: {'workflow_title' in column_names}")
print(f"Has internal_doc_slug: {'internal_doc_slug' in column_names}")
print(f"Has internal_doc_title: {'internal_doc_title' in column_names}")

conn.close()
