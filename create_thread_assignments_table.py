"""
Create thread_assignments table in ai_infrastructure.db

This table is used to track which NATO agent (Alpha, Bravo, Charlie, etc.)
has which thread assigned to them.
"""

import sqlite3
from pathlib import Path

# Connect to ai_infrastructure.db
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print(f"Connecting to: {db_path}")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_assignments'")
exists = cursor.fetchone()

if exists:
    print("[INFO] thread_assignments table already exists")
    
    # Show current data
    cursor.execute("SELECT * FROM thread_assignments")
    rows = cursor.fetchall()
    print(f"\nCurrent rows: {len(rows)}")
    for row in rows:
        print(f"  {row}")
else:
    print("[INFO] Creating thread_assignments table...")
    
    # Create table
    cursor.execute("""
        CREATE TABLE thread_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            location TEXT NOT NULL,
            agent_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, session_id)
        )
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX idx_thread_assignments_user_session 
        ON thread_assignments(user_id, session_id)
    """)
    
    cursor.execute("""
        CREATE INDEX idx_thread_assignments_session 
        ON thread_assignments(session_id)
    """)
    
    conn.commit()
    print("[OK] Created thread_assignments table with indexes")

conn.close()
print("\n[DONE] Thread assignments table ready")
