"""
Extract complete database schemas from all AI_agents databases
Creates comprehensive JSON and SQL documentation
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def get_table_schema(cursor, table_name):
    """Get detailed schema for a table"""
    # Get CREATE TABLE statement
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    create_sql = cursor.fetchone()[0]
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = []
    for col in cursor.fetchall():
        columns.append({
            'name': col[1],
            'type': col[2],
            'not_null': bool(col[3]),
            'default_value': col[4],
            'primary_key': bool(col[5])
        })
    
    # Get indexes
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=?", (table_name,))
    indexes = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Get foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = []
    for fk in cursor.fetchall():
        foreign_keys.append({
            'column': fk[3],
            'references_table': fk[2],
            'references_column': fk[4],
            'on_update': fk[5],
            'on_delete': fk[6]
        })
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    return {
        'table_name': table_name,
        'create_statement': create_sql,
        'columns': columns,
        'indexes': indexes,
        'foreign_keys': foreign_keys,
        'row_count': row_count
    }


def extract_database_schema(db_path):
    """Extract complete schema from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    table_names = [row[0] for row in cursor.fetchall()]
    
    # Get database file info
    db_file = Path(db_path)
    file_size_kb = db_file.stat().st_size / 1024
    
    schema = {
        'database_path': str(db_path),
        'file_size_kb': round(file_size_kb, 2),
        'table_count': len(table_names),
        'extracted_at': datetime.now().isoformat(),
        'tables': []
    }
    
    # Extract each table
    for table_name in table_names:
        schema['tables'].append(get_table_schema(cursor, table_name))
    
    conn.close()
    return schema


