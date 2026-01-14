"""
Cleanup Orphaned Thread Assignments
from shared.database_utils import convert_sql_placeholders

This script removes thread assignments from users.metadata for threads that no longer exist.
Ensures database integrity by cleaning up stale references.

Usage:
    python cleanup_orphaned_assignments.py [--dry-run]
"""

import sqlite3
import json
from pathlib import Path
import sys

def cleanup_orphaned_assignments(dry_run=True):
    """
    Clean up thread assignments for non-existent threads
    
    Args:
        dry_run: If True, only report issues without fixing
    """
    root_dir = Path(__file__).parent
    db_path = root_dir / 'data' / 'sessions.db'
    
    print(f"{'='*60}")
    print(f"ORPHANED THREAD ASSIGNMENT CLEANUP")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will update database)'}")
    print(f"Database: {db_path}")
    print(f"{'='*60}\n")
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all thread IDs that exist
    cursor.execute("SELECT thread_slug FROM threads")
    valid_thread_ids = set(row[0] for row in cursor.fetchall())
    print(f"Found {len(valid_thread_ids)} valid threads in database\n")
    
    # Get all users with metadata
    cursor.execute("SELECT id, username, email, metadata FROM users WHERE metadata IS NOT NULL")
    users = cursor.fetchall()
    
    print(f"Checking {len(users)} users for orphaned assignments...\n")
    
    total_orphans = 0
    users_with_orphans = 0
    
    for user_id, username, email, metadata_json in users:
        try:
            metadata = json.loads(metadata_json or '{}')
            assignments = metadata.get('thread_assignments', {})
            
            if not assignments:
                continue
            
            print(f"User {user_id} ({username or email}):")
            print(f"  Current assignments: {len(assignments)}")
            
            # Check each assignment
            orphaned = {}
            valid = {}
            
            for location, thread_id in assignments.items():
                if thread_id not in valid_thread_ids:
                    orphaned[location] = thread_id
                    total_orphans += 1
                    print(f"    ORPHAN: {location} → '{thread_id}' (thread not found)")
                else:
                    valid[location] = thread_id
            
            if orphaned:
                users_with_orphans += 1
                print(f"  Valid assignments: {len(valid)}")
                print(f"  Orphaned assignments: {len(orphaned)}")
                
                if not dry_run:
                    # Update metadata with only valid assignments
                    metadata['thread_assignments'] = valid
                    new_metadata_json = json.dumps(metadata)
                    
                    cursor.execute(
                        "UPDATE users SET metadata = ? WHERE id = ?",
                        (new_metadata_json, user_id)
                    )
                    print(f"  ✅ Cleaned up {len(orphaned)} orphaned assignments")
                else:
                    print(f"  [DRY RUN] Would remove {len(orphaned)} orphaned assignments")
            else:
                print(f"  ✅ All assignments valid")
            
            print()
            
        except json.JSONDecodeError as e:
            print(f"  ERROR: Failed to parse metadata: {e}\n")
            continue
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    # Summary
    print(f"{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total orphaned assignments found: {total_orphans}")
    print(f"Users affected: {users_with_orphans}")
    
    if dry_run:
        print(f"\n[DRY RUN] No changes made")
        print(f"Run with '--fix' flag to clean up orphaned assignments")
    else:
        print(f"\n✅ Database updated - {total_orphans} orphaned assignments removed")
    
    print(f"{'='*60}\n")
    
    return total_orphans, users_with_orphans

def main():
    dry_run = '--fix' not in sys.argv
    
    if dry_run:
        print("\n⚠️  Running in DRY RUN mode\n")
    else:
        print("\n🔧 Running in LIVE mode - will update database\n")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled")
            return
    
    cleanup_orphaned_assignments(dry_run=dry_run)

if __name__ == '__main__':
    main()
