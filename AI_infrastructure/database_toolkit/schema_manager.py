"""
Database Schema Manager
========================

Handles all database schema operations:
- View current schema
- Create missing tables
- Migrate schema versions
- Export/Import schemas
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class SchemaManager:
    """Manage database schema operations"""
    
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
        # KANBAN TASK SYNC (Future Feature)
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
                source_type TEXT DEFAULT 'recording', -- recording | upload
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
        """Initialize schema manager"""
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_existing_tables(self) -> List[str]:
        """Get list of existing tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Tuple]:
        """Get schema for specific table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        conn.close()
        return schema
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def create_all_tables(self) -> Dict[str, bool]:
        """Create all tables from schema definition"""
        conn = self.get_connection()
        cursor = conn.cursor()
        results = {}
        
        # Create tables
        for table_name, create_sql in self.TABLES.items():
            try:
                cursor.execute(create_sql)
                results[table_name] = True
            except Exception as e:
                results[table_name] = False
                print(f" Error creating {table_name}: {e}")
        
        # Create indexes
        for idx_name, idx_sql in self.INDEXES.items():
            try:
                cursor.execute(idx_sql)
            except Exception as e:
                print(f"⚠️ Warning creating index {idx_name}: {e}")
        
        # Record schema version
        try:
            cursor.execute("""
                INSERT INTO schema_versions (version, description)
                VALUES (%s, %s)
            """, (self.SCHEMA_VERSION, "Initial schema creation"))
        except:
            pass  # Table might not exist yet
        
        conn.commit()
        conn.close()
        
        return results
    
    def view_schema(self, detailed: bool = False) -> Dict:
        """View current database schema"""
        existing_tables = self.get_existing_tables()
        
        schema_info = {
            'database': self.db_path,
            'version': self.SCHEMA_VERSION,
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
        """Check which tables are missing from schema"""
        existing = set(self.get_existing_tables())
        required = set(self.TABLES.keys())
        missing = required - existing
        return list(missing)
    
    def export_schema(self, output_file: str = "schema_export.json"):
        """Export complete schema to JSON"""
        schema_info = self.view_schema(detailed=True)
        
        with open(output_file, 'w') as f:
            json.dump(schema_info, f, indent=2, default=str)
        
        return output_file
    
    def get_schema_version(self) -> Optional[str]:
        """Get current schema version from database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except:
            return None
    
    def print_schema_summary(self):
        """Print formatted schema summary"""
        schema = self.view_schema()
        
        print("=" * 70)
        print("DATABASE SCHEMA SUMMARY")
        print("=" * 70)
        print(f"Database: {schema['database']}")
        print(f"Schema Version: {schema['version']}")
        print(f"Total Tables: {schema['total_tables']}")
        print()
        
        # Group tables by category
        categories = {
            'Users & Auth': ['users', 'user_sessions'],
            'Platform Credentials': ['user_platform_credentials', 'user_gmail_accounts', 'user_email_aliases'],
            'Workspaces': ['workspaces'],
            'Account Linking': ['user_account_links', 'account_link_requests'],
            'Kanban Sync': ['kanban_task_links'],
            'System': ['schema_versions']
        }
        
        for category, tables in categories.items():
            print(f"\n📂 {category}")
            for table in tables:
                if table in schema['tables']:
                    info = schema['tables'][table]
                    status = "" if info['exists'] else ""
                    print(f"  {status} {table:30s} ({info['row_count']:>5} rows)")
                else:
                    print(f"   {table:30s} (MISSING)")
        
        print()
        print("=" * 70)


if __name__ == "__main__":
    # Test schema manager
    manager = SchemaManager()
    manager.print_schema_summary()
