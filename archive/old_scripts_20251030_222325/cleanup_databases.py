"""
Database Cleanup Script - Remove Duplicate Databases
====================================================

PRODUCTION DATABASES (KEEP):
1. AI_infrastructure/ai_infrastructure.db (232 KB, 13 tables) - MAIN USER/OAUTH DATABASE
2. AI_infrastructure/data/sessions.db (4.57 MB, 7 tables) - SESSION STORAGE

DELETE (Duplicates/Empty/Backups):
- ai_agents.db (32 KB, root) - Unknown/unused
- ai_infrastructure.db (0 B, root) - Empty duplicate
- AI_infrastructure/data/ai_infrastructure.db (16 KB, 2 tables) - Wrong location
- AI_infrastructure/data/users.db (unknown size, 3 tables) - Consolidated into ai_infrastructure.db
- data/sessions.db (12 KB, 1 table) - Old version
- data/synergy_sessions.db (140 KB, 7 tables) - Old Kanban system
- AI_infrastructure/meta_tools/data/sessions.db (12 KB) - Duplicate

BACKUPS TO DELETE (All migrations complete):
- AI_infrastructure/ai_infrastructure_backup_20251030_142125.db (184 KB)
- AI_infrastructure/data/ai_infrastructure_backup_20251030_143153.db (16 KB)
- AI_infrastructure/data/ai_infrastructure_backup_final_20251030_143418.db (16 KB)
- AI_infrastructure/ai_infrastructure_backup_final_20251030_144020.db (212 KB)
- AI_infrastructure/data/sessions_backup_20251027_124900.db (2.32 MB)
- AI_infrastructure/data/sessions_backup_20251027_124918.db (2.32 MB)

CORRECT DATABASE PATHS (to update in code):
- Main database: AI_infrastructure/ai_infrastructure.db
- Sessions database: AI_infrastructure/data/sessions.db
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Root directory
ROOT_DIR = Path(__file__).parent

# Databases to DELETE
DATABASES_TO_DELETE = [
    # Root level duplicates/empty (KEEP ai_agents.db per user request)
    # ROOT_DIR / 'ai_agents.db',  # KEEP THIS ONE
    ROOT_DIR / 'ai_infrastructure.db',
    
    # Wrong location
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'ai_infrastructure.db',
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'users.db',
    
    # Old versions
    ROOT_DIR / 'data' / 'sessions.db',
    ROOT_DIR / 'data' / 'synergy_sessions.db',
    
    # Meta tools duplicate
    ROOT_DIR / 'AI_infrastructure' / 'meta_tools' / 'data' / 'sessions.db',
    
    # All backups
    ROOT_DIR / 'AI_infrastructure' / 'ai_infrastructure_backup_20251030_142125.db',
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'ai_infrastructure_backup_20251030_143153.db',
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'ai_infrastructure_backup_final_20251030_143418.db',
    ROOT_DIR / 'AI_infrastructure' / 'ai_infrastructure_backup_final_20251030_144020.db',
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'sessions_backup_20251027_124900.db',
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'sessions_backup_20251027_124918.db',
]

# Production databases (KEEP - DO NOT DELETE)
PRODUCTION_DATABASES = [
    ROOT_DIR / 'AI_infrastructure' / 'ai_infrastructure.db',  # 232 KB, 13 tables - MAIN
    ROOT_DIR / 'AI_infrastructure' / 'data' / 'sessions.db',  # 4.57 MB, 7 tables - SESSIONS
]


def analyze_databases():
    """Analyze which databases exist and their sizes"""
    print("=" * 80)
    print("DATABASE ANALYSIS")
    print("=" * 80)
    
    print("\nPRODUCTION DATABASES (WILL KEEP):")
    for db in PRODUCTION_DATABASES:
        if db.exists():
            size_mb = db.stat().st_size / (1024 * 1024)
            print(f"   {db.relative_to(ROOT_DIR)}")
            print(f"      Size: {size_mb:.2f} MB")
            print(f"      Modified: {datetime.fromtimestamp(db.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"    {db.relative_to(ROOT_DIR)} - NOT FOUND (CRITICAL!)")
    
    print("\n DATABASES TO DELETE:")
    found_count = 0
    total_size = 0
    
    for db in DATABASES_TO_DELETE:
        if db.exists():
            size_mb = db.stat().st_size / (1024 * 1024)
            total_size += size_mb
            found_count += 1
            print(f"   🗑️  {db.relative_to(ROOT_DIR)}")
            print(f"      Size: {size_mb:.2f} MB")
        else:
            print(f"   ⚠️  {db.relative_to(ROOT_DIR)} - Already deleted")
    
    print(f"\n📊 Summary: {found_count} files to delete, total size: {total_size:.2f} MB")
    
    return found_count, total_size


def backup_production_databases():
    """Create backup of production databases before cleanup"""
    print("\n" + "=" * 80)
    print("CREATING SAFETY BACKUPS")
    print("=" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = ROOT_DIR / 'AI_infrastructure' / 'data' / f'backup_before_cleanup_{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for db in PRODUCTION_DATABASES:
        if db.exists():
            backup_file = backup_dir / db.name
            shutil.copy2(db, backup_file)
            print(f"   Backed up: {db.relative_to(ROOT_DIR)} → {backup_file.relative_to(ROOT_DIR)}")
        else:
            print(f"    Cannot backup (not found): {db.relative_to(ROOT_DIR)}")
    
    print(f"\nBackups saved to: {backup_dir.relative_to(ROOT_DIR)}")
    return backup_dir


def delete_duplicate_databases(dry_run=True):
    """Delete duplicate/old databases"""
    print("\n" + "=" * 80)
    if dry_run:
        print("DRY RUN - NO FILES WILL BE DELETED")
    else:
        print("DELETING DUPLICATE DATABASES")
    print("=" * 80)
    
    deleted_count = 0
    total_freed = 0
    
    for db in DATABASES_TO_DELETE:
        if db.exists():
            size_mb = db.stat().st_size / (1024 * 1024)
            
            if dry_run:
                print(f"   🔍 Would delete: {db.relative_to(ROOT_DIR)} ({size_mb:.2f} MB)")
            else:
                try:
                    db.unlink()
                    print(f"   Deleted: {db.relative_to(ROOT_DIR)} ({size_mb:.2f} MB)")
                    deleted_count += 1
                    total_freed += size_mb
                except Exception as e:
                    print(f"    Failed to delete {db.relative_to(ROOT_DIR)}: {e}")
    
    if not dry_run:
        print(f"\nCleanup complete: {deleted_count} files deleted, {total_freed:.2f} MB freed")
    
    return deleted_count, total_freed


def verify_production_databases():
    """Verify production databases are intact"""
    print("\n" + "=" * 80)
    print("VERIFICATION - PRODUCTION DATABASES")
    print("=" * 80)
    
    all_good = True
    
    for db in PRODUCTION_DATABASES:
        if db.exists():
            size_mb = db.stat().st_size / (1024 * 1024)
            print(f"   {db.relative_to(ROOT_DIR)} - OK ({size_mb:.2f} MB)")
        else:
            print(f"    {db.relative_to(ROOT_DIR)} - MISSING (CRITICAL!)")
            all_good = False
    
    if all_good:
        print("\n🎉 All production databases intact!")
    else:
        print("\n⚠️  WARNING: Some production databases are missing!")
    
    return all_good


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("DATABASE CLEANUP SCRIPT")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Analyze all database files")
    print("2. Create safety backups of production databases")
    print("3. Delete duplicate/backup/empty databases")
    print("4. Verify production databases are intact")
    
    # Step 1: Analyze
    found_count, total_size = analyze_databases()
    
    if found_count == 0:
        print("\nNo duplicate databases found - cleanup already complete!")
        verify_production_databases()
        exit(0)
    
    # Step 2: Confirm
    print("\n" + "=" * 80)
    response = input(f"\nDelete {found_count} duplicate databases ({total_size:.2f} MB)? [y/N]: ")
    
    if response.lower() != 'y':
        print("\n Cleanup cancelled by user")
        exit(0)
    
    # Step 3: Backup production databases
    backup_dir = backup_production_databases()
    
    # Step 4: Delete duplicates
    deleted_count, total_freed = delete_duplicate_databases(dry_run=False)
    
    # Step 5: Verify
    all_good = verify_production_databases()
    
    # Summary
    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Deleted: {deleted_count} files")
    print(f"Freed: {total_freed:.2f} MB")
    print(f"Backups: {backup_dir.relative_to(ROOT_DIR)}")
    print(f"Production DBs: {'OK' if all_good else 'CHECK REQUIRED'}")
    print("\nProduction databases:")
    print("  • AI_infrastructure/ai_infrastructure.db (users, oauth, auth)")
    print("  • AI_infrastructure/data/sessions.db (conversation history)")
