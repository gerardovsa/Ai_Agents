"""
Complete Database and API System Structure Visualizer with Supabase Support
Version 2.0 - January 2025

Analyzes both SQLite (local) and Supabase PostgreSQL (production) databases
Compares schemas, detects inconsistencies, validates API routes
"""

import sqlite3
from pathlib import Path
import sys
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("WARNING: psycopg2 not available. Supabase analysis will be skipped.")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class SupabaseConnection:
    """Handle Supabase PostgreSQL connections"""
    
    def __init__(self):
        self.conn = None
        self.credentials = self._load_credentials()
        
    def _load_credentials(self) -> Optional[Dict[str, str]]:
        """Load Supabase credentials from .env.master"""
        if not DOTENV_AVAILABLE or not PSYCOPG2_AVAILABLE:
            return None
            
        env_path = Path(__file__).parent.parent / '.env.master'
        if not env_path.exists():
            print(f"WARNING: .env.master not found at {env_path}")
            return None
        
        # Parse .env.master
        credentials = {}
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
        
        # Extract database URL
        db_url = credentials.get('SUPABASE_DB_URL')
        if not db_url:
            return None
        
        try:
            # Parse: postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
            url_parts = db_url.replace('postgresql://', '')
            auth, rest = url_parts.split('@')
            user, password = auth.split(':')
            host_port, database = rest.split('/')
            host, port = host_port.split(':')
            
            return {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password,
                'project_name': credentials.get('SUPABASE_PROJECT_NAME', 'Unknown')
            }
        except Exception as e:
            print(f"ERROR: Failed to parse SUPABASE_DB_URL: {e}")
            return None
    
    def connect(self) -> bool:
        """Connect to Supabase"""
        if not PSYCOPG2_AVAILABLE or not self.credentials:
            return False
        
        try:
            self.conn = psycopg2.connect(
                host=self.credentials['host'],
                port=self.credentials['port'],
                database=self.credentials['database'],
                user=self.credentials['user'],
                password=self.credentials['password'],
                sslmode='require'
            )
            self.conn.autocommit = False
            return True
        except Exception as e:
            print(f"ERROR: Supabase connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Supabase"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.conn is not None


class SQLiteDatabaseAnalyzer:
    """Analyze local SQLite databases"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.databases = {}
        self.load_databases()
    
    def load_databases(self):
        """Load all non-backup databases"""
        for db_file in self.data_dir.glob("*.db"):
            if "backup" not in db_file.name.lower():
                self.databases[db_file.name] = self.analyze_database(db_file)
    
    def analyze_database(self, db_path: Path) -> Dict[str, Any]:
        """Analyze single database structure"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row['name'] for row in cursor.fetchall()]
        
        db_info = {
            'path': str(db_path),
            'size': db_path.stat().st_size,
            'type': 'SQLite',
            'tables': {}
        }
        
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = [dict(row) for row in cursor.fetchall()]
            
            # Fetch sample data
            column_examples = {}
            for col in columns:
                col_name = col['name']
                try:
                    cursor.execute(f"""
                        SELECT DISTINCT {col_name} 
                        FROM {table_name} 
                        WHERE {col_name} IS NOT NULL 
                        LIMIT 3
                    """)
                    examples = [row[0] for row in cursor.fetchall()]
                    column_examples[col_name] = examples
                except:
                    column_examples[col_name] = []
            
            db_info['tables'][table_name] = {
                'columns': columns,
                'row_count': count,
                'foreign_keys': foreign_keys,
                'column_examples': column_examples
            }
        
        conn.close()
        return db_info


class SupabaseDatabaseAnalyzer:
    """Analyze Supabase PostgreSQL database"""
    
    def __init__(self, supabase_conn: SupabaseConnection):
        self.supabase = supabase_conn
        self.schemas = {}
        if self.supabase.is_connected():
            self.load_schemas()
    
    def load_schemas(self):
        """Load all custom schemas"""
        cursor = self.supabase.conn.cursor(cursor_factory=RealDictCursor)
        
        # Get custom schemas (exclude system schemas)
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN (
                'pg_catalog', 'information_schema', 'pg_toast', 'auth', 
                'extensions', 'graphql', 'graphql_public', 'net', 'pgsodium',
                'pgsodium_masks', 'pgtle', 'realtime', 'storage', 
                'supabase_functions', 'supabase_migrations', 'vault'
            )
            ORDER BY schema_name
        """)
        
        schema_names = [row['schema_name'] for row in cursor.fetchall()]
        
        for schema_name in schema_names:
            self.schemas[schema_name] = self.analyze_schema(schema_name)
        
        cursor.close()
    
    def analyze_schema(self, schema_name: str) -> Dict[str, Any]:
        """Analyze single schema"""
        cursor = self.supabase.conn.cursor(cursor_factory=RealDictCursor)
        
        schema_info = {
            'name': schema_name,
            'type': 'PostgreSQL',
            'tables': {}
        }
        
        # Get tables in schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema_name,))
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        for table_name in tables:
            schema_info['tables'][table_name] = self.analyze_table(schema_name, table_name)
        
        cursor.close()
        return schema_info
    
    def analyze_table(self, schema_name: str, table_name: str) -> Dict[str, Any]:
        """Analyze single table"""
        cursor = self.supabase.conn.cursor(cursor_factory=RealDictCursor)
        
        # Get columns
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema_name, table_name))
        
        columns = [dict(row) for row in cursor.fetchall()]
        
        # Get row count
        try:
            cursor.execute(sql.SQL("SELECT COUNT(*) as count FROM {}.{}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name)
            ))
            row_count = cursor.fetchone()['count']
        except:
            row_count = 0
        
        # Get primary keys
        cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
        """, (f'{schema_name}.{table_name}',))
        
        primary_keys = [row['attname'] for row in cursor.fetchall()]
        
        # Get sample data
        column_examples = {}
        for col in columns:
            col_name = col['column_name']
            try:
                cursor.execute(sql.SQL("""
                    SELECT DISTINCT {}
                    FROM {}.{}
                    WHERE {} IS NOT NULL
                    LIMIT 3
                """).format(
                    sql.Identifier(col_name),
                    sql.Identifier(schema_name),
                    sql.Identifier(table_name),
                    sql.Identifier(col_name)
                ))
                examples = [row[0] for row in cursor.fetchall()]
                column_examples[col_name] = examples
            except:
                column_examples[col_name] = []
        
        cursor.close()
        
        return {
            'columns': columns,
            'row_count': row_count,
            'primary_keys': primary_keys,
            'column_examples': column_examples
        }


