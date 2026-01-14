"""Quick migration script to add token_count column to threads table"""
import sqlite3
from pathlib import Path

# Database path (threads are in sessions.db, not ai_infrastructure.db)
db_path = Path(__file__).parent / 'data' / 'sessions.db'

print(f"Connecting to: {db_path}")

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Check if threads table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='threads'")
    if not cursor.fetchone():
        print("ERROR: threads table does not exist!")
        print("\nAvailable tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for table in cursor.fetchall():
            print(f"  - {table[0]}")
    else:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(threads)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'token_count' in columns:
            print("token_count column already exists!")
        else:
            # Add column
            cursor.execute("ALTER TABLE threads ADD COLUMN token_count INTEGER DEFAULT 0")
            print("✅ Added token_count column")
            
        # Create index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_token_count ON threads(token_count)")
        print("✅ Created index on token_count")
        
        # Update existing records
        cursor.execute("UPDATE threads SET token_count = 0 WHERE token_count IS NULL")
        print(f"✅ Updated {cursor.rowcount} existing threads")
        
        conn.commit()
        print("\n🎉 Migration complete!")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM threads")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM threads WHERE token_count IS NOT NULL")
        with_count = cursor.fetchone()[0]
        print(f"\nVerification: {with_count}/{total} threads have token_count field")
        
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
