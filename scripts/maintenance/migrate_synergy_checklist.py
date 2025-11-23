"""
Migrate Synergy Sessions - Checklist Field Normalization
==========================================================
from shared.database_utils import convert_sql_placeholders

Normalizes checklist field to ensure:
1. Field name is 'task' (not 'text' or 'item')
2. All items have 'subtasks' array (even if empty)
3. Subtasks also use 'task' field name

BEFORE:  [{"text": "Do this", "completed": false}]
AFTER:   [{"task": "Do this", "completed": false, "completed_at": null, "subtasks": []}]

BEFORE:  [{"task": "Main", "subtasks": [{"item": "Sub1"}]}]
AFTER:   [{"task": "Main", "completed": false, "completed_at": null, "subtasks": [{"task": "Sub1", "completed": false}]}]

Usage:
    python scripts/maintenance/migrate_synergy_checklist.py
    python scripts/maintenance/migrate_synergy_checklist.py --dry-run
    python scripts/maintenance/migrate_synergy_checklist.py --backup
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import argparse


def normalize_checklist(items):
    """
    Normalize checklist items ensuring 'task' field exists and subtasks are preserved
    
    Handles three field name variations:
    - Old format: {"text": "...", "completed": false}
    - UI format: {"item": "...", "completed": false}
    - Correct format: {"task": "...", "completed": false, "subtasks": []}
    
    Returns standardized format with task field and subtasks array.
    """
    if not items:
        return []
    
    normalized = []
    for item in items:
        if isinstance(item, dict):
            # Get task text from any field name variation
            task_text = item.get('task') or item.get('item') or item.get('text', '')
            
            # Skip empty items
            if not task_text:
                continue
            
            # Normalize subtasks (recursively handle field name variations)
            subtasks = item.get('subtasks', [])
            normalized_subtasks = []
            
            for subtask in subtasks:
                if isinstance(subtask, dict):
                    subtask_text = subtask.get('task') or subtask.get('item') or subtask.get('text', '')
                    if subtask_text:
                        normalized_subtasks.append({
                            'task': subtask_text,
                            'completed': subtask.get('completed', False)
                        })
            
            # Build standardized item
            normalized.append({
                'task': task_text,
                'completed': item.get('completed', False),
                'completed_at': item.get('completed_at'),
                'subtasks': normalized_subtasks
            })
    
    return normalized


def backup_database(db_path):
    """Create timestamped backup of database"""
    backup_name = f"synergy_sessions_checklist_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = db_path.parent / backup_name
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def migrate_checklists(dry_run=False, create_backup=True):
    """
    Migrate all checklist fields to standardized format
    
    Args:
        dry_run: If True, only report what would be changed
        create_backup: If True, create backup before migration
    
    Returns:
        Dict with migration statistics
    """
    # Database path
    ROOT_DIR = Path(__file__).parent.parent.parent
    DB_PATH = ROOT_DIR / 'data' / 'synergy_sessions.db'
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return None
    
    # Create backup if requested
    if create_backup and not dry_run:
        backup_database(DB_PATH)
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all sessions with checklist data
    cursor.execute("SELECT session_id, checklist FROM synergy_sessions WHERE checklist IS NOT NULL AND checklist != '[]'")
    sessions = cursor.fetchall()
    
    stats = {
        'total_sessions': len(sessions),
        'field_name_fixes': 0,
        'subtasks_added': 0,
        'subtasks_normalized': 0,
        'already_correct': 0,
        'errors': [],
        'details': []
    }
    
    for session in sessions:
        session_id = session['session_id']
        checklist_json = session['checklist']
        
        if not checklist_json:
            continue
        
        try:
            checklist = json.loads(checklist_json)
            
            if not checklist:
                continue
            
            # Check what needs fixing
            needs_migration = False
            has_wrong_field_name = False
            missing_subtasks_array = False
            has_subtasks_to_normalize = False
            
            for item in checklist:
                # Check field names
                if 'text' in item or 'item' in item:
                    has_wrong_field_name = True
                    needs_migration = True
                
                # Check subtasks array
                if 'subtasks' not in item:
                    missing_subtasks_array = True
                    needs_migration = True
                elif item['subtasks']:
                    # Check if subtasks need normalization
                    for subtask in item['subtasks']:
                        if 'text' in subtask or 'item' in subtask:
                            has_subtasks_to_normalize = True
                            needs_migration = True
            
            if not needs_migration:
                stats['already_correct'] += 1
                continue
            
            # Normalize the checklist
            normalized = normalize_checklist(checklist)
            
            # Track what was fixed
            if has_wrong_field_name:
                stats['field_name_fixes'] += 1
            if missing_subtasks_array:
                stats['subtasks_added'] += 1
            if has_subtasks_to_normalize:
                stats['subtasks_normalized'] += 1
            
            # Log details
            detail = {
                'session_id': session_id,
                'items_count': len(checklist),
                'fixed_field_names': has_wrong_field_name,
                'added_subtasks_arrays': missing_subtasks_array,
                'normalized_subtasks': has_subtasks_to_normalize
            }
            stats['details'].append(detail)
            
            if dry_run:
                print(f"\n📋 {session_id}:")
                print(f"   Items: {len(checklist)}")
                if has_wrong_field_name:
                    print(f"   ⚠️  Field name fix needed (text/item → task)")
                if missing_subtasks_array:
                    print(f"   ➕ Subtasks array will be added")
                if has_subtasks_to_normalize:
                    print(f"   🔧 Subtasks will be normalized")
                print(f"   BEFORE: {json.dumps(checklist[0], indent=6)}")
                print(f"   AFTER:  {json.dumps(normalized[0], indent=6)}")
            else:
                # Update database
                cursor.execute("""
                    UPDATE synergy_sessions 
                    SET checklist = ? 
                    WHERE session_id = ?
                """, (json.dumps(normalized), session_id))
        
        except json.JSONDecodeError as e:
            stats['errors'].append(f"{session_id}: Invalid JSON - {e}")
        except Exception as e:
            stats['errors'].append(f"{session_id}: Migration failed - {e}")
    
    # Commit changes
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    return stats


def print_report(stats, dry_run=False):
    """Print migration report"""
    print("\n" + "="*60)
    print("SYNERGY CHECKLIST MIGRATION REPORT")
    print("="*60)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes made\n")
    else:
        print("✅ MIGRATION COMPLETE\n")
    
    print(f"Total sessions analyzed:     {stats['total_sessions']}")
    print()
    print("FIXES APPLIED:")
    print(f"  Field name fixes:          {stats['field_name_fixes']} sessions")
    print(f"    (text/item → task)")
    print(f"  Subtasks arrays added:     {stats['subtasks_added']} sessions")
    print(f"    (ensure all items have subtasks: [])")
    print(f"  Subtasks normalized:       {stats['subtasks_normalized']} sessions")
    print(f"    (fix field names in subtasks)")
    print(f"  Already correct:           {stats['already_correct']} sessions")
    print()
    
    if stats['details'] and dry_run:
        print("DETAILED CHANGES:")
        for detail in stats['details'][:5]:  # Show first 5
            print(f"  📋 {detail['session_id'][:40]}:")
            print(f"     Items: {detail['items_count']}")
            if detail['fixed_field_names']:
                print(f"     - Field names will be fixed")
            if detail['added_subtasks_arrays']:
                print(f"     - Subtasks arrays will be added")
            if detail['normalized_subtasks']:
                print(f"     - Subtasks will be normalized")
        
        if len(stats['details']) > 5:
            print(f"  ... and {len(stats['details']) - 5} more sessions")
        print()
    
    if stats['errors']:
        print("ERRORS:")
        for error in stats['errors']:
            print(f"  ❌ {error}")
    else:
        print("No errors encountered ✅")
    
    print("="*60)


def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(description='Migrate Synergy checklist fields to standardized format')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup (not recommended)')
    
    args = parser.parse_args()
    
    print("\n🔧 Synergy Checklist Migration Tool")
    print("="*60)
    
    if args.dry_run:
        print("Running in DRY RUN mode...")
        print("No changes will be made to the database")
    else:
        if not args.no_backup:
            print("Will create backup before migration")
        else:
            print("⚠️  WARNING: Running without backup!")
            response = input("Continue without backup? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled")
                return
    
    print()
    
    # Run migration
    stats = migrate_checklists(
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    if stats:
        print_report(stats, dry_run=args.dry_run)
        
        if args.dry_run:
            print("\nℹ️  To apply these changes, run without --dry-run flag")
    else:
        print("❌ Migration failed - check error messages above")


if __name__ == '__main__':
    main()
