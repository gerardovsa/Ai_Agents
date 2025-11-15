"""
Create synergy_internal_docs table
Run this once to set up the database table for internal documents
"""

import sqlite3
from pathlib import Path

# Database path
ROOT_DIR = Path(__file__).parent
DB_PATH = ROOT_DIR / 'data' / 'synergy_sessions.db'

print(f"Creating table in: {DB_PATH}")

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS synergy_internal_docs (
    doc_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    format TEXT NOT NULL DEFAULT 'markdown',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (session_id) REFERENCES synergy_sessions(session_id) ON DELETE CASCADE
)
''')

# Index for fast lookups
cursor.execute('''
CREATE INDEX IF NOT EXISTS idx_internal_docs_session 
ON synergy_internal_docs(session_id)
''')

conn.commit()
conn.close()

print("✅ Created synergy_internal_docs table successfully")
print("✅ Created index on session_id")
print("\nTable structure:")
print("  - doc_id (TEXT PRIMARY KEY)")
print("  - session_id (TEXT NOT NULL)")
print("  - title (TEXT NOT NULL)")
print("  - content (TEXT)")
print("  - format (TEXT, default: 'markdown')")
print("  - created_at (TIMESTAMP)")
print("  - updated_at (TIMESTAMP)")
print("  - created_by (TEXT)")
print("  - version (INTEGER, default: 1)")
