"""
Database Schema Manager
========================

Handles all database schema operations:
- View current schema
- Create missing tables
- Migrate schema versions
- Export/Import schemas

REFACTORED VERSION - 2026-01-01
- Fixed all cursor leaks using context managers
- Added proper error handling
- Improved type hints
- Better logging and reporting
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from contextlib import contextmanager


class SchemaManager:
    """Manage database schema operations with proper resource management"""
    
    # CORE SCHEMA DEFINITION - Single source of truth
    SCHEMA_VERSION = "1.0.0"
    
    TABLES = {
        # ============================================================
        # USERS & AUTHENTICATION
        # ============================================================
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                role TEXT DEFAULT 'user',
                primary_gmail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                is_primary BOOLEAN DEFAULT 0
            )
        """,
        
        "user_sessions": """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        
        # ============================================================
        # PLATFORM CREDENTIALS & OAUTH
        # ============================================================
        "user_platform_credentials": """
            CREATE TABLE IF NOT EXISTS user_platform_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                credential_type TEXT NOT NULL,
                credential_key TEXT,
                credential_value TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, platform, credential_type)
            )
        """,
        
        "user_gmail_accounts": """
            CREATE TABLE IF NOT EXISTS user_gmail_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                gmail_address TEXT UNIQUE NOT NULL,
                display_name TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expiry TIMESTAMP,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        
        "user_email_aliases": """
            CREATE TABLE IF NOT EXISTS user_email_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                alias_email TEXT UNIQUE NOT NULL,
                oauth_provider TEXT,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        
        # ============================================================
        # WORKSPACES & ORGANIZATION
        # ============================================================
        "workspaces": """
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        
        # ============================================================
        # ACCOUNT LINKING
        # ============================================================
        "user_account_links": """
            CREATE TABLE IF NOT EXISTS user_account_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_user_id INTEGER NOT NULL,
                linked_user_id INTEGER NOT NULL,
                linked_email TEXT NOT NULL,
                link_type TEXT DEFAULT 'gmail',
                link_status TEXT DEFAULT 'pending',
                link_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP,
                FOREIGN KEY (primary_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (linked_user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(primary_user_id, linked_email)
            )
        """,
        
        "account_link_requests": """
            CREATE TABLE IF NOT EXISTS account_link_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_email TEXT NOT NULL,
                link_token TEXT UNIQUE NOT NULL,
                request_type TEXT DEFAULT 'gmail',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        
        # ============================================================
        # KANBAN TASK SYNC
        # ============================================================
        "kanban_task_links": """
            CREATE TABLE IF NOT EXISTS kanban_task_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                agent_name TEXT,
                work_session_id TEXT,
                kanban_session_id TEXT,
                kanban_title TEXT,
                kanban_status TEXT,
                kanban_column TEXT,
                sync_direction TEXT DEFAULT 'bidirectional',
                auto_sync_enabled BOOLEAN DEFAULT 1,
                agent_work_status TEXT,
                last_synced_at TEXT,
                sync_status TEXT DEFAULT 'pending',
                last_error TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                notes TEXT
            )
        """,
        
        # ============================================================
        # TRANSCRIPTION STORAGE
        # ============================================================
        "user_transcriptions": """
            CREATE TABLE IF NOT EXISTS user_transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                source_type TEXT DEFAULT 'recording',
                transcript_text TEXT,
                confidence REAL,
                language TEXT,
                duration_seconds REAL,
                word_count INTEGER,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """,

        "transcription_uploads": """
            CREATE TABLE IF NOT EXISTS transcription_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transcription_id INTEGER NOT NULL,
                filename TEXT,
                file_size INTEGER,
                file_type TEXT,
                mime_type TEXT,
                original_duration REAL,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transcription_id) REFERENCES user_transcriptions(id) ON DELETE CASCADE
            )
        """,

        # ============================================================
        # SCHEMA VERSION TRACKING
        # ============================================================
        "schema_versions": """
            CREATE TABLE IF NOT EXISTS schema_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                migration_script TEXT
            )
        """
    }
    
    # Indexes for performance
    INDEXES = {
        "idx_users_email": "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "idx_users_username": "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "idx_sessions_token": "CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token)",
        "idx_sessions_user": "CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)",
        "idx_credentials_user": "CREATE INDEX IF NOT EXISTS idx_credentials_user ON user_platform_credentials(user_id)",
        "idx_credentials_platform": "CREATE INDEX IF NOT EXISTS idx_credentials_platform ON user_platform_credentials(platform)",
        "idx_user_transcriptions_user_id": "CREATE INDEX IF NOT EXISTS idx_user_transcriptions_user_id ON user_transcriptions(user_id)",
        "idx_user_transcriptions_created_at": "CREATE INDEX IF NOT EXISTS idx_user_transcriptions_created_at ON user_transcriptions(created_at)",
        "idx_transcription_uploads_transcription_id": "CREATE INDEX IF NOT EXISTS idx_transcription_uploads_transcription_id ON transcription_uploads(transcription_id)"
    }
    
    def __init__(self, db_path: str = "ai_infrastructure.db"):
        """Initialize schema manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Ensure database file exists"""
        db_file = Path(self.db_path)
        if not db_file.parent.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_existing_tables(self) -> List[str]:
        """Get list of existing tables
        
        Returns:
            List of table names
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema for specific table
        
        Args:
            table_name: Name of table to inspect
            
        Returns:
            List of column information dictionaries
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = []
                
                for row in cursor.fetchall():
                    columns.append({
                        'cid': row[0],
                        'name': row[1],
                        'type': row[2],
                        'notnull': bool(row[3]),
                        'default': row[4],
                        'pk': bool(row[5])
                    })
                
        return columns
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for table
        
        Args:
            table_name: Name of table to count
            
        Returns:
            Number of rows in table
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
        return count
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists
        
        Args:
            table_name: Name of table to check
            
        Returns:
            True if table exists
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                exists = cursor.fetchone() is not None
                
        return exists
    
    def create_all_tables(self) -> Dict[str, bool]:
        """Create all tables from schema definition
        
        Returns:
            Dictionary mapping table names to success status
        """
        results = {}
        errors = {}
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Create tables
                for table_name, create_sql in self.TABLES.items():
                    try:
                        cursor.execute(create_sql)
                        results[table_name] = True
                        print(f"✅ Created table: {table_name}")
                    except Exception as e:
                        results[table_name] = False
                        errors[table_name] = str(e)
                        print(f"❌ Error creating {table_name}: {e}")
                
                # Create indexes
                for idx_name, idx_sql in self.INDEXES.items():
                    try:
                        cursor.execute(idx_sql)
                        print(f"✅ Created index: {idx_name}")
                    except Exception as e:
                        print(f"⚠️  Warning creating index {idx_name}: {e}")
                
                # Record schema version
                try:
                    cursor.execute("""
                        INSERT INTO schema_versions (version, description)
                        VALUES (?, ?)
                    """, (self.SCHEMA_VERSION, "Initial schema creation"))
                    print(f"✅ Recorded schema version: {self.SCHEMA_VERSION}")
                except Exception as e:
                    print(f"⚠️  Could not record schema version: {e}")
        
        if errors:
            print("\n⚠️  Errors occurred:")
            for table, error in errors.items():
                print(f"  - {table}: {error}")
        
        return results
    
    def create_missing_tables(self) -> Dict[str, bool]:
        """Create only missing tables
        
        Returns:
            Dictionary mapping created table names to success status
        """
        missing = self.check_missing_tables()
        
        if not missing:
            print("✅ All tables exist. Nothing to create.")
            return {}
        
        print(f"Creating {len(missing)} missing tables...")
        results = {}
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                for table_name in missing:
                    if table_name in self.TABLES:
                        try:
                            cursor.execute(self.TABLES[table_name])
                            results[table_name] = True
                            print(f"✅ Created table: {table_name}")
                        except Exception as e:
                            results[table_name] = False
                            print(f"❌ Error creating {table_name}: {e}")
        
        return results
    
    def view_schema(self, detailed: bool = False) -> Dict[str, Any]:
        """View current database schema
        
        Args:
            detailed: Include column information
            
        Returns:
            Dictionary with schema information
        """
        existing_tables = self.get_existing_tables()
        
        schema_info = {
            'database': self.db_path,
            'version': self.SCHEMA_VERSION,
            'current_db_version': self.get_schema_version(),
            'total_tables': len(existing_tables),
            'tables': {}
        }
        
        for table in existing_tables:
            table_info = {
                'exists': True,
                'row_count': self.get_table_count(table)
            }
            
            if detailed:
                table_info['columns'] = self.get_table_schema(table)
            
            schema_info['tables'][table] = table_info
        
        return schema_info
    
    def check_missing_tables(self) -> List[str]:
        """Check which tables are missing from schema
        
        Returns:
            List of missing table names
        """
        existing = set(self.get_existing_tables())
        required = set(self.TABLES.keys())
        missing = required - existing
        return sorted(list(missing))
    
    def check_extra_tables(self) -> List[str]:
        """Check which tables exist but aren't in schema definition
        
        Returns:
            List of extra table names
        """
        existing = set(self.get_existing_tables())
        required = set(self.TABLES.keys())
        extra = existing - required
        return sorted(list(extra))
    
    def export_schema(self, output_file: str = "schema_export.json") -> str:
        """Export complete schema to JSON
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            Path to exported file
        """
        schema_info = self.view_schema(detailed=True)
        
        # Add export metadata
        schema_info['exported_at'] = datetime.now().isoformat()
        schema_info['exported_by'] = 'SchemaManager'
        
        with open(output_file, 'w') as f:
            json.dump(schema_info, f, indent=2, default=str)
        
        print(f"✅ Schema exported to: {output_file}")
        return output_file
    
    def get_schema_version(self) -> Optional[str]:
        """Get current schema version from database
        
        Returns:
            Version string or None if not found
        """
        if not self.table_exists('schema_versions'):
            return None
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute("""
                        SELECT version FROM schema_versions 
                        ORDER BY applied_at DESC LIMIT 1
                    """)
                    result = cursor.fetchone()
                    
            return result[0] if result else None
        except Exception as e:
            print(f"⚠️  Could not get schema version: {e}")
            return None
    
    def record_migration(self, version: str, description: str, 
                        migration_script: Optional[str] = None) -> bool:
        """Record a schema migration
        
        Args:
            version: Version string
            description: Migration description
            migration_script: Optional SQL script that was executed
            
        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute("""
                        INSERT INTO schema_versions 
                        (version, description, migration_script)
                        VALUES (?, ?, ?)
                    """, (version, description, migration_script))
                    
            print(f"✅ Recorded migration: {version}")
            return True
        except Exception as e:
            print(f"❌ Failed to record migration: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history
        
        Returns:
            List of migration records
        """
        if not self.table_exists('schema_versions'):
            return []
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT id, version, applied_at, description
                    FROM schema_versions
                    ORDER BY applied_at DESC
                """)
                
                migrations = []
                for row in cursor.fetchall():
                    migrations.append({
                        'id': row[0],
                        'version': row[1],
                        'applied_at': row[2],
                        'description': row[3]
                    })
                
        return migrations
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate current schema against definition
        
        Returns:
            Dictionary with validation results
        """
        missing = self.check_missing_tables()
        extra = self.check_extra_tables()
        
        validation = {
            'valid': len(missing) == 0,
            'missing_tables': missing,
            'extra_tables': extra,
            'total_issues': len(missing) + len(extra)
        }
        
        return validation
    
    def print_schema_summary(self) -> None:
        """Print formatted schema summary"""
        schema = self.view_schema()
        
        print("\n" + "=" * 70)
        print("DATABASE SCHEMA SUMMARY".center(70))
        print("=" * 70)
        print(f"Database File: {schema['database']}")
        print(f"Schema Version: {schema['version']}")
        print(f"Current DB Version: {schema.get('current_db_version', 'Not set')}")
        print(f"Total Tables: {schema['total_tables']}")
        
        # Check for issues
        validation = self.validate_schema()
        if not validation['valid']:
            print(f"\n⚠️  Schema Issues Found: {validation['total_issues']}")
            if validation['missing_tables']:
                print(f"  Missing tables: {', '.join(validation['missing_tables'])}")
            if validation['extra_tables']:
                print(f"  Extra tables: {', '.join(validation['extra_tables'])}")
        else:
            print("\n✅ Schema is valid")
        
        # Group tables by category
        categories = {
            'Users & Auth': ['users', 'user_sessions'],
            'Platform Credentials': [
                'user_platform_credentials', 
                'user_gmail_accounts', 
                'user_email_aliases'
            ],
            'Workspaces': ['workspaces'],
            'Account Linking': ['user_account_links', 'account_link_requests'],
            'Kanban Sync': ['kanban_task_links'],
            'Transcriptions': ['user_transcriptions', 'transcription_uploads'],
            'System': ['schema_versions']
        }
        
        for category, tables in categories.items():
            print(f"\n📂 {category}")
            for table in tables:
                if table in schema['tables']:
                    info = schema['tables'][table]
                    status = "✅" if info['exists'] else "❌"
                    print(f"  {status} {table:35s} ({info['row_count']:>6} rows)")
                else:
                    print(f"  ❌ {table:35s} (MISSING)")
        
        print("\n" + "=" * 70 + "\n")
    
    def print_migration_history(self) -> None:
        """Print migration history"""
        migrations = self.get_migration_history()
        
        if not migrations:
            print("No migration history found.")
            return
        
        print("\n" + "=" * 70)
        print("MIGRATION HISTORY".center(70))
        print("=" * 70)
        
        for migration in migrations:
            print(f"\n📋 Version: {migration['version']}")
            print(f"   Applied: {migration['applied_at']}")
            print(f"   Description: {migration['description']}")
        
        print("\n" + "=" * 70 + "\n")


