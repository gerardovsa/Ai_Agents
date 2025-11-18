"""Check and update SQLite Synergy Sessions schema for milestone system"""

import sqlite3
import os
from pathlib import Path

# Get database path
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

def check_schema():
    """Check if milestone columns and tables exist"""
    print(f"Checking database: {db_path}")
    print("=" * 60)
    
    if not db_path.exists():
        print("ERROR: Database does not exist!")
        print(f"Expected location: {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    # Check synergy_sessions columns
    print("\n=== Current synergy_sessions columns ===")
    cur.execute("PRAGMA table_info(synergy_sessions)")
    columns = [row[1] for row in cur.fetchall()]
    for col in columns:
        print(f"  - {col}")
    
    # Check for milestone columns
    print("\n=== Milestone system columns ===")
    milestone_cols = ['uses_milestones', 'next_steps_deprecated', 'checklist_deprecated', 'message_count', 'migration_date']
    missing_cols = []
    for col in milestone_cols:
        exists = col in columns
        status = "EXISTS" if exists else "MISSING"
        print(f"  [{status}] {col}")
        if not exists:
            missing_cols.append(col)
    
    # Check for milestone tables
    print("\n=== Milestone tables ===")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    milestone_tables = ['milestones', 'tasks', 'subtasks', 'milestone_comments', 'milestone_history']
    missing_tables = []
    for table in milestone_tables:
        exists = table in tables
        status = "EXISTS" if exists else "MISSING"
        print(f"  [{status}] {table}")
        if not exists:
            missing_tables.append(table)
    
    # Check for views
    print("\n=== Progress calculation views ===")
    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = [row[0] for row in cur.fetchall()]
    progress_views = ['v_milestone_progress', 'v_task_progress']
    missing_views = []
    for view in progress_views:
        exists = view in views
        status = "EXISTS" if exists else "MISSING"
        print(f"  [{status}] {view}")
        if not exists:
            missing_views.append(view)
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    if missing_cols or missing_tables or missing_views:
        print("SCHEMA UPDATE NEEDED")
        print(f"  Missing columns: {len(missing_cols)}")
        print(f"  Missing tables: {len(missing_tables)}")
        print(f"  Missing views: {len(missing_views)}")
        return False
    else:
        print("SCHEMA IS UP-TO-DATE!")
        return True

def apply_schema_update():
    """Apply schema update from synergy_schema_update_nov19.sql"""
    schema_file = root_dir / 'data' / 'synergy_schema_update_nov19.sql'
    
    if not schema_file.exists():
        print(f"ERROR: Schema update file not found: {schema_file}")
        return False
    
    print(f"\nApplying schema update from: {schema_file.name}")
    print("=" * 60)
    
    # Read SQL file
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # SQLite doesn't support schema prefixes like synergy_sessions.tablename
    # Remove schema prefix for SQLite
    sql_content = sql_content.replace('synergy_sessions.synergy_sessions', 'synergy_sessions')
    sql_content = sql_content.replace('synergy_sessions.milestones', 'milestones')
    sql_content = sql_content.replace('synergy_sessions.tasks', 'tasks')
    sql_content = sql_content.replace('synergy_sessions.subtasks', 'subtasks')
    sql_content = sql_content.replace('synergy_sessions.milestone_comments', 'milestone_comments')
    sql_content = sql_content.replace('synergy_sessions.milestone_history', 'milestone_history')
    
    # SQLite uses IF NOT EXISTS instead of ADD COLUMN IF NOT EXISTS
    # This is already correct in our SQL
    
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    try:
        # Execute each statement separately
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
            
            # Skip verification queries
            if statement.upper().startswith('SELECT COUNT'):
                continue
            
            try:
                cur.execute(statement)
                # Determine statement type
                stmt_type = statement.split()[0].upper()
                if 'ALTER TABLE' in statement.upper():
                    print(f"  [{i}] Added column")
                elif stmt_type == 'CREATE' and 'TABLE' in statement.upper():
                    table_name = statement.split('TABLE')[1].split('(')[0].strip()
                    print(f"  [{i}] Created table: {table_name}")
                elif stmt_type == 'CREATE' and 'INDEX' in statement.upper():
                    index_name = statement.split('INDEX')[1].split('ON')[0].strip()
                    print(f"  [{i}] Created index: {index_name}")
                elif stmt_type == 'CREATE' and 'VIEW' in statement.upper():
                    view_name = statement.split('VIEW')[1].split('AS')[0].strip()
                    print(f"  [{i}] Created view: {view_name}")
                else:
                    print(f"  [{i}] Executed statement")
            except sqlite3.OperationalError as e:
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'duplicate column' in error_msg:
                    print(f"  [{i}] Skipped (already exists)")
                else:
                    print(f"  [{i}] ERROR: {e}")
                    raise
        
        conn.commit()
        print("\n" + "=" * 60)
        print("SCHEMA UPDATE COMPLETE!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR during schema update: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("SYNERGY MILESTONE SYSTEM - SCHEMA UPDATE")
    print("=" * 60)
    
    # Check current schema
    is_up_to_date = check_schema()
    
    if not is_up_to_date:
        print("\n" + "=" * 60)
        response = input("Apply schema update? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            success = apply_schema_update()
            if success:
                print("\nVerifying schema update...")
                check_schema()
        else:
            print("Schema update cancelled.")
    else:
        print("\nNo action needed - schema is already up-to-date!")
