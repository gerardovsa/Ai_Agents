"""
Migrate Synergy Sessions - Next Steps Field Format
===================================================
from shared.database_utils import convert_sql_placeholders

Converts next_steps field from simple string arrays to rich object arrays
with completion tracking capabilities.

BEFORE:  ["Phase 1", "Phase 2", "Phase 3"]
AFTER:   [
    {"description": "Phase 1", "completed": false, "due_date": null, "completed_at": null},
    {"description": "Phase 2", "completed": false, "due_date": null, "completed_at": null},
    {"description": "Phase 3", "completed": false, "due_date": null, "completed_at": null}
]

Also fixes documents field name mismatch (converts 'name' to 'title').

Usage:
    python scripts/maintenance/migrate_synergy_next_steps.py
    python scripts/maintenance/migrate_synergy_next_steps.py --dry-run
    python scripts/maintenance/migrate_synergy_next_steps.py --backup
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import argparse


def normalize_next_steps(steps):
    """
    Convert string arrays to object arrays for next_steps field
    
    Args:
        steps: Array of strings OR objects
    
    Returns:
        Array of objects with {description, completed, due_date, completed_at}
    """
    if not steps:
        return []
    
    normalized = []
    for step in steps:
        if isinstance(step, str):
            # Convert string to rich object
            normalized.append({
                'description': step,
                'completed': False,
                'due_date': None,
                'completed_at': None
            })
        elif isinstance(step, dict):
            # Ensure object has all required fields
            normalized.append({
                'description': step.get('description', ''),
                'completed': step.get('completed', False),
                'due_date': step.get('due_date'),
                'completed_at': step.get('completed_at')
            })
        else:
            # Skip invalid entries
            continue
    
    return normalized


def normalize_documents(docs):
    """
    Convert documents array ensuring 'title' field exists (fix 'name' → 'title')
    
    Args:
        docs: Array of document objects
    
    Returns:
        Array of objects with {title, url, type}
    """
    if not docs:
        return []
    
    normalized = []
    for doc in docs:
        if isinstance(doc, dict):
            # Convert 'name' field to 'title' if needed
            title = doc.get('title') or doc.get('name', '')
            normalized.append({
                'title': title,
                'url': doc.get('url', ''),
                'type': doc.get('type', 'document')
            })
    
    return normalized


def backup_database(db_path):
    """Create timestamped backup of database"""
    backup_name = f"synergy_sessions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = db_path.parent / backup_name
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def migrate_sessions(dry_run=False, create_backup=True):
    """
    Migrate all sessions to new format
    
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
    
    # Get all sessions
    cursor.execute("SELECT session_id, next_steps, documents FROM synergy_sessions")
    sessions = cursor.fetchall()
    
    stats = {
        'total_sessions': len(sessions),
        'next_steps_migrated': 0,
        'next_steps_already_ok': 0,
        'next_steps_empty': 0,
        'documents_migrated': 0,
        'documents_already_ok': 0,
        'documents_empty': 0,
        'errors': []
    }
    
    for session in sessions:
        session_id = session['session_id']
        next_steps_json = session['next_steps']
        documents_json = session['documents']
        
        # Process next_steps
        needs_migration = False
        migrated_next_steps = None
        
        if next_steps_json:
            try:
                steps = json.loads(next_steps_json)
                
                if steps:
                    # Check if migration needed (any string entries)
                    has_strings = any(isinstance(step, str) for step in steps)
                    
                    if has_strings:
                        migrated_next_steps = normalize_next_steps(steps)
                        stats['next_steps_migrated'] += 1
                        needs_migration = True
                        
                        if dry_run:
                            print(f"\n📋 {session_id}:")
                            print(f"  BEFORE: {steps[:2]}... ({len(steps)} steps)")
                            print(f"  AFTER:  {migrated_next_steps[:2]}... ({len(migrated_next_steps)} steps)")
                    else:
                        stats['next_steps_already_ok'] += 1
                else:
                    stats['next_steps_empty'] += 1
            except json.JSONDecodeError as e:
                stats['errors'].append(f"{session_id}: Invalid next_steps JSON - {e}")
        else:
            stats['next_steps_empty'] += 1
        
        # Process documents
        migrated_documents = None
        
        if documents_json:
            try:
                docs = json.loads(documents_json)
                
                if docs:
                    # Check if migration needed (any 'name' field instead of 'title')
                    has_name_field = any(isinstance(doc, dict) and 'name' in doc and 'title' not in doc for doc in docs)
                    
                    if has_name_field:
                        migrated_documents = normalize_documents(docs)
                        stats['documents_migrated'] += 1
                        needs_migration = True
                        
                        if dry_run:
                            print(f"\n📄 {session_id} DOCUMENTS:")
                            print(f"  BEFORE: {docs[:2]}... ({len(docs)} docs)")
                            print(f"  AFTER:  {migrated_documents[:2]}... ({len(migrated_documents)} docs)")
                    else:
                        stats['documents_already_ok'] += 1
                else:
                    stats['documents_empty'] += 1
            except json.JSONDecodeError as e:
                stats['errors'].append(f"{session_id}: Invalid documents JSON - {e}")
        else:
            stats['documents_empty'] += 1
        
        # Update database if not dry run
        if needs_migration and not dry_run:
            try:
                updates = []
                params = []
                
                if migrated_next_steps is not None:
                    updates.append("next_steps = ?")
                    params.append(json.dumps(migrated_next_steps))
                
                if migrated_documents is not None:
                    updates.append("documents = ?")
                    params.append(json.dumps(migrated_documents))
                
                if updates:
                    params.append(session_id)
                    query = f"UPDATE synergy_sessions SET {', '.join(updates)} WHERE session_id = ?"
                    cursor.execute(query, params)
            except Exception as e:
                stats['errors'].append(f"{session_id}: Update failed - {e}")
    
    # Commit changes
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    return stats


def print_report(stats, dry_run=False):
    """Print migration report"""
    print("\n" + "="*60)
    print("SYNERGY SESSIONS MIGRATION REPORT")
    print("="*60)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes made\n")
    else:
        print("✅ MIGRATION COMPLETE\n")
    
    print(f"Total sessions:              {stats['total_sessions']}")
    print()
    print("NEXT_STEPS FIELD:")
    print(f"  Migrated:                  {stats['next_steps_migrated']}")
    print(f"  Already correct format:    {stats['next_steps_already_ok']}")
    print(f"  Empty/null:                {stats['next_steps_empty']}")
    print()
    print("DOCUMENTS FIELD:")
    print(f"  Migrated ('name'→'title'): {stats['documents_migrated']}")
    print(f"  Already correct format:    {stats['documents_already_ok']}")
    print(f"  Empty/null:                {stats['documents_empty']}")
    print()
    
    if stats['errors']:
        print("ERRORS:")
        for error in stats['errors']:
            print(f"  ❌ {error}")
    else:
        print("No errors encountered")
    
    print("="*60)


def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(description='Migrate Synergy sessions to new field formats')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup (not recommended)')
    
    args = parser.parse_args()
    
    print("\n🔧 Synergy Sessions Migration Tool")
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
    stats = migrate_sessions(
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
