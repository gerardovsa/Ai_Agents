"""Check actual data structure in synergy_sessions"""
import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'synergy_sessions.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get 3 sessions to examine
cursor.execute('''
    SELECT session_id, title, documents, links, notes, checklist, thread_ids, recent_activity
    FROM synergy_sessions
    ORDER BY created_at DESC
    LIMIT 3
''')

sessions = cursor.fetchall()

for session in sessions:
    print(f"\n{'='*70}")
    print(f"Session: {session['session_id']}")
    print(f"Title: {session['title']}")
    
    # Documents
    docs_raw = session['documents']
    print(f"\nDocuments (raw): {docs_raw[:200] if docs_raw else 'None'}...")
    if docs_raw:
        try:
            docs = json.loads(docs_raw)
            print(f"Documents (parsed): {len(docs)} items")
            if docs and len(docs) > 0:
                print(f"  First doc: {docs[0]}")
        except Exception as e:
            print(f"  ERROR parsing: {e}")
    
    # Links
    links_raw = session['links']
    print(f"\nLinks (raw): {links_raw[:150] if links_raw else 'None'}...")
    if links_raw:
        try:
            links = json.loads(links_raw)
            print(f"Links (parsed): {len(links)} items")
            if links:
                for i, link in enumerate(links[:2]):
                    print(f"  {i}: {link}")
        except Exception as e:
            print(f"  ERROR parsing: {e}")
    
    # Notes
    notes_raw = session['notes']
    print(f"\nNotes (raw): {notes_raw[:150] if notes_raw else 'None'}...")
    
    # Checklist
    checklist_raw = session['checklist']
    print(f"\nChecklist (raw): {checklist_raw[:150] if checklist_raw else 'None'}...")
    if checklist_raw:
        try:
            checklist = json.loads(checklist_raw)
            print(f"Checklist (parsed): {len(checklist)} items")
            if checklist and len(checklist) > 0:
                print(f"  First item: {checklist[0]}")
        except Exception as e:
            print(f"  ERROR parsing: {e}")
    
    # Thread IDs
    threads_raw = session['thread_ids']
    print(f"\nThread IDs (raw): {threads_raw[:150] if threads_raw else 'None'}...")
    if threads_raw:
        try:
            threads = json.loads(threads_raw)
            print(f"Thread IDs (parsed): {len(threads)} items")
            if threads:
                print(f"  {threads}")
        except Exception as e:
            print(f"  ERROR parsing: {e}")
    
    # Activity
    activity_raw = session['recent_activity']
    print(f"\nActivity (raw): {activity_raw[:150] if activity_raw else 'None'}...")
    if activity_raw:
        try:
            activity = json.loads(activity_raw)
            print(f"Activity (parsed): {len(activity)} items")
            if activity and len(activity) > 0:
                print(f"  Latest: {activity[0]}")
        except Exception as e:
            print(f"  ERROR parsing: {e}")

conn.close()

# Check the specific session user mentioned
print(f"\n\n{'='*70}")
print("SPECIFIC SESSION CHECK:")
print("sess_20251101_1410_michael_e-commerce_store_setup")
print(f"{'='*70}")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('''
    SELECT links, notes
    FROM synergy_sessions
    WHERE session_id = 'sess_20251101_1410_michael_e-commerce_store_setup'
''')

row = cursor.fetchone()
if row:
    print(f"\nLinks: {row['links']}")
    print(f"\nNotes: {row['notes']}")
else:
    print("\nSession not found")

conn.close()
