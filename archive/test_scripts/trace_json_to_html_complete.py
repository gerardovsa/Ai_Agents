"""
Trace each JSON field from database → backend → frontend → HTML
Complete end-to-end analysis of why data isn't displaying
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
import json
import requests
from pathlib import Path

print("="*100)
print("COMPLETE JSON FIELD TRACING - DATABASE TO HTML")
print("="*100)

# Step 1: Get data from database
root = Path('C:/Users/gpoli/GIT/AI_agents')
db = root / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

sql, params = convert_sql_placeholders("""
    SELECT * FROM synergy_sessions 
    WHERE session_id LIKE ?
""", ('%email_thread_quote%',))


cursor.execute(sql, params)

db_row = cursor.fetchone()
conn.close()

if not db_row:
    print("❌ Session not found!")
    exit(1)

print(f"\nTarget Session: {db_row['session_id']}")
print(f"Title: {db_row['title']}\n")

# All 10 JSON fields
json_fields = [
    'platforms_involved',
    'tags', 
    'documents',
    'links',
    'next_steps',
    'assignees',
    'recent_activity',
    'checklist',
    'thread_ids',
    'assigned_agents'
]

# Step 2: Analyze each field
for field_name in json_fields:
    print("="*100)
    print(f"FIELD: {field_name}")
    print("="*100)
    
    raw_value = db_row[field_name]
    
    # STEP 1: DATABASE
    print("\n[STEP 1: DATABASE]")
    print(f"  Type: {type(raw_value)}")
    print(f"  Is None: {raw_value is None}")
    print(f"  Is Empty: {raw_value == '' if raw_value else 'N/A'}")
    
    if raw_value:
        print(f"  Length: {len(raw_value)} chars")
        print(f"  First 150 chars: {raw_value[:150]}")
        
        # Try to parse
        try:
            parsed = json.loads(raw_value)
            print(f"  ✅ Parsed type: {type(parsed)}")
            if isinstance(parsed, list):
                print(f"  ✅ Array length: {len(parsed)}")
                if len(parsed) > 0:
                    print(f"  ✅ First item type: {type(parsed[0])}")
                    if isinstance(parsed[0], dict):
                        print(f"  ✅ First item keys: {list(parsed[0].keys())}")
                    elif isinstance(parsed[0], str):
                        print(f"  ✅ First item: {parsed[0][:80]}")
            elif isinstance(parsed, dict):
                print(f"  ⚠️  It's a dict, not array! Keys: {list(parsed.keys())}")
            elif isinstance(parsed, str):
                print(f"  ❌ DOUBLE ENCODED! Still a string after parsing!")
        except Exception as e:
            print(f"  ❌ Parse error: {e}")
    else:
        print(f"  Value: NULL or empty")

print("\n" + "="*100)
print("[STEP 2: API RESPONSE]")
print("="*100)

# Step 3: Check API
try:
    response = requests.get('http://localhost:5001/api/synergy/list')
    if response.ok:
        data = response.json()
        sessions = data.get('sessions', [])
        
        # Find our session
        api_session = None
        for s in sessions:
            if 'email_thread_quote' in s.get('session_id', ''):
                api_session = s
                break
        
        if api_session:
            print(f"\n✅ Found session in API response")
            
            for field_name in json_fields:
                print(f"\n{'='*100}")
                print(f"API FIELD: {field_name}")
                print(f"{'='*100}")
                
                api_value = api_session.get(field_name)
                
                print(f"  Type in API: {type(api_value)}")
                print(f"  Is None: {api_value is None}")
                
                if isinstance(api_value, list):
                    print(f"  ✅ IS ARRAY! Length: {len(api_value)}")
                    if len(api_value) > 0:
                        print(f"  First item type: {type(api_value[0])}")
                        if isinstance(api_value[0], dict):
                            print(f"  First item: {api_value[0]}")
                        elif isinstance(api_value[0], str):
                            print(f"  First item: {api_value[0][:80]}")
                elif isinstance(api_value, str):
                    print(f"  ❌ STILL STRING IN API!")
                    print(f"  Value: {api_value[:150]}")
                elif isinstance(api_value, dict):
                    print(f"  ⚠️  IS DICT (not array)")
                    print(f"  Keys: {list(api_value.keys())}")
                else:
                    print(f"  Type: {type(api_value)}")
        else:
            print("❌ Session not found in API")
    else:
        print(f"❌ API error: {response.status_code}")
except Exception as e:
    print(f"❌ API request failed: {e}")

print("\n" + "="*100)
print("[STEP 3: HTML RENDERING POINTS]")
print("="*100)

# Map each field to where it's used in HTML
html_usage = {
    'platforms_involved': [
        'Line ~23135: parseJsonField(session.platforms_involved, [])',
        'NOT DISPLAYED in current HTML - no section for platforms'
    ],
    'tags': [
        'Line ~23050: parseJsonField(session.tags, [])',
        'Line ~23056-23062: Collapsed view - shows first 3 tags',
        'HTML: <span class="card-tag">${tag}</span>'
    ],
    'documents': [
        'Line ~23135: parseJsonField(session.documents, [])',
        'Line ~23141-23153: Expanded view document section',
        'HTML: <div class="document-item" onclick="...">',
        '      <span class="doc-name">${doc.name}</span>',
        '      <span class="doc-size">${doc.size || "N/A"}</span>'
    ],
    'links': [
        'Line ~23156: parseJsonField(session.links, [])',
        'Line ~23162-23174: Expanded view links section',
        'HTML: <div class="link-item">',
        '      <a href="${link.url}">${link.title}</a>'
    ],
    'next_steps': [
        'Line ~23050: parseJsonField(session.next_steps, [])',
        'Line ~23177-23195: Expanded view next steps section',
        'HTML: <div class="step-item ${completed ? \'completed\' : \'\'}">',
        '      <input type="checkbox" ${completed ? \'checked\' : \'\'}/>',
        '      <span>${step.description}</span>'
    ],
    'assignees': [
        'Line ~23135: parseJsonField(session.assignees, [])',
        'Line ~23247-23252: Expanded view assignees section',
        'HTML: <div class="card-assignees">',
        '      <i class="fas fa-users"></i> ${assignees.join(\', \')}'
    ],
    'recent_activity': [
        'Line ~23136: parseJsonField(session.recent_activity, [])',
        'NOT DISPLAYED in current HTML - no visible section'
    ],
    'checklist': [
        'Line ~23136: parseJsonField(session.checklist, [])',
        'Line ~23198-23215: Expanded view checklist section',
        'HTML: <div class="checklist-item ${completed ? \'completed\' : \'\'}">',
        '      <input type="checkbox" ${completed ? \'checked\' : \'\'}/>',
        '      <span>${item.item}</span>'
    ],
    'thread_ids': [
        'Line ~22995: parseJsonField(session.thread_ids, [])',
        'Line ~23002: renderLinkedThreads(threadIds) - async call',
        'Line ~23295-23301: Expanded view linked threads section',
        'HTML: <div class="linked-thread" onclick="openThread(...)">',
        '      <div class="thread-name">${thread.name}</div>'
    ],
    'assigned_agents': [
        'Line ~23305-23315: Expanded view assigned agents section',
        'HTML: <div class="agent-item">',
        '      <span class="agent-name">${agent}</span>'
    ]
}

for field_name, usage in html_usage.items():
    print(f"\n{'='*80}")
    print(f"{field_name}")
    print(f"{'='*80}")
    for line in usage:
        print(f"  {line}")

print("\n" + "="*100)
print("[STEP 4: CHECK JAVASCRIPT CONSOLE]")
print("="*100)
print("""
CRITICAL: Open browser DevTools (F12) and check:

