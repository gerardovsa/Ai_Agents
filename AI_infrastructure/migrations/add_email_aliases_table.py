"""
Database Migration: Add Email Aliases Support
Date: October 28, 2025
Purpose: Enable users to link multiple email addresses to a single account

Strategy #2: Account Aliases
- Users have one primary email in users.email
- Additional emails stored in user_email_aliases table as pointers
- Allows login with any linked email → same account data
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = 'C:/Users/gpoli/GIT/AI_agents/AI_infrastructure/ai_infrastructure.db'

def migrate_up():
    """Create user_email_aliases table"""
    
    print("🚀 Starting migration: Add Email Aliases Support")
    print(f"📂 Database: {DB_PATH}")
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create user_email_aliases table
        print("📋 Creating user_email_aliases table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_email_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                alias_email TEXT UNIQUE NOT NULL,
                oauth_provider TEXT NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        print("🔍 Creating indexes for fast lookup...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alias_email 
            ON user_email_aliases(alias_email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id_aliases 
            ON user_email_aliases(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_oauth_provider 
            ON user_email_aliases(oauth_provider)
        ''')
        
        # Commit changes
        conn.commit()
        
        # Verify table was created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_email_aliases'
        """)
        
        if cursor.fetchone():
            print("✅ user_email_aliases table created successfully!")
            
            # Show table schema
            cursor.execute("PRAGMA table_info(user_email_aliases)")
            columns = cursor.fetchall()
            print("\n📊 Table Schema:")
            for col in columns:
                print(f"   - {col[1]}: {col[2]}")
            
            # Show indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='user_email_aliases'
            """)
            indexes = cursor.fetchall()
            print("\n🔍 Indexes:")
            for idx in indexes:
                print(f"   - {idx[0]}")
            
            print("\n✅ Migration completed successfully!")
            return True
        else:
            print("❌ Error: Table was not created")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def migrate_down():
    """Remove user_email_aliases table (rollback)"""
    
    print("⚠️  Rolling back migration: Remove Email Aliases")
    print(f"📂 Database: {DB_PATH}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Drop indexes first
        print("🗑️  Dropping indexes...")
        cursor.execute("DROP INDEX IF EXISTS idx_alias_email")
        cursor.execute("DROP INDEX IF EXISTS idx_user_id_aliases")
        cursor.execute("DROP INDEX IF EXISTS idx_oauth_provider")
        
        # Drop table
        print("🗑️  Dropping user_email_aliases table...")
        cursor.execute("DROP TABLE IF EXISTS user_email_aliases")
        
        conn.commit()
        print("✅ Migration rolled back successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Rollback error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_migration():
    """Verify migration was applied correctly"""
    
    print("\n🔍 Verifying migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_email_aliases'
        """)
        
        if not cursor.fetchone():
            print("❌ Verification failed: Table not found")
            return False
        
        # Check required columns
        cursor.execute("PRAGMA table_info(user_email_aliases)")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        required_columns = {
            'id': 'INTEGER',
            'user_id': 'INTEGER',
            'alias_email': 'TEXT',
            'oauth_provider': 'TEXT',
            'is_primary': 'BOOLEAN',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                print(f"❌ Verification failed: Missing column '{col_name}'")
                return False
        
        # Check indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='user_email_aliases'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        required_indexes = ['idx_alias_email', 'idx_user_id_aliases', 'idx_oauth_provider']
        for idx in required_indexes:
            if idx not in indexes:
                print(f"⚠️  Warning: Index '{idx}' not found")
        
        print("✅ Migration verified successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Verification error: {e}")
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'down':
        success = migrate_down()
    elif len(sys.argv) > 1 and sys.argv[1] == 'verify':
        success = verify_migration()
    else:
        success = migrate_up()
        if success:
            verify_migration()
    
    sys.exit(0 if success else 1)