def main():
    """Extract schemas from all databases"""
    data_dir = Path(__file__).parent / 'data'
    
    databases = {
        'sessions.db': 'Main session storage with conversation history',
        'ai_infrastructure.db': 'User accounts, OAuth credentials, platform connections',
        'synergy_sessions.db': 'Synergy dashboard sessions (Kanban board)'
    }
    
    all_schemas = {
        'project': 'AI_agents',
        'description': 'Multi-agent AI platform with 576+ tools',
        'data_directory': str(data_dir),
        'extracted_at': datetime.now().isoformat(),
        'databases': {}
    }
    
    print("📊 Extracting database schemas...\n")
    
    for db_file, description in databases.items():
        db_path = data_dir / db_file
        if db_path.exists():
            print(f"📁 Extracting {db_file}...")
            schema = extract_database_schema(db_path)
            schema['description'] = description
            all_schemas['databases'][db_file] = schema
            print(f"   ✅ {len(schema['tables'])} tables, {schema['file_size_kb']} KB\n")
        else:
            print(f"   ⚠️ {db_file} not found\n")
    
    # Save JSON schema
    json_output = data_dir.parent / 'DATABASE_SCHEMA_COMPLETE.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(all_schemas, f, indent=2)
    print(f"✅ JSON schema saved: {json_output}")
    
    # Generate SQL documentation
    sql_output = data_dir.parent / 'DATABASE_SCHEMA_COMPLETE.sql'
    with open(sql_output, 'w', encoding='utf-8') as f:
        f.write("-- ============================================\n")
        f.write("-- AI_agents Database Schema Documentation\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- ============================================\n\n")
        
        for db_name, schema in all_schemas['databases'].items():
            f.write(f"-- ============================================\n")
            f.write(f"-- DATABASE: {db_name}\n")
            f.write(f"-- {schema['description']}\n")
            f.write(f"-- Location: {schema['database_path']}\n")
            f.write(f"-- Size: {schema['file_size_kb']} KB\n")
            f.write(f"-- Tables: {schema['table_count']}\n")
            f.write(f"-- ============================================\n\n")
            
            for table in schema['tables']:
                f.write(f"-- Table: {table['table_name']} ({table['row_count']} rows)\n")
                f.write(f"{table['create_statement']};\n\n")
                
                # Add indexes
                for idx in table['indexes']:
                    f.write(f"{idx};\n")
                if table['indexes']:
                    f.write("\n")
                
                # Document columns
                f.write(f"-- Columns in {table['table_name']}:\n")
                for col in table['columns']:
                    pk = " PRIMARY KEY" if col['primary_key'] else ""
                    nn = " NOT NULL" if col['not_null'] else ""
                    default = f" DEFAULT {col['default_value']}" if col['default_value'] else ""
                    f.write(f"--   {col['name']}: {col['type']}{pk}{nn}{default}\n")
                
                # Document foreign keys
                if table['foreign_keys']:
                    f.write(f"-- Foreign Keys:\n")
                    for fk in table['foreign_keys']:
                        f.write(f"--   {fk['column']} -> {fk['references_table']}.{fk['references_column']}")
                        f.write(f" (ON DELETE {fk['on_delete']})\n")
                
                f.write("\n\n")
    
    print(f"✅ SQL schema saved: {sql_output}")
    
    # Generate markdown documentation
    md_output = data_dir.parent / 'DATABASE_SCHEMA_COMPLETE.md'
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write("# 🗄️ AI_agents Database Schema Documentation\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 Overview\n\n")
        f.write(f"**Data Directory:** `{all_schemas['data_directory']}`\n\n")
        f.write(f"**Total Databases:** {len(all_schemas['databases'])}\n\n")
        
        # Summary table
        f.write("| Database | Description | Tables | Size | Rows |\n")
        f.write("|----------|-------------|--------|------|------|\n")
        for db_name, schema in all_schemas['databases'].items():
            total_rows = sum(t['row_count'] for t in schema['tables'])
            f.write(f"| `{db_name}` | {schema['description']} | ")
            f.write(f"{schema['table_count']} | {schema['file_size_kb']} KB | {total_rows:,} |\n")
        
        f.write("\n---\n\n")
        
        # Detailed schemas
        for db_name, schema in all_schemas['databases'].items():
            f.write(f"## 📁 {db_name}\n\n")
            f.write(f"**Description:** {schema['description']}\n\n")
            f.write(f"**Location:** `{schema['database_path']}`\n\n")
            f.write(f"**Size:** {schema['file_size_kb']} KB\n\n")
            f.write(f"**Tables:** {schema['table_count']}\n\n")
            
            for table in schema['tables']:
                f.write(f"### 📋 Table: `{table['table_name']}`\n\n")
                f.write(f"**Rows:** {table['row_count']:,}\n\n")
                
                # Columns table
                f.write("**Columns:**\n\n")
                f.write("| Column | Type | Null | Default | Key |\n")
                f.write("|--------|------|------|---------|-----|\n")
                for col in table['columns']:
                    null_str = "❌" if col['not_null'] else "✅"
                    key_str = "🔑 PK" if col['primary_key'] else ""
                    default_str = col['default_value'] if col['default_value'] else ""
                    f.write(f"| `{col['name']}` | {col['type']} | {null_str} | {default_str} | {key_str} |\n")
                
                # Foreign keys
                if table['foreign_keys']:
                    f.write("\n**Foreign Keys:**\n\n")
                    for fk in table['foreign_keys']:
                        f.write(f"- `{fk['column']}` → `{fk['references_table']}.{fk['references_column']}`")
                        f.write(f" (ON DELETE {fk['on_delete']})\n")
                
                # Indexes
                if table['indexes']:
                    f.write("\n**Indexes:**\n\n")
                    for idx in table['indexes']:
                        f.write(f"```sql\n{idx}\n```\n\n")
                
                # CREATE statement
                f.write("**CREATE Statement:**\n\n")
                f.write(f"```sql\n{table['create_statement']}\n```\n\n")
                f.write("---\n\n")
    
    print(f"✅ Markdown documentation saved: {md_output}")
    
    print("\n🎉 Database schema extraction complete!")
    print(f"\n📄 Generated files:")
    print(f"   - {json_output.name} (JSON format)")
    print(f"   - {sql_output.name} (SQL format)")
    print(f"   - {md_output.name} (Markdown documentation)")


if __name__ == '__main__':
    main()
