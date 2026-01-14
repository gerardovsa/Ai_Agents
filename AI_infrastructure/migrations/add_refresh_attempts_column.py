"""
Add refresh_attempts column to oauth_tokens table

Migration: Add missing refresh_attempts column
Date: November 14, 2025
Reason: Microsoft OAuth routes expect this column but it's missing from table schema
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection (respects USE_SUPABASE environment)"""
    from shared.database_utils import get_database_connection
    return get_database_connection('ai_infrastructure')


def add_refresh_attempts_column():
    """
    Add refresh_attempts column to oauth_tokens table if it doesn't exist
    
    This column tracks the number of token refresh attempts for monitoring
    and error handling purposes.
    """
    # DISABLED: Migration not needed on Render with Supabase (tables already exist)
    import os
    if os.getenv('USE_SUPABASE') == 'true' or os.getenv('RENDER') == 'true':
        logger.info("⏭️  Skipping migration - using Supabase (tables already exist)")
        return True
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if column already exists (PostgreSQL-compatible)
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name = 'oauth_tokens'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
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