class SchemaComparator:
    """Compare SQLite and Supabase schemas"""
    
    def __init__(self, sqlite_analyzer: SQLiteDatabaseAnalyzer, 
                 supabase_analyzer: SupabaseDatabaseAnalyzer):
        self.sqlite = sqlite_analyzer
        self.supabase = supabase_analyzer
        self.differences = []
    
    def compare_all(self):
        """Compare all databases/schemas"""
        # Map SQLite databases to Supabase schemas
        db_schema_map = {
            'ai_infrastructure.db': 'ai_infrastructure',
            'sessions.db': 'sessions',
            'synergy_sessions.db': 'synergy_sessions',
            'kanban_analytics.db': 'kanban_analytics',
            'stock_data.db': 'stock_data'
        }
        
        for db_name, schema_name in db_schema_map.items():
            if db_name in self.sqlite.databases and schema_name in self.supabase.schemas:
                self.compare_database_schema(db_name, schema_name)
        
        return self.differences
    
    def compare_database_schema(self, db_name: str, schema_name: str):
        """Compare SQLite database to Supabase schema"""
        sqlite_db = self.sqlite.databases[db_name]
        supabase_schema = self.supabase.schemas[schema_name]
        
        sqlite_tables = set(sqlite_db['tables'].keys())
        supabase_tables = set(supabase_schema['tables'].keys())
        
        # Tables only in SQLite
        only_sqlite = sqlite_tables - supabase_tables
        if only_sqlite:
            self.differences.append({
                'type': 'MISSING_IN_SUPABASE',
                'severity': 'HIGH',
                'database': db_name,
                'schema': schema_name,
                'tables': list(only_sqlite),
                'message': f'{len(only_sqlite)} tables missing in Supabase'
            })
        
        # Tables only in Supabase
        only_supabase = supabase_tables - sqlite_tables
        if only_supabase:
            self.differences.append({
                'type': 'EXTRA_IN_SUPABASE',
                'severity': 'LOW',
                'database': db_name,
                'schema': schema_name,
                'tables': list(only_supabase),
                'message': f'{len(only_supabase)} extra tables in Supabase'
            })
        
        # Compare common tables
        common_tables = sqlite_tables & supabase_tables
        for table_name in common_tables:
            self.compare_table_structure(db_name, schema_name, table_name)
            self.compare_row_counts(db_name, schema_name, table_name)
    
    def compare_table_structure(self, db_name: str, schema_name: str, table_name: str):
        """Compare table structures"""
        sqlite_table = self.sqlite.databases[db_name]['tables'][table_name]
        supabase_table = self.supabase.schemas[schema_name]['tables'][table_name]
        
        sqlite_cols = {col['name'] for col in sqlite_table['columns']}
        supabase_cols = {col['column_name'] for col in supabase_table['columns']}
        
        # Columns only in SQLite
        only_sqlite = sqlite_cols - supabase_cols
        if only_sqlite:
            self.differences.append({
                'type': 'COLUMN_MISSING_IN_SUPABASE',
                'severity': 'MEDIUM',
                'database': db_name,
                'schema': schema_name,
                'table': table_name,
                'columns': list(only_sqlite),
                'message': f'Columns missing in Supabase: {", ".join(only_sqlite)}'
            })
        
        # Columns only in Supabase
        only_supabase = supabase_cols - sqlite_cols
        if only_supabase:
            self.differences.append({
                'type': 'COLUMN_EXTRA_IN_SUPABASE',
                'severity': 'LOW',
                'database': db_name,
                'schema': schema_name,
                'table': table_name,
                'columns': list(only_supabase),
                'message': f'Extra columns in Supabase: {", ".join(only_supabase)}'
            })
    
    def compare_row_counts(self, db_name: str, schema_name: str, table_name: str):
        """Compare row counts"""
        sqlite_count = self.sqlite.databases[db_name]['tables'][table_name]['row_count']
        supabase_count = self.supabase.schemas[schema_name]['tables'][table_name]['row_count']
        
        if sqlite_count != supabase_count:
            difference = supabase_count - sqlite_count
            self.differences.append({
                'type': 'ROW_COUNT_MISMATCH',
                'severity': 'MEDIUM' if abs(difference) > 10 else 'LOW',
                'database': db_name,
                'schema': schema_name,
                'table': table_name,
                'sqlite_count': sqlite_count,
                'supabase_count': supabase_count,
                'difference': difference,
                'message': f'Row count mismatch: SQLite={sqlite_count}, Supabase={supabase_count} (diff={difference:+d})'
            })


