"""
Database Setup Script - Workspace Schema

Creates/updates database schema for multi-user workspace system.

NO DATA MIGRATION - Only adds columns and creates new tables.

Usage:
    python scripts/database/setup_workspace_schema.py
    python scripts/database/setup_workspace_schema.py --rollback
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class WorkspaceSchemaSetup:
    """
    Workspace Schema Setup
    
    Creates new tables and adds columns for multi-user workspace support.
    """
    
    def __init__(self):
        """Initialize with database path"""
        root_dir = Path(__file__).parent.parent.parent
        self.db_path = root_dir / 'data' / 'ai_infrastructure.db'
        print(f"Database: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def check_column_exists(self, table: str, column: str) -> bool:
        """Check if column exists in table"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row['name'] for row in cursor.fetchall()]
        conn.close()
        
        return column in columns
    
    def check_table_exists(self, table: str) -> bool:
        """Check if table exists"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def add_slug_to_workspaces(self):
        """Add slug column to workspaces table"""
        print("\n[1/5] Adding slug column to workspaces table...")
        
        if self.check_column_exists('workspaces', 'slug'):
            print("  - Column 'slug' already exists, skipping")
            return
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Add slug column
            cursor.execute("ALTER TABLE workspaces ADD COLUMN slug TEXT")
            
            # Create unique index
            cursor.execute("CREATE UNIQUE INDEX idx_workspaces_slug ON workspaces(slug)")
            
            conn.commit()
            print("  - Added 'slug' column with unique index")
            print("  - NOTE: Existing workspaces need slugs generated manually")
        
        except Exception as e:
            conn.rollback()
            print(f"  - ERROR: {e}")
            raise
        finally:
            conn.close()
    
    def add_slug_to_threads(self):
        """Add slug column to threads table"""
        print("\n[2/5] Adding slug column to threads table...")
        
        # Check if threads table exists
        if not self.check_table_exists('threads'):
            print("  - Table 'threads' does not exist, skipping")
            print("  - NOTE: Create threads table first or add slug later")
            return
        
        if self.check_column_exists('threads', 'slug'):
            print("  - Column 'slug' already exists, skipping")
            return
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Add slug column
            cursor.execute("ALTER TABLE threads ADD COLUMN slug TEXT")
            
            # Create index (not unique - workspace_id + slug is unique)
            cursor.execute("CREATE INDEX idx_threads_slug ON threads(workspace_id, slug)")
            
            conn.commit()
            print("  - Added 'slug' column with composite index")
            print("  - NOTE: Existing threads need slugs generated manually")
        
        except Exception as e:
            conn.rollback()
            print(f"  - ERROR: {e}")
            raise
        finally:
            conn.close()
    
    def create_workspace_users_table(self):
        """Create workspace_users table"""
        print("\n[3/5] Creating workspace_users table...")
        
        if self.check_table_exists('workspace_users'):
            print("  - Table 'workspace_users' already exists, skipping")
            return
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Create table
            cursor.execute("""
                CREATE TABLE workspace_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    added_by_user_id INTEGER NOT NULL,
                    added_at TEXT NOT NULL,
                    removed_at TEXT,
                    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (added_by_user_id) REFERENCES users(id),
                    UNIQUE(workspace_id, user_id)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX idx_workspace_users_workspace 
                ON workspace_users(workspace_id)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_workspace_users_user 
                ON workspace_users(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_workspace_users_active 
                ON workspace_users(workspace_id, user_id) 
                WHERE removed_at IS NULL
            """)
            
            conn.commit()
            print("  - Created 'workspace_users' table with 3 indexes")
            print("  - Indexes: workspace_id, user_id, active members")
        
        except Exception as e:
            conn.rollback()
            print(f"  - ERROR: {e}")
            raise
        finally:
            conn.close()
    
    def create_workspace_invitations_table(self):
        """Create workspace_invitations table"""
        print("\n[4/5] Creating workspace_invitations table...")
        
        if self.check_table_exists('workspace_invitations'):
            print("  - Table 'workspace_invitations' already exists, skipping")
            return
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Create table
            cursor.execute("""
                CREATE TABLE workspace_invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_id INTEGER NOT NULL,
                    invited_user_id INTEGER,
                    invited_email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL,
                    invited_by_user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    responded_at TEXT,
                    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                    FOREIGN KEY (invited_user_id) REFERENCES users(id),
                    FOREIGN KEY (invited_by_user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE UNIQUE INDEX idx_invitations_token 
                ON workspace_invitations(token)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_invitations_workspace 
                ON workspace_invitations(workspace_id)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_invitations_user 
                ON workspace_invitations(invited_user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_invitations_email 
                ON workspace_invitations(invited_email)
            """)
            
            cursor.execute("""
                CREATE INDEX idx_invitations_status 
                ON workspace_invitations(status, expires_at)
            """)
            
            conn.commit()
            print("  - Created 'workspace_invitations' table with 5 indexes")
            print("  - Indexes: token, workspace_id, user_id, email, status")
        
        except Exception as e:
            conn.rollback()
            print(f"  - ERROR: {e}")
            raise
        finally:
            conn.close()
    
    def verify_schema(self):
        """Verify all changes applied successfully"""
        print("\n[5/5] Verifying schema changes...")
        
        checks = [
            ('workspaces.slug', lambda: self.check_column_exists('workspaces', 'slug')),
            ('threads.slug', lambda: self.check_column_exists('threads', 'slug')),
            ('workspace_users table', lambda: self.check_table_exists('workspace_users')),
            ('workspace_invitations table', lambda: self.check_table_exists('workspace_invitations'))
        ]
        
        all_good = True
        for name, check_func in checks:
            result = check_func()
            status = "OK" if result else "MISSING"
            symbol = "  " if result else "  "
            print(f"  {symbol} {name}: {status}")
            if not result:
                all_good = False
        
        return all_good
    
    def rollback(self):
        """
        Rollback changes (DROP new tables, remove slug columns)
        
        WARNING: This will delete all workspace_users and workspace_invitations data!
        """
        print("\n ROLLBACK - Removing workspace schema changes...")
        print("WARNING: This will delete workspace_users and workspace_invitations tables!")
        
        confirm = input("\nType 'YES' to confirm rollback: ")
        if confirm != 'YES':
            print("Rollback cancelled")
            return
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Drop tables
            if self.check_table_exists('workspace_invitations'):
                cursor.execute("DROP TABLE workspace_invitations")
                print("  - Dropped 'workspace_invitations' table")
            
            if self.check_table_exists('workspace_users'):
                cursor.execute("DROP TABLE workspace_users")
                print("  - Dropped 'workspace_users' table")
            
            # Note: Cannot easily drop columns in SQLite without recreating table
            # Just document that slug columns exist but are unused
            
            conn.commit()
            print("\n  Rollback complete!")
            print("  NOTE: Slug columns remain (SQLite limitation)")
            print("        They will be ignored by old code")
        
        except Exception as e:
            conn.rollback()
            print(f"\n  ERROR during rollback: {e}")
            raise
        finally:
            conn.close()
    
    def setup(self):
        """Run complete setup"""
        print("\n" + "="*60)
        print("WORKSPACE SCHEMA SETUP")
        print("="*60)
        print(f"Database: {self.db_path}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # Check database exists
            if not self.db_path.exists():
                print(f"\n ERROR: Database not found: {self.db_path}")
                print("       Please create database first")
                return False
            
            # Run setup steps
            self.add_slug_to_workspaces()
            self.add_slug_to_threads()
            self.create_workspace_users_table()
            self.create_workspace_invitations_table()
            
            # Verify
            success = self.verify_schema()
            
            print("\n" + "="*60)
            if success:
                print(" SUCCESS - All schema changes applied!")
                print("="*60)
                print("\nNext steps:")
                print("  1. Generate slugs for existing workspaces")
                print("  2. Generate slugs for existing threads")
                print("  3. Add workspace members (optional)")
                print("  4. Test workspace API endpoints")
            else:
                print(" WARNING - Some changes may have failed")
                print("="*60)
                print("         Check error messages above")
            
            return success
        
        except Exception as e:
            print(f"\n ERROR: Setup failed: {e}")
            return False


def main():
    """Main entry point"""
    setup = WorkspaceSchemaSetup()
    
    # Check for rollback flag
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        setup.rollback()
    else:
        setup.setup()


if __name__ == '__main__':
    main()