def main():
    """Main CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage: python schema_manager.py <command> [options]

Commands:
  view              - View current schema
  view-detailed     - View schema with column details
  create            - Create all missing tables
  create-all        - Create all tables (including existing)
  validate          - Validate schema against definition
  export [file]     - Export schema to JSON
  migrations        - Show migration history
  
Examples:
  python schema_manager.py view
  python schema_manager.py create
  python schema_manager.py export my_schema.json
        """)
        return
    
    command = sys.argv[1].lower()
    manager = SchemaManager()
    
    if command == 'view':
        manager.print_schema_summary()
        
    elif command == 'view-detailed':
        schema = manager.view_schema(detailed=True)
        print(json.dumps(schema, indent=2, default=str))
        
    elif command == 'create':
        results = manager.create_missing_tables()
        print(f"\n✅ Created {sum(results.values())} tables")
        
    elif command == 'create-all':
        results = manager.create_all_tables()
        print(f"\n✅ Created {sum(results.values())} tables")
        
    elif command == 'validate':
        validation = manager.validate_schema()
        if validation['valid']:
            print("✅ Schema is valid")
        else:
            print(f"❌ Schema has {validation['total_issues']} issues")
            if validation['missing_tables']:
                print(f"Missing: {', '.join(validation['missing_tables'])}")
            if validation['extra_tables']:
                print(f"Extra: {', '.join(validation['extra_tables'])}")
        
    elif command == 'export':
        output_file = sys.argv[2] if len(sys.argv) > 2 else "schema_export.json"
        manager.export_schema(output_file)
        
    elif command == 'migrations':
        manager.print_migration_history()
        
    else:
        print(f"❌ Unknown command: {command}")
        return


if __name__ == "__main__":
    main()