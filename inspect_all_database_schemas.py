"""
Comprehensive Database Schema Inspector
Extracts COMPLETE schemas for sessions.db, synergy_sessions.db, and ai_infrastructure.db
"""

import sqlite3
import json
from pathlib import Path

def get_full_schema(db_path):
    """Get complete schema including tables, columns, types, constraints, indexes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = {
        "database": str(db_path),
        "tables": {}
    }
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        table_info = {
            "columns": [],
            "indexes": [],
            "create_statement": ""
        }
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_info = {
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "default_value": col[4],
                "primary_key": bool(col[5])
            }
            table_info["columns"].append(col_info)
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = cursor.fetchall()
        
        for idx in indexes:
            idx_name = idx[1]
            cursor.execute(f"PRAGMA index_info({idx_name})")
            idx_columns = [row[2] for row in cursor.fetchall()]
            
            idx_info = {
                "name": idx_name,
                "unique": bool(idx[2]),
                "columns": idx_columns
            }
            table_info["indexes"].append(idx_info)
        
        # Get CREATE statement
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        create_sql = cursor.fetchone()
        if create_sql:
            table_info["create_statement"] = create_sql[0]
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        table_info["row_count"] = cursor.fetchone()[0]
        
        schema["tables"][table] = table_info
    
    conn.close()
    return schema

def print_schema_detailed(schema):
    """Print schema in detailed human-readable format"""
    print(f"\n{'='*100}")
    print(f"DATABASE: {schema['database']}")
    print(f"{'='*100}\n")
    
    for table_name, table_info in schema["tables"].items():
        print(f"\n{'-'*100}")
        print(f"TABLE: {table_name} ({table_info['row_count']} rows)")
        print(f"{'-'*100}")
        
        # Print columns
        print("\nCOLUMNS:")
        print(f"{'ID':<5} {'Name':<30} {'Type':<15} {'Null':<8} {'Default':<15} {'PK':<5}")
        print(f"{'-'*5} {'-'*30} {'-'*15} {'-'*8} {'-'*15} {'-'*5}")
        
        for col in table_info["columns"]:
            null_str = "NO" if col["not_null"] else "YES"
            pk_str = "YES" if col["primary_key"] else ""
            default_str = str(col["default_value"]) if col["default_value"] else ""
            
            print(f"{col['cid']:<5} {col['name']:<30} {col['type']:<15} {null_str:<8} {default_str:<15} {pk_str:<5}")
        
        # Print indexes
        if table_info["indexes"]:
            print("\nINDEXES:")
            for idx in table_info["indexes"]:
                unique_str = "UNIQUE" if idx["unique"] else "NON-UNIQUE"
                cols_str = ", ".join(idx["columns"])
                print(f"  - {idx['name']} ({unique_str}): {cols_str}")
        
        # Print CREATE statement
        print("\nCREATE STATEMENT:")
        print(table_info["create_statement"])
        print()

def main():
    root_dir = Path(__file__).parent
    data_dir = root_dir / "data"
    
    databases = [
        data_dir / "sessions.db",
        data_dir / "synergy_sessions.db",
        data_dir / "ai_infrastructure.db"
    ]
    
    all_schemas = {}
    
    for db_path in databases:
        if db_path.exists():
            print(f"\nProcessing: {db_path.name}")
            schema = get_full_schema(db_path)
            all_schemas[db_path.name] = schema
            print_schema_detailed(schema)
        else:
            print(f"\nWARNING: {db_path} does not exist!")
    
    # Save to JSON file
    output_file = root_dir / "COMPLETE_DATABASE_SCHEMAS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_schemas, f, indent=2, default=str)
    
    print(f"\n{'='*100}")
    print(f"COMPLETE SCHEMAS SAVED TO: {output_file}")
    print(f"{'='*100}\n")
    
    # Print summary
    print("\nSUMMARY:")
    print(f"{'Database':<30} {'Tables':<10} {'Total Rows'}")
    print(f"{'-'*30} {'-'*10} {'-'*10}")
    
    for db_name, schema in all_schemas.items():
        table_count = len(schema["tables"])
        total_rows = sum(t["row_count"] for t in schema["tables"].values())
        print(f"{db_name:<30} {table_count:<10} {total_rows}")

if __name__ == "__main__":
    main()
