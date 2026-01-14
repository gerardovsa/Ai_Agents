"""
Initialize prompt_library table on Flask startup

This ensures the table exists before any API calls are made.
Should be called from flask_app.py during initialization.

UPDATED: November 17, 2025 - Now uses Supabase via get_database_connection()
"""

from pathlib import Path
import logging

# Import Supabase connection utility
import sys
sys.path.insert(0, str(Path(__file__).parent))
from shared.database_utils import get_database_connection, adapt_sql_for_database

logger = logging.getLogger(__name__)

def init_prompt_library_table(db_path=None):
    """
    Create prompt_library table and indexes if they don't exist
    
    Args:
        db_path: DEPRECATED - No longer used (kept for backward compatibility)
                Connection is always to Supabase ai_infrastructure schema
    
    OPTIMIZATION (Nov 19, 2025):
    - Uses longer statement timeout (120s) for DDL operations
    - Creates indexes in separate transactions to avoid lock contention
    - Catches timeout errors gracefully and verifies table existence
    """
    # Ignore db_path parameter - always use Supabase
    logger.info(f"🔧 Initializing prompt_library table in Supabase (ai_infrastructure schema)")
    
    conn = None
    try:
        conn = get_database_connection('ai_infrastructure')
        
        # Set longer timeout for DDL operations (120 seconds)
        with conn.cursor() as cursor:
            cursor.execute("SET statement_timeout = '120s'")
        conn.commit()
        
        # Step 1: Create table (most critical operation)
        try:
            with conn.cursor() as cursor:
                create_table_sql = adapt_sql_for_database("""
                    CREATE TABLE IF NOT EXISTS ai_infrastructure.prompt_library (
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
                        FOREIGN KEY (user_id) REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE
                    )
                """)
                cursor.execute(create_table_sql)
            conn.commit()
            logger.info(f"✅ prompt_library table structure verified")
        except Exception as table_error:
            # If timeout or error, verify table exists anyway
            logger.warning(f"⚠️ Table creation warning: {table_error}")
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM ai_infrastructure.prompt_library LIMIT 1")
                logger.info(f"✅ Table exists despite creation warning")
            except:
                raise Exception(f"Table creation failed and table does not exist: {table_error}")
        
        # Step 2: Create indexes (skip if slow, table works without them)
        # Indexes are performance optimization only - not required for functionality
        indexes = [
            ("idx_prompt_library_user_id", "user_id"),
            ("idx_prompt_library_workspace_id", "workspace_id"),
            ("idx_prompt_library_category", "category"),
            ("idx_prompt_library_visibility", "visibility")
        ]
        
        logger.info("Creating indexes (may skip if slow)...")
        
        for idx_name, column in indexes:
            try:
                # Rollback any previous failed transaction
                conn.rollback()
                
                # Check if index already exists (fast query)
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 1 FROM pg_indexes 
                        WHERE schemaname = 'ai_infrastructure' 
                          AND indexname = %s
                    """, (idx_name,))
                    exists = cursor.fetchone()
                
                if exists:
                    logger.info(f"✅ Index {idx_name} already exists")
                    continue
                
                # Index doesn't exist - try to create it (with timeout)
                # Set short timeout for index creation (10s max per index)
                conn.rollback()  # Clean state
                with conn.cursor() as cursor:
                    cursor.execute("SET LOCAL statement_timeout = '10s'")
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON ai_infrastructure.prompt_library({column})")
                conn.commit()
                logger.info(f"✅ Index {idx_name} created")
                    
            except Exception as idx_error:
                # Rollback failed transaction
                try:
                    conn.rollback()
                except:
                    pass
                # Non-critical: indexes are performance optimization, not required
                error_msg = str(idx_error)
                if "timeout" in error_msg.lower():
                    logger.warning(f"⚠️ Index {idx_name} skipped (timeout - will retry next startup)")
                else:
                    logger.warning(f"⚠️ Index {idx_name} skipped: {error_msg}")
        
        # Step 3: Check row count (rollback first if transaction is aborted)
        try:
            conn.rollback()  # Ensure clean state
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ai_infrastructure.prompt_library")
                count = cursor.fetchone()[0]
            logger.info(f"✅ prompt_library table initialized ({count} existing prompts)")
        except Exception as count_error:
            logger.warning(f"⚠️ Could not count prompts: {count_error}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize prompt_library table: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


if __name__ == '__main__':
    # Test initialization
    logging.basicConfig(level=logging.INFO)
    success = init_prompt_library_table()
    if success:
        print("✅ Prompt library table initialized successfully")
    else:
        print("❌ Failed to initialize prompt library table")