1. Console tab - look for:
   - [OK] Sessions loaded from API: X
   - [SYNERGY] renderCard called
   - Any errors or warnings

2. Network tab - look for:
   - /api/synergy/list request
   - Check response payload
   - Verify JSON fields are arrays

3. Sources tab - set breakpoints:
   - Line ~22650: loadSessions()
   - Line ~22956: renderCard()
   - Line ~23135: renderCardExpanded()
   - Check session object structure

4. Elements tab - inspect:
   - Find .kanban-card element
   - Check if .card-expanded-view exists
   - Look for .document-list
   - Verify data-session-id attribute
""")

print("\n" + "="*100)
print("QUICK DIAGNOSTIC CHECKS")
print("="*100)

if api_session:
    issues = []
    
    # Check if documents is array
    docs = api_session.get('documents')
    if not isinstance(docs, list):
        issues.append(f"❌ documents is {type(docs)}, not list")
    elif len(docs) == 0:
        issues.append("⚠️  documents array is empty")
    elif not isinstance(docs[0], dict):
        issues.append(f"❌ documents[0] is {type(docs[0])}, not dict")
    elif 'name' not in docs[0]:
        issues.append("❌ documents[0] has no 'name' key")
    else:
        issues.append("✅ documents structure looks correct")
    
    # Check tags
    tags = api_session.get('tags')
    if not isinstance(tags, list):
        issues.append(f"❌ tags is {type(tags)}, not list")
    else:
        issues.append(f"✅ tags is array with {len(tags)} items")
    
    # Check next_steps
    steps = api_session.get('next_steps')
    if not isinstance(steps, list):
        issues.append(f"❌ next_steps is {type(steps)}, not list")
    else:
        issues.append(f"✅ next_steps is array with {len(steps)} items")
    
    print("\nIssues found:")
    for issue in issues:
        print(f"  {issue}")

print("\n" + "="*100)
print("NEXT STEPS TO DEBUG")
print("="*100)
print("""
1. REFRESH BROWSER (Ctrl + F5) - hard refresh to clear cache
2. Open DevTools Console (F12)
3. Navigate to Synergy tab
4. Expand the email thread quote card (double-click)
5. Look for console errors
6. Check if parseJsonField is called (look for logs)
7. Verify session object has correct data structure
8. Check if renderCardExpanded is executing
9. Inspect HTML elements to see if divs are created
10. Check CSS - maybe elements are hidden or have display:none

If still not showing:
- Check if card is in collapsed vs expanded state
- Verify onclick handlers are working
- Check if documents section HTML is being generated
- Look for JavaScript errors preventing rendering
""")
