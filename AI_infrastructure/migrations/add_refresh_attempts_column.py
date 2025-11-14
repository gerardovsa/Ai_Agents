"""
Add refresh_attempts column to oauth_tokens table

Migration: Add missing refresh_attempts column
Date: November 14, 2025
Reason: Microsoft OAuth routes expect this column but it's missing from table schema
"""

import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection to ai_infrastructure.db in data/ folder"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def add_refresh_attempts_column():
    """
    Add refresh_attempts column to oauth_tokens table if it doesn't exist
    
    This column tracks the number of token refresh attempts for monitoring
    and error handling purposes.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(oauth_tokens)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'refresh_attempts' in columns:
            logger.info("✅ refresh_attempts column already exists")
            conn.close()
            return True
        
        # Add the column with default value 0
        logger.info("🔧 Adding refresh_attempts column to oauth_tokens table...")
        cursor.execute('''
            ALTER TABLE oauth_tokens 
            ADD COLUMN refresh_attempts INTEGER DEFAULT 0
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Successfully added refresh_attempts column")
        print("✅ Migration complete: refresh_attempts column added to oauth_tokens table")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    # Run migration when executed directly
    logging.basicConfig(level=logging.INFO)
    add_refresh_attempts_column()
