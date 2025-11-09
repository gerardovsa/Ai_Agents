#!/usr/bin/env python3
"""
Supabase Toolkit for AI Agents Migration
Based on SQL_Data_AI_UI_v5 database_cli.py and supabase_config.py

Features:
- Automatic credential loading from .env.master
- Connection testing and validation
- Database schema inspection
- Migration helpers
- Data verification tools
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("\nError: psycopg2 not installed")
    print("Install: pip install psycopg2-binary\n")
    sys.exit(1)


class SupabaseToolkit:
    """Comprehensive Supabase toolkit for AI Agents migration"""
    
    def __init__(self, project_url: str = None, service_key: str = None, db_url: str = None):
        """Initialize with credentials from .env.master or parameters"""
        
        # Try to load from .env.master if parameters not provided
        if not all([project_url, service_key, db_url]):
            self._load_from_env_master()
        else:
            self.project_url = project_url
            self.service_key = service_key
            self.db_url = db_url
        
        # Parse database connection details
        self._parse_db_url()
        self.conn = None
    
    def _load_from_env_master(self):
        """Load credentials from .env.master file"""
        env_master_path = Path(__file__).parent.parent / '.env.master'
        
        if not env_master_path.exists():
            print(f"\nError: .env.master not found at {env_master_path}")
            print("Please provide credentials manually or create .env.master file\n")
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
        self.project_url = credentials.get('SUPABASE_URL')
        self.service_key = credentials.get('SUPABASE_SERVICE_ROLE_SECRET')
        self.db_url = credentials.get('SUPABASE_DB_URL')
        self.project_name = credentials.get('SUPABASE_PROJECT_NAME')
        self.project_password = credentials.get('SUPABASE_PROJECT_PASSWORD')
        
        if not all([self.project_url, self.service_key, self.db_url]):
            print("\nError: Missing Supabase credentials in .env.master")
            print("Required:")
            print("  - SUPABASE_URL")
            print("  - SUPABASE_SERVICE_ROLE_SECRET")
            print("  - SUPABASE_DB_URL")
            sys.exit(1)
        
        print(f"✓ Loaded credentials for project: {self.project_name}")
    
    def _parse_db_url(self):
        """Parse PostgreSQL connection URL"""
        # Example: postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
        if not self.db_url:
            return
        
        try:
            # Remove postgresql:// prefix
            url_parts = self.db_url.replace('postgresql://', '')
            
            # Split user:password@host:port/database
            auth, rest = url_parts.split('@')
            self.db_user, self.db_password = auth.split(':')
            
            host_port, self.db_name = rest.split('/')
            self.db_host, self.db_port = host_port.split(':')
            
        except Exception as e:
            print(f"Warning: Could not parse database URL: {e}")
    
    def connect(self) -> bool:
        """Connect to Supabase PostgreSQL"""
        print("\n" + "="*80)
        print("Connecting to Supabase PostgreSQL...")
        print("="*80)
        print(f"Project: {self.project_name}")
        print(f"Host: {self.db_host}")
        print(f"Database: {self.db_name}")
        
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                sslmode='require'
            )
            self.conn.autocommit = False
            print("✓ Connected successfully\n")
            return True
        
        except Exception as e:
            print(f"✗ Connection failed: {e}\n")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("✓ Disconnected from database")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        result = {
            'success': False,
            'message': '',
            'details': {}
        }
        
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            # Test query
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            db_size = cursor.fetchone()[0]
            
            # Count schemas
            cursor.execute("SELECT count(*) FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema')")
            schema_count = cursor.fetchone()[0]
            
            result['success'] = True
            result['message'] = 'Connection test successful'
            result['details'] = {
                'postgresql_version': version,
                'database_size': db_size,
                'custom_schemas': schema_count
            }
            
            cursor.close()
            
        except Exception as e:
            result['message'] = f'Connection test failed: {str(e)}'
        
        return result
    
    def list_schemas(self) -> List[str]:
        """List all database schemas"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast', 'auth', 'extensions', 'graphql', 'graphql_public', 'net', 'pgsodium', 'pgsodium_masks', 'pgtle', 'realtime', 'storage', 'supabase_functions', 'supabase_migrations', 'vault')
            ORDER BY schema_name
        """)
        
        schemas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        return schemas
    
    def list_tables(self, schema: str = 'public') -> List[Dict[str, Any]]:
        """List all tables in a schema"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = %s
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema, schema))
        
        tables = cursor.fetchall()
        cursor.close()
        
        return [dict(row) for row in tables]
    
    def get_table_info(self, table_name: str, schema: str = 'public') -> Dict[str, Any]:
        """Get detailed information about a table"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        # Get columns
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table_name))
        
        columns = [dict(row) for row in cursor.fetchall()]
        
        # Get row count
        cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(table_name)
        ))
        row_count = cursor.fetchone()['count']
        
        # Get table size
        cursor.execute("""
            SELECT pg_size_pretty(pg_total_relation_size(%s::regclass))
        """, (f'{schema}.{table_name}',))
        table_size = cursor.fetchone()[0]
        
        cursor.close()
        
        return {
            'schema': schema,
            'table': table_name,
            'columns': columns,
            'row_count': row_count,
            'table_size': table_size
        }
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return results
        
        except Exception as e:
            cursor.close()
            raise Exception(f"Query failed: {str(e)}")
    
    def show_database_summary(self):
        """Show comprehensive database summary"""
        print("\n" + "="*80)
        print("SUPABASE DATABASE SUMMARY")
        print("="*80)
        
        # Connection test
        test_result = self.test_connection()
        if not test_result['success']:
            print(f"\n✗ {test_result['message']}\n")
            return
        
        print(f"\nProject: {self.project_name}")
        print(f"PostgreSQL Version: {test_result['details']['postgresql_version'][:50]}...")
        print(f"Database Size: {test_result['details']['database_size']}")
        print(f"Custom Schemas: {test_result['details']['custom_schemas']}")
        
        # List schemas
        print("\n" + "-"*80)
        print("SCHEMAS")
        print("-"*80)
        
        schemas = self.list_schemas()
        if schemas:
            for schema in schemas:
                print(f"  • {schema}")
                
                # Show tables in this schema
                tables = self.list_tables(schema)
                if tables:
                    for table in tables:
                        print(f"      - {table['table_name']} ({table['column_count']} columns)")
        else:
            print("  No custom schemas found (database is empty)")
        
        print("\n" + "="*80 + "\n")
    
    def verify_migration(self, expected_data: Dict[str, Dict[str, int]]):
        """
        Verify migration results match expected data
        
        Args:
            expected_data: Dict with schema -> {table -> row_count}
        """
        print("\n" + "="*80)
        print("MIGRATION VERIFICATION")
        print("="*80)
        
        all_match = True
        
        for schema, tables in expected_data.items():
            print(f"\nSchema: {schema}")
            print("-" * 60)
            
            for table_name, expected_count in tables.items():
                try:
                    info = self.get_table_info(table_name, schema)
                    actual_count = info['row_count']
                    
                    if expected_count == actual_count:
                        print(f"  ✓ {table_name}: {actual_count:,} rows (matches)")
                    else:
                        print(f"  ✗ {table_name}: Expected {expected_count:,}, got {actual_count:,}")
                        all_match = False
                
                except Exception as e:
                    print(f"  ✗ {table_name}: Error - {str(e)}")
                    all_match = False
        
        print("\n" + "="*80)
        if all_match:
            print("✓ ALL DATA VERIFIED SUCCESSFULLY")
        else:
            print("⚠ VERIFICATION FAILED - See errors above")
        print("="*80 + "\n")
        
        return all_match


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Supabase Toolkit for AI Agents')
    parser.add_argument('command', choices=['test', 'summary', 'schemas', 'tables', 'info', 'query'],
                       help='Command to execute')
    parser.add_argument('--schema', default='public', help='Schema name')
    parser.add_argument('--table', help='Table name')
    parser.add_argument('--query', help='SQL query to execute')
    
    args = parser.parse_args()
    
    # Initialize toolkit
    toolkit = SupabaseToolkit()
    
    try:
        if args.command == 'test':
            # Test connection
            result = toolkit.test_connection()
            print("\n" + "="*80)
            print("CONNECTION TEST")
            print("="*80)
            
            if result['success']:
                print(f"\n✓ {result['message']}")
                print(f"\nPostgreSQL Version: {result['details']['postgresql_version'][:60]}...")
                print(f"Database Size: {result['details']['database_size']}")
                print(f"Custom Schemas: {result['details']['custom_schemas']}")
            else:
                print(f"\n✗ {result['message']}")
            
            print("\n" + "="*80 + "\n")
        
        elif args.command == 'summary':
            # Show database summary
            toolkit.show_database_summary()
        
        elif args.command == 'schemas':
            # List schemas
            schemas = toolkit.list_schemas()
            print("\n" + "="*80)
            print("DATABASE SCHEMAS")
            print("="*80 + "\n")
            
            if schemas:
                for schema in schemas:
                    print(f"  • {schema}")
            else:
                print("  No custom schemas found")
            
            print("\n" + "="*80 + "\n")
        
        elif args.command == 'tables':
            # List tables in schema
            tables = toolkit.list_tables(args.schema)
            print("\n" + "="*80)
            print(f"TABLES IN SCHEMA: {args.schema}")
            print("="*80 + "\n")
            
            if tables:
                for table in tables:
                    print(f"  • {table['table_name']} ({table['column_count']} columns)")
            else:
                print(f"  No tables found in schema '{args.schema}'")
            
            print("\n" + "="*80 + "\n")
        
        elif args.command == 'info':
            # Get table info
            if not args.table:
                print("\nError: --table required for info command\n")
                sys.exit(1)
            
            info = toolkit.get_table_info(args.table, args.schema)
            print("\n" + "="*80)
            print(f"TABLE INFO: {info['schema']}.{info['table']}")
            print("="*80)
            print(f"\nRows: {info['row_count']:,}")
            print(f"Size: {info['table_size']}")
            print(f"\nColumns ({len(info['columns'])}):")
            
            for col in info['columns']:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
            
            print("\n" + "="*80 + "\n")
        
        elif args.command == 'query':
            # Execute query
            if not args.query:
                print("\nError: --query required for query command\n")
                sys.exit(1)
            
            results = toolkit.execute_query(args.query)
            print("\n" + "="*80)
            print(f"QUERY RESULTS ({len(results)} rows)")
            print("="*80 + "\n")
            
            if results:
                # Show first 10 results
                for i, row in enumerate(results[:10], 1):
                    print(f"Row {i}:")
                    for key, value in row.items():
                        print(f"  {key}: {value}")
                    print()
                
                if len(results) > 10:
                    print(f"... and {len(results) - 10} more rows\n")
            else:
                print("  No results\n")
            
            print("="*80 + "\n")
    
    finally:
        toolkit.disconnect()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
