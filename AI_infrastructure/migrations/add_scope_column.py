"""
Migration: Add scope column to oauth_tokens table
Created: November 14, 2025
Purpose: Fix "table oauth_tokens has no column named scope" error
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_scope_column():
    """Add scope column to oauth_tokens table if it doesn't exist"""
    
    # Get database path
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db - DEPRECATED (now PostgreSQL)'
    
    logger.info(f"🔧 Connecting to: {db_path}")
    
    conn = psycopg2.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='oauth_tokens'")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'scope' in columns:
            logger.info("✅ Column 'scope' already exists in oauth_tokens table")
        else:
            logger.info("🔧 Adding 'scope' column to oauth_tokens table...")
            cursor.execute("""
                ALTER TABLE oauth_tokens 
                ADD COLUMN scope TEXT
            """)
            conn.commit()
            logger.info("✅ Successfully added 'scope' column")
        
        # Verify the change
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='oauth_tokens'")
        columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"📋 Current oauth_tokens columns: {', '.join(columns)}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_scope_column()

