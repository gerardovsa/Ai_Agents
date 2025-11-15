"""
Fix double-encoding issue in synergy_sessions database
Documents, links, notes, and other JSON fields are stored as double-encoded strings
"""
import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all sessions
cursor.execute('SELECT * FROM synergy_sessions')
sessions = cursor.fetchall()

print(f"\n=== FIXING DOUBLE-ENCODING ===")
print(f"Total sessions: {len(sessions)}\n")

fixed_count = 0
error_count = 0

for session in sessions:
    session_id = session['session_id']
    title = session['title']
    
    print(f"\n{session_id}")
    print(f"  Title: {title}")
    
    updates = {}
    
    # Fix documents field
    documents_raw = session['documents']
    if documents_raw:
        try:
            # Try to parse as JSON
            documents = json.loads(documents_raw)
            
            # Check if it's a list of characters (double-encoded)
            if isinstance(documents, list) and len(documents) > 0 and all(isinstance(x, str) and len(x) <= 1 for x in documents[:10]):
                # It's double-encoded! Rejoin and parse again
                documents_str = ''.join(documents)
                documents = json.loads(documents_str)
                updates['documents'] = json.dumps(documents)
                print(f"  Fixed documents: {len(documents)} items")
            elif isinstance(documents, list) and len(documents) > 0 and isinstance(documents[0], dict):
                print(f"  Documents OK: {len(documents)} items")
            else:
                print(f"  Documents: Unknown format")
        except Exception as e:
            print(f"  ERROR parsing documents: {e}")
            error_count += 1
    
    # Fix links field
    links_raw = session['links']
    if links_raw:
        try:
            links = json.loads(links_raw)
            
            if isinstance(links, list) and len(links) > 0 and all(isinstance(x, str) and len(x) <= 1 for x in links[:10]):
                links_str = ''.join(links)
                links = json.loads(links_str)
                updates['links'] = json.dumps(links)
                print(f"  Fixed links: {len(links)} items")
            elif isinstance(links, list):
                print(f"  Links OK: {len(links)} items")
        except Exception as e:
            print(f"  ERROR parsing links: {e}")
            error_count += 1
    
    # Fix checklist field
    checklist_raw = session['checklist']
    if checklist_raw:
        try:
            checklist = json.loads(checklist_raw)
            
            if isinstance(checklist, list) and len(checklist) > 0 and all(isinstance(x, str) and len(x) <= 1 for x in checklist[:10]):
                checklist_str = ''.join(checklist)
                checklist = json.loads(checklist_str)
                updates['checklist'] = json.dumps(checklist)
                print(f"  Fixed checklist: {len(checklist)} items")
            elif isinstance(checklist, list):
                print(f"  Checklist OK: {len(checklist)} items")
        except Exception as e:
            print(f"  ERROR parsing checklist: {e}")
            error_count += 1
    
    # Fix next_steps field
    next_steps_raw = session['next_steps']
    if next_steps_raw:
        try:
            next_steps = json.loads(next_steps_raw)
            
            if isinstance(next_steps, list) and len(next_steps) > 0 and all(isinstance(x, str) and len(x) <= 1 for x in next_steps[:10]):
                next_steps_str = ''.join(next_steps)
                next_steps = json.loads(next_steps_str)
                updates['next_steps'] = json.dumps(next_steps)
                print(f"  Fixed next_steps: {len(next_steps)} items")
            elif isinstance(next_steps, list):
                print(f"  Next steps OK: {len(next_steps)} items")
        except Exception as e:
            print(f"  ERROR parsing next_steps: {e}")
            error_count += 1
    
    # Fix other JSON arrays
    for field in ['platforms_involved', 'thread_ids', 'assigned_agents', 'tags', 'assignees', 'recent_activity']:
        field_raw = session[field]
        if field_raw:
            try:
                field_data = json.loads(field_raw)
                
                if isinstance(field_data, list) and len(field_data) > 0 and all(isinstance(x, str) and len(x) <= 1 for x in field_data[:10]):
                    field_str = ''.join(field_data)
                    field_data = json.loads(field_str)
                    updates[field] = json.dumps(field_data)
                    print(f"  Fixed {field}: {len(field_data)} items")
            except Exception:
                pass
    
    # Apply updates
    if updates:
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        values = list(updates.values()) + [session_id]
        
        update_sql = f"UPDATE synergy_sessions SET {set_clause} WHERE session_id = ?"
        cursor.execute(update_sql, values)
        fixed_count += 1
        print(f"  Updated {len(updates)} fields")

conn.commit()
conn.close()

print(f"\n\n=== SUMMARY ===")
print(f"Fixed: {fixed_count} sessions")
print(f"Errors: {error_count}")
print(f"\nDone!")