class ScriptAnalyzer:
    """Analyze Python and JavaScript files for database access"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts = []
        self.scan_scripts()
    
    def scan_scripts(self):
        """Scan Python and JavaScript files"""
        exclude_dirs = {'__pycache__', '.git', 'venv', '.venv', 'node_modules', 
                       'archive', 'archived', 'Archive', 'Archived'}
        exclude_patterns = ['test_', 'fix_', 'TEST_', 'FIX_']
        
        for pattern in ["*.py", "*.js"]:
            for script_file in self.project_root.rglob(pattern):
                if any(excluded in script_file.parts for excluded in exclude_dirs):
                    continue
                
                if script_file.parent == self.project_root:
                    continue
                
                if any(script_file.name.startswith(p) for p in exclude_patterns):
                    continue
                
                script_info = self.analyze_script(script_file)
                if script_info['db_connections'] or script_info['table_accesses']:
                    self.scripts.append(script_info)
    
    def analyze_script(self, script_path: Path) -> Dict[str, Any]:
        """Analyze script for database patterns"""
        try:
            content = script_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return {
                'path': str(script_path),
                'db_connections': [],
                'table_accesses': [],
                'error': True
            }
        
        db_connections = []
        table_accesses = []
        uses_supabase = False
        
        # Find database connections
        patterns = [
            r'sqlite3\.connect\([\'"]([^\'"]+)[\'"]',
            r'get_database_connection\([\'"]([^\'"]+)[\'"]',
            r'DATABASE_PATH\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'db_path\s*=\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                db_path = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                db_connections.append({
                    'path': db_path,
                    'line': line_num,
                    'uses_utility': 'get_database_connection' in match.group(0)
                })
        
        # Check for Supabase usage
        if 'get_database_connection' in content or 'USE_SUPABASE' in content:
            uses_supabase = True
        
        # Find table accesses
        for match in re.finditer(r'FROM\s+(\w+)', content, re.IGNORECASE):
            table_accesses.append(match.group(1))
        for match in re.finditer(r'INTO\s+(\w+)', content, re.IGNORECASE):
            table_accesses.append(match.group(1))
        
        return {
            'path': str(script_path.relative_to(self.project_root)),
            'full_path': str(script_path),
            'db_connections': db_connections,
            'table_accesses': list(set(table_accesses)),
            'uses_supabase': uses_supabase,
            'lines': len(content.split('\n'))
        }


def print_section(title: str, char: str = "="):
    """Print section header"""
    print(f"\n{char * 100}")
    print(f"{title}")
    print(f"{char * 100}\n")


def format_examples(examples: List) -> str:
    """Format example values"""
    formatted = []
    for ex in examples[:3]:
        if ex is None:
            formatted.append("NULL")
        elif isinstance(ex, str):
            if len(ex) > 50:
                formatted.append(f'"{ex[:47]}..."')
            else:
                formatted.append(f'"{ex}"')
        else:
            formatted.append(str(ex)[:50])
    return ", ".join(formatted)


def print_sqlite_structure(sqlite_analyzer: SQLiteDatabaseAnalyzer):
    """Print SQLite database structure"""
    print_section("SQLITE DATABASES (LOCAL)")
    
    for db_name, db_info in sorted(sqlite_analyzer.databases.items()):
        print(f"\nDATABASE: {db_name}")
        print(f"Location: {db_info['path']}")
        print(f"Size: {db_info['size']:,} bytes")
        print(f"Tables: {len(db_info['tables'])}")
        print(f"{'-' * 100}")
        
        for table_name, table_info in sorted(db_info['tables'].items()):
            print(f"\n  TABLE: {table_name} - {table_info['row_count']:,} rows")
            
            column_examples = table_info.get('column_examples', {})
            
            for col in table_info['columns']:
                pk = " [PK]" if col['pk'] else ""
                nn = " [NOT NULL]" if col['notnull'] else ""
                col_name = col['name']
                col_type = col['type']
                
                print(f"    {col_name:<30} {col_type:<15}{pk}{nn}")
                
                examples = column_examples.get(col_name, [])
                if examples:
                    example_str = format_examples(examples)
                    print(f"      Examples: {example_str}")
            
            if table_info['foreign_keys']:
                print(f"\n  Foreign Keys:")
                for fk in table_info['foreign_keys']:
                    print(f"    {fk['from']} -> {fk['table']}.{fk['to']}")


def print_supabase_structure(supabase_analyzer: SupabaseDatabaseAnalyzer):
    """Print Supabase database structure"""
    print_section("SUPABASE SCHEMAS (PRODUCTION)")
    
    if not supabase_analyzer.supabase.is_connected():
        print("SUPABASE NOT CONNECTED - Skipping analysis\n")
        return
    
    for schema_name, schema_info in sorted(supabase_analyzer.schemas.items()):
        print(f"\nSCHEMA: {schema_name}")
        print(f"Tables: {len(schema_info['tables'])}")
        print(f"{'-' * 100}")
        
        for table_name, table_info in sorted(schema_info['tables'].items()):
            print(f"\n  TABLE: {table_name} - {table_info['row_count']:,} rows")
            
            column_examples = table_info.get('column_examples', {})
            primary_keys = table_info.get('primary_keys', [])
            
            for col in table_info['columns']:
                col_name = col['column_name']
                col_type = col['data_type']
                pk = " [PK]" if col_name in primary_keys else ""
                nn = " [NOT NULL]" if col['is_nullable'] == 'NO' else ""
                
                print(f"    {col_name:<30} {col_type:<15}{pk}{nn}")
                
                examples = column_examples.get(col_name, [])
                if examples:
                    example_str = format_examples(examples)
                    print(f"      Examples: {example_str}")


def print_schema_comparison(comparator: SchemaComparator):
    """Print schema comparison results"""
    print_section("SCHEMA COMPARISON (SQLite vs Supabase)")
    
    if not comparator.differences:
        print("SUCCESS - Schemas are identical\n")
        return
    
    print(f"WARNING - Found {len(comparator.differences)} differences\n")
    
    by_severity = defaultdict(list)
    for diff in comparator.differences:
        by_severity[diff['severity']].append(diff)
    
    for severity in ['HIGH', 'MEDIUM', 'LOW']:
        if severity not in by_severity:
            continue
        
        print(f"\n{severity} SEVERITY ({len(by_severity[severity])} issues)")
        print(f"{'-' * 100}")
        
        for diff in by_severity[severity]:
            print(f"\n  {diff['type']}: {diff['message']}")
            print(f"  Database: {diff.get('database', 'N/A')}")
            print(f"  Schema: {diff.get('schema', 'N/A')}")
            if 'table' in diff:
                print(f"  Table: {diff['table']}")
            if 'tables' in diff:
                print(f"  Tables: {', '.join(diff['tables'][:10])}")
            if 'columns' in diff:
                print(f"  Columns: {', '.join(diff['columns'])}")


def print_script_analysis(script_analyzer: ScriptAnalyzer):
    """Print script analysis"""
    print_section("SCRIPT DATABASE ACCESS ANALYSIS")
    
    total = len(script_analyzer.scripts)
    using_supabase = sum(1 for s in script_analyzer.scripts if s['uses_supabase'])
    
    print(f"Total scripts with database access: {total}")
    print(f"Scripts using get_database_connection(): {using_supabase}")
    print(f"Scripts using direct sqlite3.connect(): {total - using_supabase}\n")
    
    # Group by Supabase support
    supabase_scripts = [s for s in script_analyzer.scripts if s['uses_supabase']]
    sqlite_scripts = [s for s in script_analyzer.scripts if not s['uses_supabase']]
    
    if sqlite_scripts:
        print(f"\nSCRIPTS NEEDING UPDATE (direct sqlite3.connect):")
        print(f"{'-' * 100}")
        for script in sorted(sqlite_scripts, key=lambda x: x['path'])[:20]:
            print(f"\n  FILE: {script['path']}")
            for conn in script['db_connections']:
                print(f"    Line {conn['line']}: {conn['path']}")


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    data_dir = Path(__file__).parent
    
    print("\n" + "=" * 100)
    print("AI AGENTS PLATFORM - DATABASE ANALYSIS v2.0 (SQLite + Supabase)")
    print("=" * 100)
    print(f"Project: {project_root}")
    print(f"Data: {data_dir}")
    
    # Initialize SQLite analyzer
    print("\n[1/4] Analyzing SQLite databases...")
    sqlite_analyzer = SQLiteDatabaseAnalyzer(data_dir)
    print(f"  Found {len(sqlite_analyzer.databases)} databases")
    
    # Initialize Supabase analyzer
    print("\n[2/4] Analyzing Supabase database...")
    supabase_conn = SupabaseConnection()
    if supabase_conn.connect():
        print(f"  Connected to Supabase: {supabase_conn.credentials['project_name']}")
        supabase_analyzer = SupabaseDatabaseAnalyzer(supabase_conn)
        print(f"  Found {len(supabase_analyzer.schemas)} schemas")
    else:
        print("  Supabase connection failed - skipping")
        supabase_analyzer = None
    
    # Compare schemas
    print("\n[3/4] Comparing schemas...")
    if supabase_analyzer:
        comparator = SchemaComparator(sqlite_analyzer, supabase_analyzer)
        comparator.compare_all()
        print(f"  Found {len(comparator.differences)} differences")
    else:
        comparator = None
    
    # Analyze scripts
    print("\n[4/4] Analyzing scripts...")
    script_analyzer = ScriptAnalyzer(project_root)
    print(f"  Found {len(script_analyzer.scripts)} scripts with database access")
    
    # Print all sections
    print_sqlite_structure(sqlite_analyzer)
    
    if supabase_analyzer:
        print_supabase_structure(supabase_analyzer)
        print_schema_comparison(comparator)
    
    print_script_analysis(script_analyzer)
    
    # Save report
    output_file = data_dir / 'database_analysis_v2_report.txt'
    print(f"\nSaving report to: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            original_stdout = sys.stdout
            sys.stdout = f
            
            print_sqlite_structure(sqlite_analyzer)
            if supabase_analyzer:
                print_supabase_structure(supabase_analyzer)
                print_schema_comparison(comparator)
            print_script_analysis(script_analyzer)
            
            print("\n" + "=" * 100)
            print("ANALYSIS COMPLETE")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100)
            
            sys.stdout = original_stdout
        
        print(f"SUCCESS: Report saved to {output_file.name}")
        
    except Exception as e:
        print(f"ERROR: Failed to save report: {e}")
    
    # Cleanup
    if supabase_conn:
        supabase_conn.disconnect()
    
    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)


if __name__ == '__main__':
    main()
