"""
Cleanup AI Infrastructure Database - Remove Redundant Tables

This script will:
1. DROP empty/redundant tables from ai_infrastructure.db
2. Keep active tables (oauth_tokens, users, user_sessions, etc.)
3. Create backup before changes

Tables to DELETE:
- user_email_aliases (empty)
- user_gmail_accounts (empty - replaced by oauth_tokens)
- user_platform_credentials (2 rows but old format)
- _ARCHIVED_user_gmail_accounts (5 rows - old table)
- _ARCHIVED_user_platform_credentials (12 rows - old table)
- oauth_tokens_backup_jan2025 (4 rows - backup from January)
- account_link_requests (empty)
- kanban_task_links (empty)
- user_account_links (empty)
- thread_assignments (empty - redundant)

Usage:
    python cleanup_infrastructure_db.py          # Dry run
    python cleanup_infrastructure_db.py --clean  # Execute cleanup
"""

import sqlite3
import sys
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_infrastructure_db(actually_clean=False):
    """Remove redundant tables from ai_infrastructure.db"""
    
    root_dir = Path(__file__).parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    print(f"{'='*70}")
    print(f"AI INFRASTRUCTURE DB CLEANUP")
    print(f"{'='*70}\n")
    
    if actually_clean:
        print("MODE: CLEAN (will drop tables)")
    else:
        print("MODE: DRY RUN (no changes will be made)")
    
    print(f"\nDatabase: {db_path}\n")
    
    if not db_path.exists():
        print(f"ERROR: Database not found")
        return
    
    # Backup database first
    if actually_clean:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = root_dir / 'data' / f'ai_infrastructure_backup_{timestamp}.db'
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}\n")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Tables to drop
    tables_to_drop = [
        'user_email_aliases',
        'user_gmail_accounts',
        'user_platform_credentials',
        '_ARCHIVED_user_gmail_accounts',
        '_ARCHIVED_user_platform_credentials',
        'oauth_tokens_backup_jan2025',
        'account_link_requests',
        'kanban_task_links',
        'user_account_links',
        'thread_assignments'
    ]
    
    print(f"{'='*70}")
    print(f"TABLES TO DROP ({len(tables_to_drop)})")
    print(f"{'='*70}\n")
    
    # Check each table and show row counts
    for table_name in tables_to_drop:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"📊 {table_name}: {row_count} rows")
        except sqlite3.OperationalError:
            print(f"⚠️  {table_name}: Table doesn't exist (already dropped)")
    
    print()
    
    # Get list of tables to keep
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    tables_to_keep = [t for t in all_tables if t not in tables_to_drop]
    
    print(f"{'='*70}")
    print(f"TABLES TO KEEP ({len(tables_to_keep)})")
    print(f"{'='*70}\n")
    
    for table_name in tables_to_keep:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"✅ {table_name}: {row_count} rows")
    
    print()
    
    # Execute cleanup
    if actually_clean:
        print(f"{'='*70}")
        print(f"EXECUTING CLEANUP")
        print(f"{'='*70}\n")
        
        dropped_count = 0
        
        for table_name in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"✅ Dropped table: {table_name}")
                dropped_count += 1
            except sqlite3.Error as e:
                print(f"❌ Error dropping {table_name}: {e}")
        
        conn.commit()
        
        print(f"\n{'='*70}")
        print(f"CLEANUP COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Dropped {dropped_count} tables")
        print(f"✅ Kept {len(tables_to_keep)} tables")
        print(f"✅ Database cleaned successfully")
        print(f"\n📝 Backup saved: {backup_path}")
        
    else:
        print(f"{'='*70}")
        print(f"DRY RUN SUMMARY")
        print(f"{'='*70}")
        print(f"Would drop: {len(tables_to_drop)} tables")
        print(f"Would keep: {len(tables_to_keep)} tables")
        print(f"\n🔸 Run with '--clean' flag to execute")
    
    conn.close()
    print(f"{'='*70}\n")

if __name__ == '__main__':
    clean_mode = '--clean' in sys.argv
    cleanup_infrastructure_db(actually_clean=clean_mode)
