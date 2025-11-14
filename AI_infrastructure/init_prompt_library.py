"""
Initialize prompt_library table on Flask startup

This ensures the table exists before any API calls are made.
Should be called from flask_app.py during initialization.
"""

import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def init_prompt_library_table(db_path=None):
    """
    Create prompt_library table and indexes if they don't exist
    
    Args:
        db_path: Path to ai_infrastructure.db (auto-detected if not provided)
    """
    if db_path is None:
        # Use standard path from AI_agents/data/
        root_dir = Path(__file__).parent.parent
        db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    db_path = str(db_path)
    logger.info(f"🔧 Initializing prompt_library table in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create prompt_library table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workspace_id INTEGER,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(50) NOT NULL,
                type VARCHAR(20) NOT NULL DEFAULT 'quick_action',
                description TEXT,
                prompt_text TEXT NOT NULL,
                tags TEXT,
                visibility VARCHAR(20) NOT NULL DEFAULT 'private',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_prompt_library_user_id ON prompt_library(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_prompt_library_workspace_id ON prompt_library(workspace_id)",
            "CREATE INDEX IF NOT EXISTS idx_prompt_library_category ON prompt_library(category)",
            "CREATE INDEX IF NOT EXISTS idx_prompt_library_visibility ON prompt_library(visibility)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Check if table has any rows
        cursor.execute("SELECT COUNT(*) FROM prompt_library")
        count = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ prompt_library table initialized ({count} existing prompts)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize prompt_library table: {e}")
        return False


if __name__ == '__main__':
    # Test initialization
    logging.basicConfig(level=logging.INFO)
    success = init_prompt_library_table()
    if success:
        print("✅ Prompt library table initialized successfully")
    else:
        print("❌ Failed to initialize prompt library table")
