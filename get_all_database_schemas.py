"""
Extract Complete Database Schemas

This script extracts detailed schemas for all databases in the project:
- sessions.db
- ai_infrastructure.db
- synergy_sessions.db (if exists)
- In_House_SQL databases (if accessible)

Output: JSON file with complete schema information
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def get_table_schema(cursor, table_name):
    """Get detailed schema for a table"""
    schema = {
        'name': table_name,
        'columns': [],
        'indexes': [],
        'sample_count': 0
    }
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_info = {
            'cid': col[0],
            'name': col[1],
            'type': col[2],
            'not_null': bool(col[3]),
            'default_value': col[4],
            'primary_key': bool(col[5])
        }
        schema['columns'].append(col_info)
    
    # Get index information
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    
    for idx in indexes:
        idx_info = {
            'name': idx[1],
            'unique': bool(idx[2]),
            'origin': idx[3],
            'partial': bool(idx[4])
        }
        
        # Get index columns
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        idx_cols = cursor.fetchall()
        idx_info['columns'] = [col[2] for col in idx_cols]
        
        schema['indexes'].append(idx_info)
    
    # Get row count
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        schema['sample_count'] = cursor.fetchone()[0]
    except:
        schema['sample_count'] = 0
    
    # Get sample data (first 3 rows)
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        cursor.execute(f"PRAGMA table_info({table_name})")
        col_names = [col[1] for col in cursor.fetchall()]
        
        schema['sample_data'] = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(col_names):
                value = row[i]
                # Truncate long strings/JSON
                if isinstance(value, str) and len(value) > 200:
                    value = value[:200] + '...'
                row_dict[col_name] = value
            schema['sample_data'].append(row_dict)
    except Exception as e:
        schema['sample_data_error'] = str(e)
    
    return schema

def get_database_schema(db_path, db_name):
    """Get complete schema for a database"""
    print(f"\n{'='*60}")
    print(f"Extracting schema for: {db_name}")
    print(f"Path: {db_path}")
    print(f"{'='*60}")
    
    if not db_path.exists():
        return {
            'database': db_name,
            'path': str(db_path),
            'exists': False,
            'error': 'Database file not found'
        }
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        schema = {
            'database': db_name,
            'path': str(db_path),
            'exists': True,
            'extracted_at': datetime.now().isoformat(),
            'table_count': len(tables),
            'tables': {}
        }
        
        # Get schema for each table
        for table in tables:
            print(f"  Processing table: {table}...", end='')
            table_schema = get_table_schema(cursor, table)
            schema['tables'][table] = table_schema
            print(f" {table_schema['sample_count']} rows")
        
        conn.close()
        
        return schema
        
    except Exception as e:
        return {
            'database': db_name,
            'path': str(db_path),
            'exists': True,
            'error': str(e)
        }

def main():
    root_dir = Path(__file__).parent
    
    all_schemas = {
        'extracted_at': datetime.now().isoformat(),
        'project_root': str(root_dir),
        'databases': {}
    }
    
    # Database paths to check
    databases = {
        'sessions.db': root_dir / 'data' / 'sessions.db',
        'ai_infrastructure.db': root_dir / 'data' / 'ai_infrastructure.db',
        'synergy_sessions.db': root_dir / 'data' / 'synergy_sessions.db',
    }
    
    # Check for In_House_SQL databases
    in_house_path = root_dir.parent / 'In_House_SQL' / 'G_Folder'
    if in_house_path.exists():
        # Look for .db files
        for db_file in in_house_path.glob('*.db'):
            databases[f'In_House_SQL/{db_file.name}'] = db_file
    
    print(f"{'='*60}")
    print(f"DATABASE SCHEMA EXTRACTION")
    print(f"Project: {root_dir.name}")
    print(f"Databases to extract: {len(databases)}")
    print(f"{'='*60}")
    
    # Extract schemas
    for db_name, db_path in databases.items():
        schema = get_database_schema(db_path, db_name)
        all_schemas['databases'][db_name] = schema
    
    # Save to JSON file
    output_file = root_dir / 'DATABASE_SCHEMAS.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_schemas, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Output file: {output_file}")
    print(f"Total databases: {len(all_schemas['databases'])}")
    
    # Summary
    print(f"\nSUMMARY:")
    for db_name, schema in all_schemas['databases'].items():
        if schema.get('exists'):
            if 'error' in schema:
                print(f"  ❌ {db_name}: ERROR - {schema['error']}")
            else:
                table_count = schema.get('table_count', 0)
                total_rows = sum(
                    table_data.get('sample_count', 0) 
                    for table_data in schema.get('tables', {}).values()
                )
                print(f"  ✅ {db_name}: {table_count} tables, {total_rows} total rows")
        else:
            print(f"  ⚠️  {db_name}: Not found")
    
    # Create human-readable markdown version
    md_output = root_dir / 'DATABASE_SCHEMAS.md'
    create_markdown_schema(all_schemas, md_output)
    print(f"\nMarkdown version: {md_output}")

def create_markdown_schema(schemas, output_file):
    """Create a human-readable markdown version"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Database Schemas\n\n")
        f.write(f"**Extracted:** {schemas['extracted_at']}\n")
        f.write(f"**Project:** {schemas['project_root']}\n\n")
        f.write(f"---\n\n")
        
        for db_name, db_schema in schemas['databases'].items():
            f.write(f"## {db_name}\n\n")
            
            if not db_schema.get('exists'):
                f.write(f"❌ **Database not found**\n\n")
                continue
            
            if 'error' in db_schema:
                f.write(f"❌ **Error:** {db_schema['error']}\n\n")
                continue
            
            f.write(f"**Path:** `{db_schema['path']}`\n")
            f.write(f"**Tables:** {db_schema['table_count']}\n\n")
            
            for table_name, table_schema in db_schema.get('tables', {}).items():
                f.write(f"### Table: `{table_name}`\n\n")
                f.write(f"**Row Count:** {table_schema['sample_count']}\n\n")
                
                # Columns
                f.write(f"**Columns:**\n\n")
                f.write(f"| # | Name | Type | Null | Default | PK |\n")
                f.write(f"|---|------|------|------|---------|----|\n")
                
                for col in table_schema['columns']:
                    pk = '🔑' if col['primary_key'] else ''
                    not_null = '❌' if col['not_null'] else '✓'
                    default = col['default_value'] if col['default_value'] else '-'
                    f.write(f"| {col['cid']} | `{col['name']}` | {col['type']} | {not_null} | {default} | {pk} |\n")
                
                f.write(f"\n")
                
                # Indexes
                if table_schema['indexes']:
                    f.write(f"**Indexes:**\n\n")
                    for idx in table_schema['indexes']:
                        unique = '(UNIQUE)' if idx['unique'] else ''
                        cols = ', '.join([f'`{c}`' for c in idx['columns']])
                        f.write(f"- `{idx['name']}` {unique}: {cols}\n")
                    f.write(f"\n")
                
                # Sample data
                if 'sample_data' in table_schema and table_schema['sample_data']:
                    f.write(f"**Sample Data** (first {len(table_schema['sample_data'])} rows):\n\n")
                    f.write(f"```json\n")
                    f.write(json.dumps(table_schema['sample_data'], indent=2))
                    f.write(f"\n```\n\n")
                
                f.write(f"---\n\n")

if __name__ == '__main__':
    main()
