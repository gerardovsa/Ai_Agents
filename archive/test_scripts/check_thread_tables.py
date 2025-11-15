"""Check for thread_assignments and agent tracking tables"""
import sqlite3
from pathlib import Path

def check_database(db_path, db_name):
    print(f"\n{'='*80}")
    print(f"DATABASE: {db_name}")
    print(f"Path: {db_path}")
    print('='*80)
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in cursor.fetchall()]
    print(f"\nTotal tables: {len(all_tables)}")
    
    # Check for thread-related tables
    thread_tables = [t for t in all_tables if 'thread' in t.lower()]
    print(f"\n📋 Thread-related tables ({len(thread_tables)}):")
    for table in thread_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} rows")
    
    # Check for agent-related tables
    agent_tables = [t for t in all_tables if 'agent' in t.lower()]
    print(f"\n🤖 Agent-related tables ({len(agent_tables)}):")
    for table in agent_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} rows")
    
    # Check specifically for thread_assignments
    if 'thread_assignments' in all_tables:
        print(f"\n✅ thread_assignments TABLE EXISTS!")
        cursor.execute("PRAGMA table_info(thread_assignments)")
        columns = cursor.fetchall()
        print("\nColumns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM thread_assignments")
        count = cursor.fetchone()[0]
        print(f"\nRows: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM thread_assignments LIMIT 5")
            rows = cursor.fetchall()
            print("\nSample data:")
            for row in rows:
                print(f"  {row}")
    else:
        print(f"\n❌ thread_assignments table NOT FOUND")
    
    # Check for assignment data in metadata columns
    print(f"\n🔍 Checking for assignment data in other tables...")
    for table in all_tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            metadata_cols = [col[1] for col in columns if 'metadata' in col[1].lower() or 'agent' in col[1].lower()]
            
            if metadata_cols:
                print(f"\n  Table: {table}")
                for col in metadata_cols:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NOT NULL")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"    - {col}: {count} non-null values")
                        # Sample one value
                        cursor.execute(f"SELECT {col} FROM {table} WHERE {col} IS NOT NULL LIMIT 1")
                        sample = cursor.fetchone()
                        if sample and sample[0]:
                            sample_str = str(sample[0])[:100]
                            print(f"      Sample: {sample_str}...")
        except Exception as e:
            pass
    
    conn.close()

# Check both databases
check_database('data/ai_infrastructure.db', 'ai_infrastructure.db')
check_database('data/sessions.db', 'sessions.db')

print(f"\n{'='*80}")
print("SUMMARY")
print('='*80)
print("\nKey findings will help identify where agent-thread relationships are stored.")
