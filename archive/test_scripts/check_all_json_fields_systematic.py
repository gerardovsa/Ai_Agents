"""
COMPREHENSIVE FIELD-BY-FIELD CHECK
Check EVERY JSON field vs HTML rendering for BOTH sessions
"""
import sqlite3
import json
import re

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get both sessions
sessions = [
    'sess_20251107_2211_email_thread_quote_generation_',
    'sess_20251107_2211_email_thread_quote_PROCESSING_'
]

print("=" * 120)
print("COMPREHENSIVE JSON FIELD vs HTML FIELD CHECK")
print("=" * 120)

for session_id in sessions:
    cursor.execute("""
        SELECT session_id, title, documents, tags, next_steps, links, assignees, 
               checklist, thread_ids, assigned_agents, platforms_involved, recent_activity
        FROM synergy_sessions 
        WHERE session_id = ?
    """, (session_id,))
    
    row = cursor.fetchone()
    if not row:
        print(f"\nSession not found: {session_id}")
        continue
    
    print(f"\n{'=' * 120}")
    print(f"SESSION: {session_id}")
    print(f"TITLE: {row[1]}")
    print(f"{'=' * 120}")
    
    # Parse all JSON fields
    documents = json.loads(row[2])
    tags = json.loads(row[3])
    next_steps = json.loads(row[4])
    links = json.loads(row[5])
    assignees = json.loads(row[6])
    checklist = json.loads(row[7])
    thread_ids = json.loads(row[8])
    assigned_agents = json.loads(row[9])
    platforms_involved = json.loads(row[10])
    recent_activity = json.loads(row[11])
    
    print("\n1. DOCUMENTS")
    print("-" * 120)
    print(f"   Count: {len(documents)}")
    if documents:
        first = documents[0]
        print(f"   Structure: {list(first.keys())}")
        print(f"   HTML looks for: doc.name, doc.type, doc.url, doc.size")
        print(f"   JSON has: {', '.join(first.keys())}")
        
        # Check for mismatches
        has_name = 'name' in first
        has_title = 'title' in first
        has_type = 'type' in first
        has_url = 'url' in first
        
        if not has_name and has_title:
            print(f"   MISMATCH: JSON has 'title' but HTML looks for 'name'")
        elif has_name:
            print(f"   OK: JSON has 'name' field")
        
        print(f"   Sample: {first}")
    
    print("\n2. TAGS")
    print("-" * 120)
    print(f"   Count: {len(tags)}")
    print(f"   HTML looks for: array of strings or {{label, color}}")
    if tags:
        first = tags[0]
        if isinstance(first, str):
            print(f"   JSON has: strings")
        else:
            print(f"   JSON has: objects with keys: {list(first.keys())}")
        print(f"   Sample: {first}")
    
    print("\n3. NEXT STEPS")
    print("-" * 120)
    print(f"   Count: {len(next_steps)}")
    print(f"   HTML looks for: step.description (objects) OR strings")
    if next_steps:
        first = next_steps[0]
        if isinstance(first, str):
            print(f"   JSON has: strings")
        else:
            print(f"   JSON has: objects with keys: {list(first.keys())}")
        print(f"   Sample: {str(first)[:100]}...")
    
    print("\n4. LINKS")
    print("-" * 120)
    print(f"   Count: {len(links)}")
    print(f"   HTML looks for: link.title, link.url")
    if links:
        first = links[0]
        print(f"   JSON has: {list(first.keys())}")
        print(f"   Sample: {first}")
    
    print("\n5. ASSIGNEES")
    print("-" * 120)
    print(f"   Count: {len(assignees)}")
    print(f"   HTML looks for: assignee.name, assignee.avatar")
    if assignees:
        first = assignees[0]
        if isinstance(first, str):
            print(f"   JSON has: strings")
        else:
            print(f"   JSON has: objects with keys: {list(first.keys())}")
        print(f"   Sample: {first}")
    
    print("\n6. CHECKLIST")
    print("-" * 120)
    print(f"   Count: {len(checklist)}")
    print(f"   HTML looks for: item.task, item.completed")
    if checklist:
        first = checklist[0]
        print(f"   JSON has: {list(first.keys())}")
        print(f"   Sample: {first}")
    
    print("\n7. THREAD IDS")
    print("-" * 120)
    print(f"   Count: {len(thread_ids)}")
    print(f"   HTML looks for: array of strings")
    if thread_ids:
        first = thread_ids[0]
        print(f"   JSON has: {type(first).__name__}")
        print(f"   Sample: {first}")
    
    print("\n8. ASSIGNED AGENTS")
    print("-" * 120)
    print(f"   Count: {len(assigned_agents)}")
    print(f"   HTML looks for: array of strings")
    if assigned_agents:
        first = assigned_agents[0]
        print(f"   JSON has: {type(first).__name__}")
        print(f"   Sample: {first}")
    
    print("\n9. PLATFORMS INVOLVED")
    print("-" * 120)
    print(f"   Count: {len(platforms_involved)}")
    print(f"   HTML looks for: array of strings")
    if platforms_involved:
        first = platforms_involved[0]
        print(f"   JSON has: {type(first).__name__}")
        print(f"   Sample: {first}")
    
    print("\n10. RECENT ACTIVITY")
    print("-" * 120)
    print(f"   Count: {len(recent_activity)}")
    print(f"   HTML looks for: activity.description, activity.timestamp")
    if recent_activity:
        first = recent_activity[0]
        print(f"   JSON has: {list(first.keys())}")
        print(f"   Sample: {first}")

