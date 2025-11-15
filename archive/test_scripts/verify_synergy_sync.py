"""
Verify Synergy Bidirectional Sync Integrity

This script checks that Synergy card <-> thread linking is properly synchronized:
1. threads.synergy_card_id (in sessions.db)
2. synergy_sessions.thread_ids (JSON array in synergy_sessions.db)

Both sides should match for proper bidirectional sync.

Usage:
    python verify_synergy_sync.py
"""

import sqlite3
import json
from pathlib import Path

def verify_synergy_sync():
    """Verify bidirectional sync between threads and synergy cards"""
    
    root_dir = Path(__file__).parent
    sessions_db = root_dir / 'data' / 'sessions.db'
    synergy_db = root_dir / 'data' / 'synergy_sessions.db'
    
    print(f"{'='*70}")
    print(f"SYNERGY BIDIRECTIONAL SYNC VERIFICATION")
    print(f"{'='*70}\n")
    
    print(f"Sessions DB: {sessions_db}")
    print(f"Synergy DB:  {synergy_db}\n")
    
    if not sessions_db.exists():
        print(f"ERROR: Sessions database not found")
        return
    
    if not synergy_db.exists():
        print(f"ERROR: Synergy database not found")
        return
    
    # Connect to both databases
    sessions_conn = sqlite3.connect(str(sessions_db))
    synergy_conn = sqlite3.connect(str(synergy_db))
    
    sessions_cursor = sessions_conn.cursor()
    synergy_cursor = synergy_conn.cursor()
    
    # Get all threads with synergy_card_id
    sessions_cursor.execute("""
        SELECT thread_slug, name, synergy_card_id
        FROM threads
        WHERE synergy_card_id IS NOT NULL AND synergy_card_id != ''
    """)
    threads_with_synergy = sessions_cursor.fetchall()
    
    print(f"{'='*70}")
    print(f"THREADS → SYNERGY CARDS")
    print(f"{'='*70}\n")
    print(f"Found {len(threads_with_synergy)} threads linked to Synergy cards\n")
    
    # Build mapping: synergy_card_id -> [thread_ids]
    thread_to_synergy = {}
    synergy_from_threads = {}
    
    for thread_id, thread_name, synergy_id in threads_with_synergy:
        print(f"Thread: {thread_id}")
        print(f"  Name: {thread_name}")
        print(f"  Synergy Card: {synergy_id}")
        
        thread_to_synergy[thread_id] = synergy_id
        
        if synergy_id not in synergy_from_threads:
            synergy_from_threads[synergy_id] = []
        synergy_from_threads[synergy_id].append(thread_id)
        
        print()
    
    # Get all synergy sessions with thread_ids
    synergy_cursor.execute("""
        SELECT session_id, title, thread_ids
        FROM synergy_sessions
        WHERE thread_ids IS NOT NULL AND thread_ids != ''
    """)
    synergy_sessions = synergy_cursor.fetchall()
    
    print(f"{'='*70}")
    print(f"SYNERGY CARDS → THREADS")
    print(f"{'='*70}\n")
    print(f"Found {len(synergy_sessions)} Synergy cards with linked threads\n")
    
    # Build mapping: synergy_card_id -> [thread_ids]
    synergy_to_threads = {}
    
    for session_id, title, thread_ids_json in synergy_sessions:
        try:
            thread_ids = json.loads(thread_ids_json)
        except json.JSONDecodeError:
            thread_ids = []
        
        print(f"Synergy Card: {session_id}")
        print(f"  Title: {title}")
        print(f"  Linked Threads: {len(thread_ids)}")
        
        synergy_to_threads[session_id] = thread_ids
        
        for thread_id in thread_ids:
            print(f"    - {thread_id}")
        
        print()
    
    # Verify bidirectional sync
    print(f"{'='*70}")
    print(f"SYNC VERIFICATION")
    print(f"{'='*70}\n")
    
    issues_found = 0
    
    # Check 1: Every thread with synergy_card_id should be in that synergy's thread_ids
    print("CHECK 1: Threads → Synergy integrity")
    for thread_id, synergy_id in thread_to_synergy.items():
        if synergy_id not in synergy_to_threads:
            print(f"  ❌ Thread {thread_id} points to Synergy {synergy_id}, but Synergy card not found")
            issues_found += 1
        elif thread_id not in synergy_to_threads[synergy_id]:
            print(f"  ❌ Thread {thread_id} points to Synergy {synergy_id}, but not in Synergy's thread_ids array")
            issues_found += 1
        else:
            print(f"  ✅ Thread {thread_id} ↔ Synergy {synergy_id} (bidirectional sync OK)")
    
    if not thread_to_synergy:
        print("  (No threads with synergy_card_id)")
    
    print()
    
    # Check 2: Every thread_id in synergy should have synergy_card_id pointing back
    print("CHECK 2: Synergy → Threads integrity")
    for synergy_id, thread_ids in synergy_to_threads.items():
        for thread_id in thread_ids:
            if thread_id not in thread_to_synergy:
                print(f"  ❌ Synergy {synergy_id} lists thread {thread_id}, but thread has no synergy_card_id")
                issues_found += 1
            elif thread_to_synergy[thread_id] != synergy_id:
                print(f"  ❌ Synergy {synergy_id} lists thread {thread_id}, but thread points to different Synergy: {thread_to_synergy[thread_id]}")
                issues_found += 1
            else:
                print(f"  ✅ Synergy {synergy_id} ↔ Thread {thread_id} (bidirectional sync OK)")
    
    if not synergy_to_threads:
        print("  (No Synergy cards with thread_ids)")
    
    print()
    
    # Summary
    print(f"{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Threads with Synergy links: {len(threads_with_synergy)}")
    print(f"Synergy cards with thread links: {len(synergy_sessions)}")
    print(f"Sync issues found: {issues_found}")
    
    if issues_found == 0:
        print(f"\n✅ VERIFICATION PASSED - All bidirectional links are synchronized")
    else:
        print(f"\n❌ VERIFICATION FAILED - {issues_found} sync issues found")
        print(f"\nRecommendation: Run repair script or manually fix inconsistencies")
    
    print(f"{'='*70}\n")
    
    sessions_conn.close()
    synergy_conn.close()
    
    return issues_found

if __name__ == '__main__':
    verify_synergy_sync()
