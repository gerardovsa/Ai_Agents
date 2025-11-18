"""Check current Synergy Sessions schema and apply updates if needed"""

import psycopg2
import sys

def check_schema():
    """Check if milestone columns exist"""
    try:
        conn = psycopg2.connect(
            dbname='In_House_SQL',
            user='postgres',
            host='localhost',
            password=''
        )
        cur = conn.cursor()
        
        # Check synergy_sessions columns
        print("=== Current synergy_sessions columns ===")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema='synergy_sessions' 
            AND table_name='synergy_sessions'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cur.fetchall()]
        for col in columns:
            print(f"  - {col}")
        
        # Check for milestone columns
        print("\n=== Milestone system columns ===")
        milestone_cols = ['uses_milestones', 'next_steps_deprecated', 'checklist_deprecated', 'message_count', 'migration_date']
        for col in milestone_cols:
            exists = col in columns
            status = "EXISTS" if exists else "MISSING"
            print(f"  {status}: {col}")
        
        # Check for milestone tables
        print("\n=== Milestone tables ===")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='synergy_sessions'
            AND table_name IN ('milestones', 'tasks', 'subtasks', 'milestone_comments', 'milestone_history')
        """)
        tables = [row[0] for row in cur.fetchall()]
        milestone_tables = ['milestones', 'tasks', 'subtasks', 'milestone_comments', 'milestone_history']
        for table in milestone_tables:
            exists = table in tables
            status = "EXISTS" if exists else "MISSING"
            print(f"  {status}: {table}")
        
        conn.close()
        
        # Check if we need to run schema update
        missing_cols = [c for c in milestone_cols if c not in columns]
        missing_tables = [t for t in milestone_tables if t not in tables]
        
        if missing_cols or missing_tables:
            print(f"\n=== Schema update needed ===")
            print(f"Missing columns: {len(missing_cols)}")
            print(f"Missing tables: {len(missing_tables)}")
            return False
        else:
            print(f"\n=== Schema is up-to-date ===")
            return True
            
    except Exception as e:
        print(f"Error checking schema: {e}")
        return None

if __name__ == "__main__":
    check_schema()
