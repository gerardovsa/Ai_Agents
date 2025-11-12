"""
Fix threads table schema - Add missing branch_point_message_id column
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print("=" * 60)
print("FIXING THREADS TABLE SCHEMA")
print("=" * 60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(threads)")
columns = [row[1] for row in cursor.fetchall()]

if 'branch_point_message_id' not in columns:
    print("\n❌ Missing column: branch_point_message_id")
    print("➕ Adding column...")
    
    try:
        cursor.execute("""
            ALTER TABLE threads 
            ADD COLUMN branch_point_message_id TEXT
        """)
        conn.commit()
        print("✅ Column added successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
else:
    print("\n✅ Column already exists: branch_point_message_id")

# Verify final schema
cursor.execute("PRAGMA table_info(threads)")
print("\n📋 Final threads table schema:")
for row in cursor.fetchall():
    print(f"   - {row[1]} ({row[2]})")

conn.close()
print("\n✅ Schema fix complete!")
