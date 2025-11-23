"""
Diagnose Supabase Schema Issues
================================
from shared.database_utils import convert_sql_placeholders

Scans all route files for SQL queries and checks if tables/columns exist in Supabase

USAGE:
    python scripts/testing/diagnose_supabase_schema.py
    
OUTPUT:
    - List of all tables referenced in code
    - List of all columns referenced per table
    - Missing tables/columns in Supabase
    - SQL to create missing structures
"""

import os
import re
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

# Load environment
load_dotenv('.env.master')

def get_supabase_connection():
    """Connect to Supabase"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        raise ValueError("SUPABASE_DB_URL not set")
    
    conn = psycopg2.connect(db_url, sslmode='require')
    return conn


def get_existing_schema():
    """Get all tables and columns from Supabase"""
    conn = get_supabase_connection()
    cursor = conn.cursor()
    
    # Get all tables in ai_infrastructure schema
    cursor.execute("""
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        ORDER BY table_name, ordinal_position
    """)
    
    schema = defaultdict(dict)
    for table_name, column_name, data_type, is_nullable in cursor.fetchall():
        schema[table_name][column_name] = {
            'type': data_type,
            'nullable': is_nullable == 'YES'
        }
    
    conn.close()
    return schema


def extract_sql_queries(file_path):
    """Extract SQL queries from Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []
    
    queries = []
    
    # Pattern 1: cursor.execute(""" ... """)
    pattern1 = r'cursor\.execute\s*\(\s*[rf]?"""(.*?)"""\s*[,\)]'
    queries.extend(re.findall(pattern1, content, re.DOTALL))
    
    # Pattern 2: cursor.execute(" ... ")
    pattern2 = r'cursor\.execute\s*\(\s*[rf]?"(.*?)"\s*[,\)]'
    queries.extend(re.findall(pattern2, content, re.DOTALL))
    
    # Pattern 3: cursor.execute(f""" ... """)
    pattern3 = r'cursor\.execute\s*\(\s*f"""(.*?)"""\s*[,\)]'
    queries.extend(re.findall(pattern3, content, re.DOTALL))
    
    return queries


def parse_table_columns(query):
    """Parse table names and columns from SQL query"""
    tables = set()
    columns = defaultdict(set)
    
    # Remove comments
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    
    # Find FROM/JOIN clauses for table names
    from_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    for match in re.finditer(from_pattern, query, re.IGNORECASE):
        table_name = match.group(1).lower()
        if table_name not in ['select', 'where', 'and', 'or', 'values']:
            tables.add(table_name)
    
    # Find column references
    # Pattern: table_name.column_name or just column_name in SELECT/WHERE
    column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.'
    for match in re.finditer(column_pattern, query):
        table_name = match.group(1).lower()
        if table_name in tables:
            # Find what comes after the dot
            col_match = re.search(rf'{table_name}\.([a-zA-Z_][a-zA-Z0-9_]*)', query)
            if col_match:
                columns[table_name].add(col_match.group(1).lower())
    
    return tables, columns


def scan_routes_directory():
    """Scan all route files for SQL queries"""
    routes_dir = Path(__file__).parent.parent.parent / 'AI_infrastructure' / 'routes'
    
    all_tables = set()
    all_columns = defaultdict(set)
    file_queries = {}
    
    for py_file in routes_dir.glob('*.py'):
        queries = extract_sql_queries(py_file)
        if queries:
            file_queries[py_file.name] = queries
            
            for query in queries:
                tables, columns = parse_table_columns(query)
                all_tables.update(tables)
                
                for table, cols in columns.items():
                    all_columns[table].update(cols)
    
    return all_tables, all_columns, file_queries


def main():
    print("=" * 80)
    print("SUPABASE SCHEMA DIAGNOSTICS")
    print("=" * 80)
    
    # Get existing schema from Supabase
    print("\n📊 Loading existing Supabase schema...")
    try:
        existing_schema = get_existing_schema()
        print(f"✅ Found {len(existing_schema)} tables in Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # Scan route files for SQL queries
    print("\n🔍 Scanning route files for SQL queries...")
    referenced_tables, referenced_columns, file_queries = scan_routes_directory()
    print(f"✅ Found {len(referenced_tables)} referenced tables in code")
    print(f"✅ Scanned {len(file_queries)} route files")
    
    # Compare what exists vs what's referenced
    print("\n" + "=" * 80)
    print("SCHEMA COMPARISON")
    print("=" * 80)
    
    # Check tables
    print("\n📋 TABLE STATUS:")
    print("-" * 80)
    
    missing_tables = []
    existing_tables = []
    
    for table in sorted(referenced_tables):
        if table in existing_schema:
            existing_tables.append(table)
            print(f"  ✅ {table:<40} EXISTS")
        else:
            missing_tables.append(table)
            print(f"  ❌ {table:<40} MISSING")
    
    # Check columns for existing tables
    print("\n📋 COLUMN STATUS (for existing tables):")
    print("-" * 80)
    
    missing_columns = defaultdict(list)
    
    for table in sorted(existing_tables):
        if table in referenced_columns:
            print(f"\n  Table: {table}")
            table_schema = existing_schema[table]
            
            for column in sorted(referenced_columns[table]):
                if column in table_schema:
                    print(f"    ✅ {column}")
                else:
                    missing_columns[table].append(column)
                    print(f"    ❌ {column} - NOT FOUND")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Tables:")
    print(f"  - Referenced in code: {len(referenced_tables)}")
    print(f"  - Exist in Supabase: {len(existing_tables)}")
    print(f"  - Missing: {len(missing_tables)}")
    
    if missing_tables:
        print(f"\n⚠️  MISSING TABLES:")
        for table in sorted(missing_tables):
            print(f"  - {table}")
    
    if missing_columns:
        print(f"\n⚠️  MISSING COLUMNS:")
        for table, columns in sorted(missing_columns.items()):
            print(f"  Table: {table}")
            for column in sorted(columns):
                print(f"    - {column}")
    
    # Show which files reference missing tables
    if missing_tables:
        print("\n" + "=" * 80)
        print("FILES REFERENCING MISSING TABLES")
        print("=" * 80)
        
        for file_name, queries in sorted(file_queries.items()):
            file_missing = []
            for query in queries:
                tables, _ = parse_table_columns(query)
                for table in tables:
                    if table in missing_tables:
                        file_missing.append(table)
            
            if file_missing:
                print(f"\n📄 {file_name}")
                for table in set(file_missing):
                    print(f"  - {table}")
    
    # Generate SQL to create missing tables (if any)
    if missing_tables or missing_columns:
        print("\n" + "=" * 80)
        print("RECOMMENDED ACTIONS")
        print("=" * 80)
        
        if missing_tables:
            print("\n⚠️  Create missing tables:")
            print("Run: python scripts/maintenance/sync_schema_to_supabase.py")
        
        if missing_columns:
            print("\n⚠️  Add missing columns:")
            for table, columns in sorted(missing_columns.items()):
                print(f"\n-- Table: {table}")
                for column in sorted(columns):
                    print(f"ALTER TABLE ai_infrastructure.{table} ADD COLUMN IF NOT EXISTS {column} TEXT;")
    
    print("\n" + "=" * 80)
    print("✅ DIAGNOSTICS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
