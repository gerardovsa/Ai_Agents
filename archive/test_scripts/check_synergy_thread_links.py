"""Check how Synergy-Thread linking is working"""
import sqlite3
import json
from pathlib import Path

root = Path(__file__).parent

# Connect to both databases
synergy_conn = sqlite3.connect(root / 'data' / 'synergy_sessions.db')
synergy_conn.row_factory = sqlite3.Row
sessions_conn = sqlite3.connect(root / 'data' / 'sessions.db')
sessions_conn.row_factory = sqlite3.Row

print("="*100)
print("SYNERGY-THREAD LINKING ANALYSIS")
print("="*100)

# 1. Check Synergy sessions with thread_ids
print("\n1. SYNERGY SESSIONS WITH THREAD_IDS:")
print("-"*100)
synergy_cursor = synergy_conn.cursor()
synergy_cursor.execute("""
    SELECT session_id, title, thread_ids, assigned_agents
    FROM synergy_sessions
    WHERE thread_ids IS NOT NULL 
      AND thread_ids != 'null' 
      AND thread_ids != '[]'
      AND thread_ids != ''
""")

synergy_with_threads = synergy_cursor.fetchall()
print(f"Found {len(synergy_with_threads)} Synergy sessions with threads linked\n")

for row in synergy_with_threads:
    print(f"Session ID: {row['session_id']}")
    print(f"Title: {row['title']}")
    print(f"thread_ids: {row['thread_ids']}")
    print(f"assigned_agents: {row['assigned_agents']}")
    
    # Parse thread_ids
    try:
        thread_ids = json.loads(row['thread_ids']) if row['thread_ids'] else []
        print(f"Parsed thread_ids: {thread_ids} ({len(thread_ids)} threads)")
    except:
        print(f"ERROR: Could not parse thread_ids as JSON")
    print("-"*100)

# 2. Check threads with synergy_card_id
print("\n2. THREADS WITH SYNERGY_CARD_ID:")
print("-"*100)
threads_cursor = sessions_conn.cursor()
threads_cursor.execute("""
    SELECT id, thread_slug, name, synergy_card_id, location
    FROM threads
    WHERE synergy_card_id IS NOT NULL 
      AND synergy_card_id != 'null'
      AND synergy_card_id != ''
""")

threads_with_synergy = threads_cursor.fetchall()
print(f"Found {len(threads_with_synergy)} threads linked to Synergy\n")

for row in threads_with_synergy:
    print(f"Thread ID: {row['id']}")
    print(f"Thread Slug: {row['thread_slug']}")
    print(f"Name: {row['name']}")
    print(f"synergy_card_id: {row['synergy_card_id']}")
    print(f"Agent (location): {row['location']}")
    print("-"*100)

# 3. BIDIRECTIONAL VERIFICATION
print("\n3. BIDIRECTIONAL LINK VERIFICATION:")
print("-"*100)

# For each Synergy session with threads, verify reverse link
for synergy_row in synergy_with_threads:
    session_id = synergy_row['session_id']
    try:
        thread_ids = json.loads(synergy_row['thread_ids']) if synergy_row['thread_ids'] else []
    except:
        thread_ids = []
    
    print(f"\nSynergy Session: {session_id}")
    print(f"Claims to have {len(thread_ids)} threads: {thread_ids}")
    
    for thread_id in thread_ids:
        # Check if thread exists and points back
        threads_cursor.execute("""
            SELECT id, thread_slug, name, synergy_card_id, location
            FROM threads
            WHERE thread_slug = ? OR id = ?
        """, (thread_id, thread_id))
        
        thread = threads_cursor.fetchone()
        if thread:
            matches = thread['synergy_card_id'] == session_id
            status = "BIDIRECTIONAL" if matches else "ONE-WAY (broken)"
            print(f"  Thread {thread_id}: EXISTS - {status}")
            print(f"    Name: {thread['name']}")
            print(f"    Points to: {thread['synergy_card_id']}")
            print(f"    Agent: {thread['location']}")
        else:
            print(f"  Thread {thread_id}: NOT FOUND (broken link)")

# 4. ORPHANED THREADS (point to Synergy but not in Synergy's list)
print("\n4. ORPHANED THREADS (one-way links):")
print("-"*100)

threads_cursor.execute("""
    SELECT id, thread_slug, name, synergy_card_id, location
    FROM threads
    WHERE synergy_card_id IS NOT NULL 
      AND synergy_card_id != ''
      AND synergy_card_id != 'null'
""")

all_linked_threads = threads_cursor.fetchall()

for thread in all_linked_threads:
    synergy_id = thread['synergy_card_id']
    thread_slug = thread['thread_slug']
    
    # Check if Synergy session has this thread in its list
    synergy_cursor.execute("""
        SELECT thread_ids FROM synergy_sessions WHERE session_id = ?
    """, (synergy_id,))
    
    synergy = synergy_cursor.fetchone()
    if synergy:
        try:
            thread_ids = json.loads(synergy['thread_ids']) if synergy['thread_ids'] else []
        except:
            thread_ids = []
        
        if thread_slug not in thread_ids and str(thread['id']) not in thread_ids:
            print(f"\nORPHANED: Thread {thread_slug} ({thread['name']})")
            print(f"  Points to: {synergy_id}")
            print(f"  But Synergy has: {thread_ids}")
            print(f"  STATUS: ONE-WAY LINK (needs repair)")
    else:
        print(f"\nBROKEN: Thread {thread_slug} ({thread['name']})")
        print(f"  Points to non-existent Synergy: {synergy_id}")

# 5. SUMMARY
print("\n" + "="*100)
print("SUMMARY:")
print("="*100)
print(f"Total Synergy sessions with threads: {len(synergy_with_threads)}")
print(f"Total threads with synergy_card_id: {len(threads_with_synergy)}")

# Count bidirectional links
bidirectional_count = 0
for synergy_row in synergy_with_threads:
    try:
        thread_ids = json.loads(synergy_row['thread_ids']) if synergy_row['thread_ids'] else []
    except:
        thread_ids = []
    
    for thread_id in thread_ids:
        threads_cursor.execute("""
            SELECT synergy_card_id FROM threads 
            WHERE (thread_slug = ? OR id = ?) AND synergy_card_id = ?
        """, (thread_id, thread_id, synergy_row['session_id']))
        if threads_cursor.fetchone():
            bidirectional_count += 1

print(f"Verified bidirectional links: {bidirectional_count}")
print("="*100)

synergy_conn.close()
sessions_conn.close()
