"""
Sync Synergy Thread Links (One-Time Operation)
===============================================
Syncs thread_ids in synergy_sessions to match synergy_card_id in threads.
Safe operation - only updates synergy_sessions, never touches threads table.
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
import json
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).parent
SESSIONS_DB = ROOT_DIR / 'data' / 'sessions.db'
SYNERGY_DB = ROOT_DIR / 'data' / 'synergy_sessions.db'


def sync_synergy_thread_links():
    """Sync thread_ids in Synergy sessions based on threads.synergy_card_id"""
    
    print("=" * 80)
    print("SYNERGY THREAD LINK SYNC")
    print("=" * 80)
    
    # Step 1: Read all threads with synergy links
    print("\nStep 1: Reading threads with Synergy links...")
    threads_conn = sqlite3.connect(SESSIONS_DB)
    cursor = threads_conn.execute("""
        SELECT id, thread_slug, name, synergy_card_id 
        FROM threads 
        WHERE synergy_card_id IS NOT NULL AND synergy_card_id != ''
    """)
    
    threads_with_synergy = cursor.fetchall()
    threads_conn.close()
    
    print(f"Found {len(threads_with_synergy)} threads with Synergy links")
    
    # Step 2: Group threads by synergy_card_id
    print("\nStep 2: Grouping threads by Synergy project...")
    synergy_to_threads = defaultdict(list)
    
    for thread_id, thread_slug, thread_name, synergy_id in threads_with_synergy:
        synergy_to_threads[synergy_id].append({
            'id': thread_id,
            'slug': thread_slug,
            'name': thread_name
        })
        print(f"  {synergy_id} ← thread: {thread_name[:50]}")
    
    print(f"\nGrouped into {len(synergy_to_threads)} Synergy projects")
    
    # Step 3: Update synergy_sessions with thread_ids
    print("\nStep 3: Updating Synergy sessions...")
    synergy_conn = sqlite3.connect(SYNERGY_DB)
    synergy_cursor = synergy_conn.cursor()
    
    updated_count = 0
    created_count = 0
    
    for synergy_id, threads in synergy_to_threads.items():
        # Check if session exists
        synergy_cursor.execute(
            "SELECT session_id, title, thread_ids FROM synergy_sessions WHERE session_id = ?",
            (synergy_id,)
        )
        session = synergy_cursor.fetchone()
        
        # Prepare thread_ids array (use thread_slug for consistency)
        thread_slugs = [t['slug'] for t in threads]
        thread_ids_json = json.dumps(thread_slugs)
        
        if session:
            # Update existing session
            old_thread_ids = json.loads(session[2]) if session[2] else []
            
            synergy_cursor.execute("""
                UPDATE synergy_sessions 
                SET thread_ids = ?, last_active = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (thread_ids_json, synergy_id))
            
            print(f"  ✓ Updated {session[1]}")
            print(f"    Old threads: {len(old_thread_ids)}, New threads: {len(thread_slugs)}")
            updated_count += 1
        else:
            # Create minimal session if it doesn't exist
            # (This handles orphaned thread links)
            first_thread = threads[0]
            synergy_cursor.execute("""
                INSERT INTO synergy_sessions 
                (session_id, title, description, thread_ids, kanban_column)
                VALUES (?, ?, ?, ?, ?)
            """, (
                synergy_id,
                f"Project from thread: {first_thread['name'][:50]}",
                f"Auto-created from {len(threads)} linked thread(s)",
                thread_ids_json,
                'in_progress'
            ))
            
            print(f"  ✓ Created new session: {synergy_id}")
            print(f"    Threads: {len(thread_slugs)}")
            created_count += 1
    
    synergy_conn.commit()
    synergy_conn.close()
    
    # Step 4: Verify sync
    print("\nStep 4: Verification...")
    synergy_conn = sqlite3.connect(SYNERGY_DB)
    cursor = synergy_conn.execute("""
        SELECT session_id, title, thread_ids 
        FROM synergy_sessions 
        WHERE thread_ids IS NOT NULL AND thread_ids != '[]' AND thread_ids != ''
    """)
    
    verified = cursor.fetchall()
    synergy_conn.close()
    
    print(f"\n{len(verified)} Synergy sessions have thread links:")
    for session_id, title, thread_ids in verified[:5]:  # Show first 5
        threads = json.loads(thread_ids) if thread_ids else []
        print(f"  • {title[:50]}: {len(threads)} threads")
    
    if len(verified) > 5:
        print(f"  ... and {len(verified) - 5} more")
    
    # Summary
    print("\n" + "=" * 80)
    print("SYNC COMPLETE")
    print("=" * 80)
    print(f"Sessions updated: {updated_count}")
    print(f"Sessions created: {created_count}")
    print(f"Total synced: {len(synergy_to_threads)}")
    print("\nResult: Synergy sessions now know their linked threads!")
    print("Status: Safe - threads table was never modified ✓")
    

if __name__ == "__main__":
    try:
        sync_synergy_thread_links()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
