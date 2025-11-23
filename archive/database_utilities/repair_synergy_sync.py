"""
Repair Synergy Bidirectional Sync Issues
from shared.database_utils import convert_sql_placeholders

This script fixes mismatched links between threads and Synergy cards:
- Option 1: Update threads.synergy_card_id based on synergy_sessions.thread_ids
- Option 2: Update synergy_sessions.thread_ids based on threads.synergy_card_id
- Option 3: Remove broken links (thread doesn't exist or synergy doesn't exist)

Usage:
    python repair_synergy_sync.py          # Dry run
    python repair_synergy_sync.py --fix    # Execute repairs
"""

import sqlite3
import json
import sys
from pathlib import Path

def repair_synergy_sync(fix=False):
    """Repair bidirectional sync between threads and synergy cards"""
    
    root_dir = Path(__file__).parent
    sessions_db = root_dir / 'data' / 'sessions.db'
    synergy_db = root_dir / 'data' / 'synergy_sessions.db'
    
    print(f"{'='*70}")
    print(f"SYNERGY SYNC REPAIR")
    print(f"{'='*70}\n")
    
    if fix:
        print("MODE: FIX (will modify databases)")
    else:
        print("MODE: DRY RUN (no changes will be made)")
    
    print(f"\nSessions DB: {sessions_db}")
    print(f"Synergy DB:  {synergy_db}\n")
    
    # Connect to both databases
    sessions_conn = sqlite3.connect(str(sessions_db))
    synergy_conn = sqlite3.connect(str(synergy_db))
    
    sessions_cursor = sessions_conn.cursor()
    synergy_cursor = synergy_conn.cursor()
    
    # Get all threads with synergy_card_id
    sessions_cursor.execute("""
        SELECT thread_slug, synergy_card_id
        FROM threads
        WHERE synergy_card_id IS NOT NULL AND synergy_card_id != ''
    """)
    threads_with_synergy = {row[0]: row[1] for row in sessions_cursor.fetchall()}
    
    # Get all synergy sessions with thread_ids
    synergy_cursor.execute("""
        SELECT session_id, thread_ids
        FROM synergy_sessions
        WHERE thread_ids IS NOT NULL AND thread_ids != ''
    """)
    synergy_sessions = {}
    for session_id, thread_ids_json in synergy_cursor.fetchall():
        try:
            thread_ids = json.loads(thread_ids_json)
            synergy_sessions[session_id] = thread_ids
        except json.JSONDecodeError:
            synergy_sessions[session_id] = []
    
    # Track fixes
    fixes_applied = 0
    
    print(f"{'='*70}")
    print(f"ISSUE 1: Threads point to Synergy, but not in Synergy's thread_ids")
    print(f"{'='*70}\n")
    print("SOLUTION: Add thread_id to Synergy's thread_ids array\n")
    
    for thread_id, synergy_id in threads_with_synergy.items():
        if synergy_id in synergy_sessions:
            if thread_id not in synergy_sessions[synergy_id]:
                print(f"Thread {thread_id} → Synergy {synergy_id}")
                print(f"  Action: Add {thread_id} to Synergy's thread_ids array")
                
                if fix:
                    new_thread_ids = synergy_sessions[synergy_id] + [thread_id]
                    synergy_cursor.execute("""
                        UPDATE synergy_sessions
                        SET thread_ids = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = ?
                    """, (json.dumps(new_thread_ids), synergy_id))
                    print(f"  ✅ Fixed")
                    fixes_applied += 1
                else:
                    print(f"  (Dry run - no changes made)")
                
                print()
    
    print(f"{'='*70}")
    print(f"ISSUE 2: Synergy lists threads, but threads don't point back")
    print(f"{'='*70}\n")
    print("SOLUTION: Update thread's synergy_card_id to match\n")
    
    for synergy_id, thread_ids in synergy_sessions.items():
        for thread_id in thread_ids:
            # Check if thread exists
            sessions_cursor.execute("""
                SELECT thread_slug FROM threads WHERE thread_slug = ?
            """, (thread_id,))
            thread_exists = sessions_cursor.fetchone() is not None
            
            if not thread_exists:
                print(f"Synergy {synergy_id} → Thread {thread_id}")
                print(f"  ❌ Thread doesn't exist - removing from Synergy's thread_ids")
                
                if fix:
                    new_thread_ids = [tid for tid in thread_ids if tid != thread_id]
                    synergy_cursor.execute("""
                        UPDATE synergy_sessions
                        SET thread_ids = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = ?
                    """, (json.dumps(new_thread_ids), synergy_id))
                    print(f"  ✅ Removed")
                    fixes_applied += 1
                else:
                    print(f"  (Dry run - no changes made)")
                
                print()
            elif thread_id not in threads_with_synergy:
                print(f"Synergy {synergy_id} → Thread {thread_id}")
                print(f"  Action: Set thread's synergy_card_id to {synergy_id}")
                
                if fix:
                    sessions_cursor.execute("""
                        UPDATE threads
                        SET synergy_card_id = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE thread_slug = ?
                    """, (synergy_id, thread_id))
                    print(f"  ✅ Fixed")
                    fixes_applied += 1
                else:
                    print(f"  (Dry run - no changes made)")
                
                print()
            elif threads_with_synergy[thread_id] != synergy_id:
                current_synergy = threads_with_synergy[thread_id]
                print(f"Synergy {synergy_id} → Thread {thread_id}")
                print(f"  ⚠️  Thread points to different Synergy: {current_synergy}")
                print(f"  Action: Update thread's synergy_card_id to {synergy_id}")
                
                if fix:
                    sessions_cursor.execute("""
                        UPDATE threads
                        SET synergy_card_id = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE thread_slug = ?
                    """, (synergy_id, thread_id))
                    print(f"  ✅ Fixed")
                    fixes_applied += 1
                else:
                    print(f"  (Dry run - no changes made)")
                
                print()
    
    # Commit changes
    if fix:
        sessions_conn.commit()
        synergy_conn.commit()
        print(f"\n✅ Applied {fixes_applied} fixes to databases")
    else:
        print(f"\n(Dry run complete - {fixes_applied} issues detected)")
        print(f"Run with '--fix' flag to apply repairs")
    
    sessions_conn.close()
    synergy_conn.close()
    
    print(f"\n{'='*70}")
    print(f"REPAIR COMPLETE")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    fix_mode = '--fix' in sys.argv
    repair_synergy_sync(fix=fix_mode)
