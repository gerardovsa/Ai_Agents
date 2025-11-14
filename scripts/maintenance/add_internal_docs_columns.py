"""
Add missing columns to synergy_internal_docs table for rich module features

Adds:
- content_json TEXT (TipTap JSON format)
- doc_type TEXT (richtext/spreadsheet)
- linked_to_ai BOOLEAN
"""

import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / 'data' / 'synergy_sessions.db'

def add_columns():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check which columns exist
    cursor.execute("PRAGMA table_info(synergy_internal_docs)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    # Add content_json if missing
    if 'content_json' not in columns:
        print("Adding content_json column...")
        cursor.execute("""
            ALTER TABLE synergy_internal_docs
            ADD COLUMN content_json TEXT
        """)
        print("✅ Added content_json column")
    
    # Add doc_type if missing
    if 'doc_type' not in columns:
        print("Adding doc_type column...")
        cursor.execute("""
            ALTER TABLE synergy_internal_docs
            ADD COLUMN doc_type TEXT DEFAULT 'richtext'
        """)
        print("✅ Added doc_type column")
    
    # Add linked_to_ai if missing
    if 'linked_to_ai' not in columns:
        print("Adding linked_to_ai column...")
        cursor.execute("""
            ALTER TABLE synergy_internal_docs
            ADD COLUMN linked_to_ai BOOLEAN DEFAULT 0
        """)
        print("✅ Added linked_to_ai column")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database schema updated successfully!")
    print(f"Database: {DB_PATH}")

if __name__ == '__main__':
    add_columns()
