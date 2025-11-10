"""
Check the specific session the user is looking at:
sess_20251107_2211_email_thread_quote_generation_
"""

import requests
import json

print("="*100)
print("CHECKING SESSION: sess_20251107_2211_email_thread_quote_generation_")
print("="*100)

# Get API data
r = requests.get('http://localhost:5001/api/synergy/list')
sessions = r.json()['sessions']

# Find the specific session
target_session = None
for s in sessions:
    if 'quote_generation' in s['session_id']:
        target_session = s
        break

if not target_session:
    print("❌ Session 'quote_generation' not found!")
    print("\nAvailable sessions:")
    for s in sessions:
        print(f"  - {s['session_id']}")
    exit(1)

print(f"\n✅ Found session: {target_session['session_id']}")
print(f"Title: {target_session['title']}")

# Check all JSON fields
print("\n" + "="*100)
print("ALL JSON FIELDS IN THIS SESSION")
print("="*100)

json_fields = {
    'documents': 'Documents',
    'tags': 'Tags',
    'next_steps': 'Next Steps',
    'links': 'Links',
    'assignees': 'Assignees',
    'checklist': 'Checklist',
    'thread_ids': 'Linked Threads',
    'assigned_agents': 'Assigned Agents',
    'platforms_involved': 'Platforms',
    'recent_activity': 'Recent Activity'
}

for field, label in json_fields.items():
    value = target_session.get(field, [])
    print(f"\n{label} ({field}):")
    print(f"  Type: {type(value)}")
    print(f"  Length: {len(value) if isinstance(value, (list, dict)) else 'N/A'}")
    
    if isinstance(value, list) and len(value) > 0:
        print(f"  First item type: {type(value[0])}")
        if isinstance(value[0], dict):
            print(f"  First item keys: {list(value[0].keys())}")
            print(f"  First item: {json.dumps(value[0], indent=4)[:200]}...")
        elif isinstance(value[0], str):
            print(f"  First item: {value[0][:100]}...")

print("\n" + "="*100)
print("DOCUMENTS DETAILED ANALYSIS")
print("="*100)

docs = target_session.get('documents', [])
print(f"\nTotal documents: {len(docs)}")
print(f"Type: {type(docs)}")

if isinstance(docs, list):
    for i, doc in enumerate(docs[:5], 1):  # Show first 5
        print(f"\nDocument {i}:")
        print(f"  Type: {type(doc)}")
        if isinstance(doc, dict):
            print(f"  Keys: {list(doc.keys())}")
            print(f"  name: {doc.get('name', 'MISSING')}")
            print(f"  type: {doc.get('type', 'MISSING')}")
            print(f"  url: {'Present' if doc.get('url') else 'MISSING'}")
        else:
            print(f"  Value: {doc}")
            
print("\n" + "="*100)
print("WHAT YOU SHOULD SEE IN UI")
print("="*100)

print(f"""
Collapsed Card:
  Title: {target_session['title'][:60]}
  Tags: {', '.join(target_session.get('tags', [])[:3])}
  
Expanded Card / Popup:
  📄 Documents ({len(docs)}):
""")

if len(docs) > 0:
    for i, doc in enumerate(docs[:10], 1):
        if isinstance(doc, dict):
            name = doc.get('name', 'N/A')
            print(f"    {i}. {name}")
else:
    print("    (empty)")

print(f"""
  ⏭️ Next Steps ({len(target_session.get('next_steps', []))}):
""")

steps = target_session.get('next_steps', [])
if len(steps) > 0:
    for i, step in enumerate(steps[:5], 1):
        if isinstance(step, str):
            print(f"    □ {step[:70]}...")
        elif isinstance(step, dict):
            print(f"    □ {step.get('description', 'N/A')[:70]}...")
else:
    print("    (empty)")

print("\n" + "="*100)
print("BROWSER DEVTOOLS CHECK")
print("="*100)

print("""
Open DevTools (F12) and run:

1. Check sessions loaded:
   synergyBoard.sessions.find(s => s.session_id.includes('generation'))

2. Check documents:
   synergyBoard.sessions.find(s => s.session_id.includes('generation')).documents

3. Check if it's an array:
   Array.isArray(synergyBoard.sessions.find(s => s.session_id.includes('generation')).documents)

4. Check first document:
   synergyBoard.sessions.find(s => s.session_id.includes('generation')).documents[0]

5. Inspect the HTML element:
   Right-click on a document icon → Inspect
   Look for: <span class="doc-name">...</span>
   Check if text is present but hidden by CSS
""")
