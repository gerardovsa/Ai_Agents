"""
Complete Database Schema Inspector
Inspects sessions.db and synergy_sessions.db completely
"""
import sqlite3
from pathlib import Path

def inspect_database(db_path, db_name):
    print("\n" + "="*100)
    print(f"DATABASE: {db_name}")
    print(f"Path: {db_path}")
    print("="*100)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\nTotal Tables: {len(tables)}")
    print("-"*100)
    
    for table in tables:
        table_name = table[0]
        print(f"\n{'='*100}")
        print(f"TABLE: {table_name}")
        print('='*100)
        
        # Get table info (columns, types, nullability, defaults, primary key)
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\nColumns ({len(columns)}):")
        print(f"{'#':<5} {'Name':<30} {'Type':<15} {'NOT NULL':<10} {'Default':<20} {'PK':<5}")
        print("-"*100)
        
        for col in columns:
            cid, name, col_type, not_null, default_val, pk = col
            not_null_str = "YES" if not_null else "NO"
            default_str = str(default_val) if default_val is not None else "NULL"
            pk_str = "YES" if pk else ""
            print(f"{cid:<5} {name:<30} {col_type:<15} {not_null_str:<10} {default_str:<20} {pk_str:<5}")
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fkeys = cursor.fetchall()
        
        if fkeys:
            print(f"\nForeign Keys ({len(fkeys)}):")
            print(f"{'ID':<5} {'Seq':<5} {'Table':<20} {'From':<20} {'To':<20} {'On Update':<15} {'On Delete':<15}")
            print("-"*100)
            for fk in fkeys:
                fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
                print(f"{fk_id:<5} {seq:<5} {ref_table:<20} {from_col:<20} {to_col:<20} {on_update:<15} {on_delete:<15}")
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"\nIndexes ({len(indexes)}):")
            print(f"{'Seq':<5} {'Name':<40} {'Unique':<10} {'Origin':<10}")
            print("-"*100)
            for idx in indexes:
                seq, name, unique, origin, partial = idx
                unique_str = "YES" if unique else "NO"
                print(f"{seq:<5} {name:<40} {unique_str:<10} {origin:<10}")
                
                # Get index info
                cursor.execute(f"PRAGMA index_info({name})")
                idx_cols = cursor.fetchall()
                if idx_cols:
                    print(f"  Columns: {', '.join([col[2] for col in idx_cols])}")
        
        # Get sample row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"\nRow Count: {row_count:,}")
        
        # Get sample data (first 3 rows)
        if row_count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            
            print(f"\nSample Data (first {min(3, row_count)} rows):")
            print("-"*100)
            
            # Get column names
            col_names = [desc[0] for desc in cursor.description]
            
            for row_idx, row in enumerate(sample_rows, 1):
                print(f"\nRow {row_idx}:")
                for col_name, value in zip(col_names, row):
                    # Truncate long values
                    if value is not None and isinstance(value, str) and len(value) > 100:
                        display_value = value[:100] + "... (truncated)"
                    else:
                        display_value = value
                    print(f"  {col_name:<30} = {display_value}")
    
    conn.close()
    print("\n" + "="*100 + "\n")


# Main execution
root = Path(__file__).parent

# Inspect sessions.db
sessions_db = root / 'data' / 'sessions.db'
if sessions_db.exists():
    inspect_database(sessions_db, "sessions.db")
else:
    print(f"\n❌ sessions.db not found at: {sessions_db}")

# Inspect synergy_sessions.db
synergy_db = root / 'data' / 'synergy_sessions.db'
if synergy_db.exists():
    inspect_database(synergy_db, "synergy_sessions.db")
else:
    print(f"\n❌ synergy_sessions.db not found at: {synergy_db}")

print("\n" + "="*100)
print("INSPECTION COMPLETE")
print("="*100 + "\n")
