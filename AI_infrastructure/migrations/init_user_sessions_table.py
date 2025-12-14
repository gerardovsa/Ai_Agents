"""
Migration: Initialize user_sessions table
Created: November 14, 2025
Purpose: Fix Google/Microsoft OAuth 401 errors by ensuring user_sessions table exists
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_user_sessions_table():
    """Create user_sessions table if it doesn't exist"""
    
    # Get database path
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db - DEPRECATED (now PostgreSQL)'
    
    logger.info(f"🔧 Connecting to: {db_path}")
    
    conn = psycopg2.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Create user_sessions table
        logger.info("🔧 Creating user_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create index on token for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_token 
            ON user_sessions(token)
        """)
        
        # Create index on user_id for faster user queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id 
            ON user_sessions(user_id)
        """)
        
        conn.commit()
        logger.info("✅ Successfully created/verified user_sessions table")
        
        # Verify the table structure
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='user_sessions'")
        columns = [(row[1], row[2]) for row in cursor.fetchall()]
        logger.info(f"📋 user_sessions columns: {columns}")
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM user_sessions")
        count = cursor.fetchone()[0]
        logger.info(f"📊 Current sessions in table: {count}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_user_sessions_table()

