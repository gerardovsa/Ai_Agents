"""Check threads table structure"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables in database: {tables}")

# Check if threads table exists
if 'threads' in tables:
    cursor.execute("PRAGMA table_info(threads)")
    columns = cursor.fetchall()
    print("\nThreads table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check for workflow_slug
    column_names = [col[1] for col in columns]
    print(f"\nHas workflow_slug: {'workflow_slug' in column_names}")
    print(f"Has workflow_title: {'workflow_title' in column_names}")
    print(f"Has internal_doc_slug: {'internal_doc_slug' in column_names}")
    print(f"Has internal_doc_title: {'internal_doc_title' in column_names}")
else:
    print("\nThreads table does NOT exist")

conn.close()
