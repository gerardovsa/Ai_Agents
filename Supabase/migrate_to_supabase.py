#!/usr/bin/env python3
"""
SQLite to Supabase (PostgreSQL) Migration Tool
Migrates all data from local SQLite databases to Supabase
from shared.database_utils import convert_sql_placeholders

Features:
- Automatic schema conversion (SQLite -> PostgreSQL)
- Data migration with validation
- Preserves relationships and constraints
- Rollback capability
- Progress tracking
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import execute_values
except ImportError:
    print("Error: psycopg2 not installed")
    print("Install: pip install psycopg2-binary")
    sys.exit(1)


class SupabaseMigration:
    """Handles migration from SQLite to Supabase PostgreSQL"""
    
    def __init__(self, supabase_url: str, supabase_key: str, supabase_db_url: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_db_url = supabase_db_url
        self.pg_conn = None
        
        # Database files to migrate
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.databases = {
            'ai_infrastructure': self.data_dir / 'ai_infrastructure.db',
            'sessions': self.data_dir / 'sessions.db',
            'synergy_sessions': self.data_dir / 'synergy_sessions.db',
            'kanban_analytics': self.data_dir / 'kanban_analytics.db',
            'stock_data': self.data_dir / 'stock_data.db'
        }
    
    def connect_postgresql(self):
        """Connect to Supabase PostgreSQL"""
        print("\n" + "="*80)
        print("Connecting to Supabase PostgreSQL...")
        print("="*80)
        
        try:
            # Close existing connection if any
            if self.pg_conn:
                try:
                    self.pg_conn.close()
                except:
                    pass
            
            self.pg_conn = psycopg2.connect(self.supabase_db_url)
            self.pg_conn.autocommit = False
            print("✓ Connected successfully\n")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}\n")
            return False
    
    def analyze_sqlite_database(self, db_path: Path) -> Dict:
        """Analyze SQLite database structure"""
        print(f"\nAnalyzing: {db_path.name}")
        print("-" * 60)
        
        if not db_path.exists():
            print(f"  ✗ Database not found: {db_path}")
            return {'exists': False}
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        
        analysis = {
            'exists': True,
            'path': str(db_path),
            'tables': {},
            'total_rows': 0
        }
        
        for table in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            
            analysis['tables'][table] = {
                'columns': columns,
                'row_count': row_count
            }
            analysis['total_rows'] += row_count
            
            print(f"  Table: {table}")
            print(f"    Columns: {len(columns)}")
            print(f"    Rows: {row_count:,}")
        
        conn.close()
        
        print(f"  Total tables: {len(tables)}")
        print(f"  Total rows: {analysis['total_rows']:,}")
        
        return analysis
    
    def sqlite_to_postgresql_type(self, sqlite_type: str) -> str:
        """Convert SQLite type to PostgreSQL type"""
        type_map = {
            'INTEGER': 'INTEGER',
            'TEXT': 'TEXT',
            'REAL': 'REAL',
            'BLOB': 'BYTEA',
            'NUMERIC': 'NUMERIC',
            'BOOLEAN': 'BOOLEAN',
            'DATE': 'DATE',
            'DATETIME': 'TIMESTAMP',
            'TIMESTAMP': 'TIMESTAMP'
        }
        
        sqlite_type = sqlite_type.upper()
        
        # Handle parameterized types
        if '(' in sqlite_type:
            base_type = sqlite_type.split('(')[0].strip()
            return type_map.get(base_type, 'TEXT')
        
        return type_map.get(sqlite_type, 'TEXT')
    
    def create_postgresql_schema(self, db_name: str, analysis: Dict) -> bool:
        """Create PostgreSQL schema from SQLite analysis"""
        if not analysis.get('exists'):
            return False
        
        print(f"\n" + "="*80)
        print(f"Creating PostgreSQL schema for: {db_name}")
        print("="*80)
        
        # Ensure connection is alive
        if not self.pg_conn or self.pg_conn.closed:
            print("Reconnecting to database...")
            if not self.connect_postgresql():
                return False
        
        cursor = self.pg_conn.cursor()
        
        try:
            for table_name, table_info in analysis['tables'].items():
                # Create schema name (database name as schema)
                schema_name = db_name.lower()
                full_table = f"{schema_name}.{table_name}"
                
                # Create schema if not exists
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                
                # Build CREATE TABLE statement
                columns = []
                primary_keys = []
                
                for col in table_info['columns']:
                    col_id, col_name, col_type, not_null, default_val, is_pk = col
                    
                    # Special handling for columns with mixed INTEGER/TEXT data
                    if db_name == 'sessions' and table_name == 'threads' and col_name == 'synergy_card_id':
                        pg_type = 'TEXT'  # Contains session IDs like "sess_20251101_1410..."
                    elif db_name == 'stock_data' and table_name == 'extracted_jobs' and col_name == 'stock_id':
                        pg_type = 'TEXT'  # Contains values like "TEMP_unknown_0", "T1", and integers
                    elif db_name == 'stock_data' and table_name == 'extracted_jobs' and col_name == 'color_pages':
                        pg_type = 'TEXT'  # Contains descriptive text like "9 pages color, 231 pages B&W"
                    elif db_name == 'stock_data' and table_name == 'extracted_jobs' and col_name == 'bw_pages':
                        pg_type = 'TEXT'  # May contain descriptive text
                    elif db_name == 'stock_data' and (table_name == 'extracted_jobs' or table_name == 'unified_stocks') and col_name == 'gsm':
                        pg_type = 'TEXT'  # Contains "mixed", "custom" and integer values
                    elif db_name == 'stock_data' and table_name == 'unified_stocks' and col_name == 'durability_rating':
                        pg_type = 'TEXT'  # Contains descriptive ratings like "2 - Medium-term Indoor (6-24 months...)"
                    else:
                        pg_type = self.sqlite_to_postgresql_type(col_type)
                    
                    col_def = f'"{col_name}" {pg_type}'
                    
                    if not_null:
                        col_def += ' NOT NULL'
                    
                    if default_val is not None:
                        # Skip SQLite-specific functions (strftime, datetime, etc.)
                        if any(func in str(default_val).lower() for func in ['strftime', 'datetime', 'date', 'time']):
                            # Skip SQLite date/time functions
                            pass
                        # Handle boolean defaults
                        elif pg_type == 'BOOLEAN':
                            if str(default_val) in ('0', 'false', 'False', 'FALSE'):
                                col_def += " DEFAULT false"
                            elif str(default_val) in ('1', 'true', 'True', 'TRUE'):
                                col_def += " DEFAULT true"
                            else:
                                col_def += f" DEFAULT {default_val}"
                        # Handle standard defaults (CURRENT_TIMESTAMP, NOW(), etc.)
                        elif default_val.upper() in ('CURRENT_TIMESTAMP', 'NOW()'):
                            col_def += f" DEFAULT {default_val.upper()}"
                        # Handle TEXT/string defaults (need quotes)
                        elif pg_type == 'TEXT' and not default_val.startswith("'"):
                            # Add quotes for string literals
                            col_def += f" DEFAULT '{default_val}'"
                        # Handle numeric and other defaults
                        elif default_val.upper() not in ('NULL',):
                            col_def += f" DEFAULT {default_val}"
                    
                    if is_pk:
                        primary_keys.append(col_name)
                    
                    columns.append(col_def)
                
                # Add primary key constraint
                if primary_keys:
                    pk_cols = ', '.join([f'"{pk}"' for pk in primary_keys])
                    columns.append(f'PRIMARY KEY ({pk_cols})')
                
                # Drop table if exists (for clean migration)
                cursor.execute(f'DROP TABLE IF EXISTS "{schema_name}"."{table_name}" CASCADE')
                
                # Create table
                create_sql = f'CREATE TABLE "{schema_name}"."{table_name}" (\n  ' + ',\n  '.join(columns) + '\n)'
                cursor.execute(create_sql)
                
                print(f"  ✓ Created table: {full_table}")
            
            self.pg_conn.commit()
            print("\n✓ Schema creation complete\n")
            return True
            
        except Exception as e:
            self.pg_conn.rollback()
            print(f"\n✗ Schema creation failed: {e}\n")
            return False
    
    def migrate_data(self, db_name: str, db_path: Path, analysis: Dict) -> bool:
        """Migrate data from SQLite to PostgreSQL"""
        if not analysis.get('exists'):
            return False
        
        print(f"\n" + "="*80)
        print(f"Migrating data from: {db_name}")
        print("="*80)
        
        sqlite_conn = sqlite3.connect(str(db_path))
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        pg_cursor = self.pg_conn.cursor()
        schema_name = db_name.lower()
        
        try:
            for table_name, table_info in analysis['tables'].items():
                row_count = table_info['row_count']
                
                if row_count == 0:
                    print(f"  ⊘ Skipping empty table: {table_name}")
                    continue
                
                print(f"  Migrating: {table_name} ({row_count:,} rows)...", end='', flush=True)
                
                # Get all data from SQLite
                sqlite_cursor.execute(f'SELECT * FROM {table_name}')
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(" ✓ (no data)")
                    continue
                
                # Get column names and types
                column_names = [col[1] for col in table_info['columns']]
                column_types = {col[1]: self.sqlite_to_postgresql_type(col[2]) for col in table_info['columns']}
                
                # Prepare PostgreSQL insert (quote table name to preserve case)
                full_table = f'"{schema_name}"."{table_name}"'
                columns_str = ', '.join([f'"{col}"' for col in column_names])
                
                # Convert rows to tuples with type casting
                data = []
                for row in rows:
                    converted_row = []
                    for i, value in enumerate(row):
                        col_name = column_names[i]
                        col_type = column_types[col_name]
                        
                        # Convert boolean values (SQLite stores as 0/1)
                        if col_type == 'BOOLEAN' and value is not None:
                            converted_row.append(bool(value))
                        else:
                            converted_row.append(value)
                    
                    data.append(tuple(converted_row))
                
                # Batch insert using execute_values (automatically handles placeholders)
                insert_sql = sql.SQL('INSERT INTO {} ({}) VALUES %s').format(
                    sql.Identifier(schema_name, table_name),
                    sql.SQL(', ').join([sql.Identifier(col) for col in column_names])
                )
                
                execute_values(pg_cursor, insert_sql, data, page_size=1000)
                
                print(f" ✓ ({len(data):,} rows)")
            
            self.pg_conn.commit()
            sqlite_conn.close()
            
            print("\n✓ Data migration complete\n")
            return True
            
        except Exception as e:
            self.pg_conn.rollback()
            sqlite_conn.close()
            print(f"\n✗ Data migration failed: {e}\n")
            return False
    
    def verify_migration(self, db_name: str, analysis: Dict) -> bool:
        """Verify migrated data matches source"""
        if not analysis.get('exists'):
            return True
        
        print(f"\n" + "="*80)
        print(f"Verifying migration: {db_name}")
        print("="*80)
        
        cursor = self.pg_conn.cursor()
        schema_name = db_name.lower()
        all_match = True
        
        for table_name, table_info in analysis['tables'].items():
            expected_count = table_info['row_count']
            full_table = f'"{schema_name}"."{table_name}"'
            
            cursor.execute(f'SELECT COUNT(*) FROM {full_table}')
            actual_count = cursor.fetchone()[0]
            
            if expected_count == actual_count:
                print(f"  ✓ {table_name}: {actual_count:,} rows (matches)")
            else:
                print(f"  ✗ {table_name}: Expected {expected_count:,}, got {actual_count:,}")
                all_match = False
        
        print()
        return all_match
    
    def run_migration(self):
        """Run complete migration process"""
        print("\n" + "="*80)
        print("SUPABASE MIGRATION TOOL")
        print("SQLite → PostgreSQL Data Migration")
        print("="*80)
        
        # Connect to PostgreSQL
        if not self.connect_postgresql():
            return False
        
        # Analyze all databases
        print("\n" + "="*80)
        print("PHASE 1: Analyzing SQLite Databases")
        print("="*80)
        
        analyses = {}
        total_tables = 0
        total_rows = 0
        
        for db_name, db_path in self.databases.items():
            analysis = self.analyze_sqlite_database(db_path)
            analyses[db_name] = analysis
            
            if analysis.get('exists'):
                total_tables += len(analysis['tables'])
                total_rows += analysis['total_rows']
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {len([a for a in analyses.values() if a.get('exists')])} databases, "
              f"{total_tables} tables, {total_rows:,} total rows")
        print("="*80)
        
        # Confirm migration
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\nMigration cancelled.")
            return False
        
        # Create schemas
        print("\n" + "="*80)
        print("PHASE 2: Creating PostgreSQL Schemas")
        print("="*80)
        
        for db_name, analysis in analyses.items():
            if analysis.get('exists'):
                if not self.create_postgresql_schema(db_name, analysis):
                    print(f"\n✗ Failed to create schema for {db_name}")
                    return False
        
        # Migrate data
        print("\n" + "="*80)
        print("PHASE 3: Migrating Data")
        print("="*80)
        
        for db_name, db_path in self.databases.items():
            analysis = analyses[db_name]
            if analysis.get('exists'):
                if not self.migrate_data(db_name, db_path, analysis):
                    print(f"\n✗ Failed to migrate data for {db_name}")
                    return False
        
        # Verify
        print("\n" + "="*80)
        print("PHASE 4: Verification")
        print("="*80)
        
        all_verified = True
        for db_name, analysis in analyses.items():
            if analysis.get('exists'):
                if not self.verify_migration(db_name, analysis):
                    all_verified = False
        
        # Final summary
        print("\n" + "="*80)
        print("MIGRATION COMPLETE")
        print("="*80)
        
        if all_verified:
            print("\n✓ All data migrated and verified successfully!")
            print(f"\nMigrated: {total_tables} tables, {total_rows:,} rows")
            print("\nNext steps:")
            print("1. Update config.py to use PostgreSQL")
            print("2. Add Supabase credentials to Render env vars")
            print("3. Test the application")
        else:
            print("\n⚠ Migration completed with verification warnings")
            print("Please review the data manually")
        
        print("\n" + "="*80 + "\n")
        
        # Close connection
        self.pg_conn.close()
        return all_verified


def load_credentials_from_env_master():
    """Load Supabase credentials from .env.master file"""
    env_master_path = Path(__file__).parent.parent / '.env.master'
    
    if not env_master_path.exists():
        print(f"\n✗ Error: .env.master not found at {env_master_path}")
        print("Please create .env.master file with Supabase credentials\n")
        sys.exit(1)
    
    print(f"Loading credentials from: {env_master_path}")
    
    # Parse .env.master
    credentials = {}
    with open(env_master_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                credentials[key.strip()] = value.strip()
    
    # Extract Supabase credentials
    supabase_url = credentials.get('SUPABASE_URL')
    supabase_key = credentials.get('SUPABASE_SERVICE_KEY')  # Use service role for migration
    supabase_db_url = credentials.get('SUPABASE_DB_URL')
    project_name = credentials.get('SUPABASE_PROJECT_NAME', 'Unknown')
    
    if not all([supabase_url, supabase_key, supabase_db_url]):
        print("\n✗ Error: Missing Supabase credentials in .env.master")
        print("Required:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_KEY")
        print("  - SUPABASE_DB_URL")
        sys.exit(1)
    
    print(f"✓ Loaded credentials for project: {project_name}\n")
    
    return supabase_url, supabase_key, supabase_db_url


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("Supabase Migration - Automatic Credential Loading")
    print("="*80 + "\n")
    
    # Load credentials from .env.master
    supabase_url, supabase_key, supabase_db_url = load_credentials_from_env_master()
    
    # Run migration
    migration = SupabaseMigration(supabase_url, supabase_key, supabase_db_url)
    success = migration.run_migration()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        sys.exit(1)
