"""
Database Table Analysis - What's in Each Table
"""
import sqlite3

DB_PATH = 'AI_infrastructure/ai_infrastructure.db'

def analyze_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DATABASE TABLE ANALYSIS")
    print("=" * 80)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        if table == 'sqlite_sequence':
            continue
            
        print(f"\n{'=' * 80}")
        print(f"TABLE: {table}")
        print("=" * 80)
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print("\nCOLUMNS:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] else ''}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"\nROW COUNT: {count}")
        
        # Get sample data
        if count > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            print(f"\nSAMPLE DATA (first 3 rows):")
            col_names = [col[1] for col in columns]
            
            for i, row in enumerate(rows, 1):
                print(f"\n  Row {i}:")
                for col_name, value in zip(col_names, row):
                    if isinstance(value, str) and len(str(value)) > 50:
                        value = str(value)[:50] + "..."
                    print(f"    {col_name}: {value}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_tables()
