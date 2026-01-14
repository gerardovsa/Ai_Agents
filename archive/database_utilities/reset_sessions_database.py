"""
Reset Sessions Database - Clean Slate

This script will:
1. Backup current sessions.db
2. Delete all threads and messages
3. Keep user accounts but clear metadata
4. Reset to fresh state

Usage:
    python reset_sessions_database.py          # Dry run (shows what will be deleted)
    python reset_sessions_database.py --reset  # Actually reset database
"""

import sqlite3
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime

def reset_sessions_database(actually_reset=False):
    """Reset sessions database to clean state"""
    
    root_dir = Path(__file__).parent
    db_path = root_dir / 'data' / 'sessions.db'
    
    print(f"{'='*70}")
    print(f"SESSIONS DATABASE RESET")
    print(f"{'='*70}\n")
    
    if actually_reset:
        print("MODE: RESET (will modify database)")
    else:
        print("MODE: DRY RUN (no changes will be made)")
    
    print(f"\nDatabase: {db_path}\n")
    
    if not db_path.exists():
        print(f"ERROR: Database not found")
        return
    
    # Backup database first
    if actually_reset:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = root_dir / 'data' / f'sessions_backup_{timestamp}.db'
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}\n")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get current counts
    cursor.execute("SELECT COUNT(*) FROM threads")
    thread_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    message_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    print(f"{'='*70}")
    print(f"CURRENT DATABASE STATE")
    print(f"{'='*70}")
    print(f"Threads: {thread_count}")
    print(f"Messages: {message_count}")
    print(f"Users: {user_count}\n")
    
    # Show threads
    cursor.execute("""
        SELECT thread_slug, name, created_at
        FROM threads
        ORDER BY created_at DESC
    """)
    threads = cursor.fetchall()
    
    if threads:
        print(f"{'='*70}")
        print(f"THREADS TO DELETE ({len(threads)})")
        print(f"{'='*70}")
        for t in threads[:10]:  # Show first 10
            print(f"- {t['thread_slug']}: {t['name']} (created {t['created_at']})")
        if len(threads) > 10:
            print(f"... and {len(threads) - 10} more")
        print()
    
    # Show users
    cursor.execute("SELECT id, username, email, metadata FROM users")
    users = cursor.fetchall()
    
    if users:
        print(f"{'='*70}")
        print(f"USERS (will keep accounts, clear metadata)")
        print(f"{'='*70}")
        for u in users:
            metadata = u['metadata']
            if metadata:
                try:
                    meta_obj = json.loads(metadata)
                    assignments = meta_obj.get('thread_assignments', {})
                    print(f"- User {u['id']} ({u['username']}): {len(assignments)} thread assignments")
                except:
                    print(f"- User {u['id']} ({u['username']}): Invalid metadata")
            else:
                print(f"- User {u['id']} ({u['username']}): No metadata")
        print()
    
    # Execute reset
    if actually_reset:
        print(f"{'='*70}")
        print(f"EXECUTING RESET")
        print(f"{'='*70}\n")
        
        # Delete messages
        cursor.execute("DELETE FROM messages")
        print(f"✅ Deleted {message_count} messages")
        
        # Delete threads
        cursor.execute("DELETE FROM threads")
        print(f"✅ Deleted {thread_count} threads")
        
        # Clear user metadata (keep accounts)
        cursor.execute("""
            UPDATE users 
            SET metadata = '{}', 
                last_active = CURRENT_TIMESTAMP
        """)
        print(f"✅ Cleared metadata for {user_count} users")
        
        conn.commit()
        
        print(f"\n{'='*70}")
        print(f"RESET COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Database reset to clean state")
        print(f"✅ User accounts preserved: {user_count}")
        print(f"✅ All threads and messages deleted")
        print(f"✅ All thread assignments cleared")
        print(f"\n📝 Backup saved: {backup_path}")
        
    else:
        print(f"{'='*70}")
        print(f"DRY RUN SUMMARY")
        print(f"{'='*70}")
        print(f"Would delete: {thread_count} threads")
        print(f"Would delete: {message_count} messages")
        print(f"Would clear metadata for: {user_count} users")
        print(f"Would preserve: {user_count} user accounts")
        print(f"\n🔸 Run with '--reset' flag to execute")
    
    conn.close()
    print(f"{'='*70}\n")

if __name__ == '__main__':
    reset_mode = '--reset' in sys.argv
    reset_sessions_database(actually_reset=reset_mode)