conn.close()

print("\n" + "=" * 120)
print("NOW CHECKING HTML FILE FOR FIELD REFERENCES")
print("=" * 120)

# Read HTML file
with open('c:\\Users\\gpoli\\GIT\\AI_agents\\UI\\business-ai-platform-v2.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all doc. references
print("\nDOCUMENT FIELD REFERENCES IN HTML:")
doc_refs = re.findall(r'doc\.(\w+)', html)
unique_doc_refs = sorted(set(doc_refs))
for ref in unique_doc_refs:
    count = doc_refs.count(ref)
    print(f"   doc.{ref} - used {count} times")

# Find all tag references
print("\nTAG FIELD REFERENCES IN HTML:")
tag_refs = re.findall(r'tag\.(\w+)', html)
unique_tag_refs = sorted(set(tag_refs))
for ref in unique_tag_refs:
    count = tag_refs.count(ref)
    print(f"   tag.{ref} - used {count} times")

# Find all step references
print("\nSTEP FIELD REFERENCES IN HTML:")
step_refs = re.findall(r'step\.(\w+)', html)
unique_step_refs = sorted(set(step_refs))
for ref in unique_step_refs:
    count = step_refs.count(ref)
    print(f"   step.{ref} - used {count} times")

# Find all link references
print("\nLINK FIELD REFERENCES IN HTML:")
link_refs = re.findall(r'link\.(\w+)', html)
unique_link_refs = sorted(set(link_refs))
for ref in unique_link_refs:
    count = link_refs.count(ref)
    print(f"   link.{ref} - used {count} times")

# Find all assignee references
print("\nASSIGNEE FIELD REFERENCES IN HTML:")
assignee_refs = re.findall(r'assignee\.(\w+)', html)
unique_assignee_refs = sorted(set(assignee_refs))
for ref in unique_assignee_refs:
    count = assignee_refs.count(ref)
    print(f"   assignee.{ref} - used {count} times")

# Find all item references (checklist)
print("\nCHECKLIST ITEM REFERENCES IN HTML:")
item_refs = re.findall(r'item\.(\w+)', html)
unique_item_refs = sorted(set(item_refs))
for ref in unique_item_refs:
    count = item_refs.count(ref)
    print(f"   item.{ref} - used {count} times")

# Find all activity references
print("\nACTIVITY FIELD REFERENCES IN HTML:")
activity_refs = re.findall(r'activity\.(\w+)', html)
unique_activity_refs = sorted(set(activity_refs))
for ref in unique_activity_refs:
    count = activity_refs.count(ref)
    print(f"   activity.{ref} - used {count} times")

print("\n" + "=" * 120)
print("SUMMARY: FIELD MISMATCHES THAT WILL CAUSE DISPLAY ISSUES")
print("=" * 120)
print("\nBased on analysis above:")
print("1. DOCUMENTS: HTML uses 'doc.name' but generation session has 'title' - FIXED")
print("2. Check other fields for similar mismatches above")
