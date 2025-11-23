"""
Audit synergy_sessions database for data inconsistencies
"""
import sqlite3
import json
from pathlib import Path
from shared.database_utils import convert_sql_placeholders

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM synergy_sessions ORDER BY created_at DESC')
sessions = cursor.fetchall()

print(f"\n=== SYNERGY SESSIONS AUDIT ===")
print(f"Total sessions: {len(sessions)}\n")

issues_found = []

for session in sessions:
    session_id = session['session_id']
    title = session['title']
    
    print(f"\n{session_id}")
    print(f"  Title: {title}")
    
    # Check documents
    documents_raw = session['documents']
    try:
        documents = json.loads(documents_raw) if documents_raw else []
        print(f"  Documents: {len(documents)} items")
        for i, doc in enumerate(documents):
            if isinstance(doc, dict):
                has_name = 'name' in doc
                has_url = 'url' in doc
                has_type = 'type' in doc
                if not has_name or not has_url:
                    issues_found.append(f"{session_id} - Document {i}: Missing fields (name={has_name}, url={has_url}, type={has_type})")
                    print(f"    WARNING: Doc {i} missing fields: {doc}")
            else:
                issues_found.append(f"{session_id} - Document {i}: Not a dict: {doc}")
                print(f"    ERROR: Doc {i} is not a dict: {doc}")
    except Exception as e:
        issues_found.append(f"{session_id} - Documents parse error: {e}")
        print(f"  ERROR parsing documents: {e}")
    
    # Check links
    links_raw = session['links']
    try:
        links = json.loads(links_raw) if links_raw else []
        print(f"  Links: {len(links)} items")
        if links:
            for i, link in enumerate(links):
                print(f"    {i}: {link}")
    except Exception as e:
        issues_found.append(f"{session_id} - Links parse error: {e}")
        print(f"  ERROR parsing links: {e}")
    
    # Check notes
    notes_raw = session['notes']
    print(f"  Notes: {notes_raw[:100] if notes_raw else 'None'}...")
    
    # Check checklist
    checklist_raw = session['checklist']
    try:
        checklist = json.loads(checklist_raw) if checklist_raw else []
        print(f"  Checklist: {len(checklist)} items")
        if checklist:
            for i, item in enumerate(checklist):
                if isinstance(item, dict):
                    print(f"    {i}: {item.get('text', 'NO TEXT')} - completed={item.get('completed', False)}")
                else:
                    print(f"    {i}: {item}")
    except Exception as e:
        issues_found.append(f"{session_id} - Checklist parse error: {e}")
        print(f"  ERROR parsing checklist: {e}")
    
    # Check next_steps
    next_steps_raw = session['next_steps']
    try:
        next_steps = json.loads(next_steps_raw) if next_steps_raw else []
        print(f"  Next Steps: {len(next_steps)} items")
    except Exception as e:
        issues_found.append(f"{session_id} - Next steps parse error: {e}")
        print(f"  ERROR parsing next_steps: {e}")
    
    # Check thread_ids
    thread_ids_raw = session['thread_ids']
    try:
        thread_ids = json.loads(thread_ids_raw) if thread_ids_raw else []
        print(f"  Thread IDs: {len(thread_ids)} items")
        if thread_ids:
            print(f"    {thread_ids}")
    except Exception as e:
        issues_found.append(f"{session_id} - Thread IDs parse error: {e}")
        print(f"  ERROR parsing thread_ids: {e}")
    
    # Check recent_activity
    activity_raw = session['recent_activity']
    try:
        activity = json.loads(activity_raw) if activity_raw else []
        print(f"  Activity Log: {len(activity)} items")
        if activity and len(activity) > 0:
            print(f"    Latest: {activity[0] if isinstance(activity[0], str) else activity[0].get('message', activity[0])}")
    except Exception as e:
        issues_found.append(f"{session_id} - Activity parse error: {e}")
        print(f"  ERROR parsing recent_activity: {e}")

conn.close()

print(f"\n\n=== ISSUES SUMMARY ===")
if issues_found:
    print(f"Found {len(issues_found)} issues:\n")
    for issue in issues_found:
        print(f"  - {issue}")
else:
    print("No issues found!")

# Check specific session mentioned by user
print(f"\n\n=== SPECIFIC SESSION CHECK ===")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

session_id = 'sess_20251101_1410_michael_e-commerce_store_setup'
sql, params = convert_sql_placeholders('SELECT * FROM synergy_sessions WHERE session_id = ?', (session_id,))

cursor.execute(sql, params)
session = cursor.fetchone()

if session:
    print(f"\nSession: {session_id}")
    print(f"Title: {session['title']}")
    
    links = json.loads(session['links']) if session['links'] else []
    print(f"\nLinks ({len(links)}):")
    for link in links:
        print(f"  {link}")
    
    notes = session['notes']
    print(f"\nNotes:")
    print(f"  {notes}")
else:
    print(f"Session {session_id} not found")

conn.close()
