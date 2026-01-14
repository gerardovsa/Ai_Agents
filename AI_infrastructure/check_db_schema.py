"""
Check database schema and create missing tables
"""
import os

db_path = 'ai_infrastructure.db'

print("=" * 70)
print("DATABASE SCHEMA CHECKER")
print("=" * 70)
print()

# Check if database exists
if os.path.exists(db_path):
    print(f"Database exists: {db_path}")
    
    # Connect and check tables
    conn = psycopg2.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'")
    tables = cursor.fetchall()
    
    print(f"\n📋 Existing Tables ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Get schema for each table
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='{table[0]}'")
        columns = cursor.fetchall()
        print(f"    Columns: {len(columns)}")
        for col in columns:
            print(f"      • {col[1]} ({col[2]})")
    
    conn.close()
else:
    print(f" Database does not exist: {db_path}")
    print("   Will be created when tables are added")

print()
print("=" * 70)

