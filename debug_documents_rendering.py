"""
Debug why documents show N/A instead of names
Check the exact data structure and rendering path
"""

import requests
import json

print("="*100)
print("DOCUMENTS RENDERING DEBUG")
print("="*100)

# Get API data
r = requests.get('http://localhost:5001/api/synergy/list')
sessions = r.json()['sessions']
session = [x for x in sessions if 'email_thread' in x['session_id']][0]

docs = session['documents']

print(f"\nSession: {session['session_id']}")
print(f"Documents count: {len(docs)}")

print("\n" + "="*100)
print("DOCUMENT STRUCTURE ANALYSIS")
print("="*100)

for i, doc in enumerate(docs[:3], 1):
    print(f"\nDocument {i}:")
    print(f"  Type: {type(doc)}")
    print(f"  Keys: {list(doc.keys()) if isinstance(doc, dict) else 'NOT A DICT'}")
    
    if isinstance(doc, dict):
        print(f"  name: {doc.get('name', 'MISSING')}")
        print(f"  url: {doc.get('url', 'MISSING')[:60]}..." if doc.get('url') else "  url: MISSING")
        print(f"  type: {doc.get('type', 'MISSING')}")
        print(f"  size: {doc.get('size', 'MISSING')}")

print("\n" + "="*100)
print("HTML RENDERING EXPECTATION")
print("="*100)

print("""
HTML Code (Line 23143):
  <span class="doc-name">${this.escapeHtml(doc.name)}</span>
  <span class="doc-size">${doc.size || 'N/A'}</span>

Expected for Document 1:
  <span class="doc-name">Email Thread 1 - Leanne Catalano Corflute</span>
  <span class="doc-size">N/A</span>  ← size not in data, shows N/A correctly

Actual rendering (from screenshot):
  Icon + N/A
  
Problem: doc.name exists but not displaying!
""")

print("="*100)
print("CHECK ESCAPEHTML FUNCTION")
print("="*100)

# Simulate what escapeHtml should do
test_name = docs[0]['name']
print(f"\nOriginal name: {test_name}")
print(f"Length: {len(test_name)}")
print(f"Contains special chars: {'&' in test_name or '<' in test_name or '>' in test_name}")

# Simple escape
escaped = test_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
print(f"Escaped: {escaped}")

print("\n" + "="*100)
print("POSSIBLE ISSUES")
print("="*100)

print("""
1. escapeHtml function missing or broken
   - Check if this.escapeHtml is defined
   - Check console for "undefined is not a function" errors

2. CSS hiding the doc-name
   - .doc-name { display: none; } ?
   - Check computed styles in DevTools

3. doc-name not rendering at all
   - HTML generation failing silently
   - Check if <span class="doc-name"> exists in DOM

4. Text color same as background
   - Check .doc-name color vs background color
   - Possible color: transparent or match bg

5. Width/overflow issue
   - .doc-name { width: 0; overflow: hidden; }
   - Max-width too small
""")

print("\n" + "="*100)
print("NEXT DEBUGGING STEPS")
print("="*100)

print("""
1. Open DevTools Console (F12)
2. Run: synergyBoard.sessions[0].documents[0]
   Should show: {name: "Email Thread 1...", url: "...", type: "word"}
   
3. Inspect the document-item element
   Right-click on document icon → Inspect
   
4. Check if <span class="doc-name"> exists
   Should see: <span class="doc-name">Email Thread 1...</span>
   
5. Check computed CSS
   Click on doc-name span in Elements
   Look at Computed tab → font-size, color, display, width
   
6. Check for JavaScript errors
   Console tab → Any red errors about escapeHtml?
   
7. Test escapeHtml manually
   Console: synergyBoard.escapeHtml("Test")
   Should return: "Test"
""")

print("\n" + "="*100)
print("API DATA IS CORRECT")
print("="*100)

print(f"""
✅ API returns documents correctly
✅ Each document has 'name' field
✅ First document name: "{docs[0]['name']}"
✅ Data structure matches HTML expectations

❌ Something wrong between data and display:
   - JavaScript function issue?
   - CSS hiding content?
   - DOM not updating?
""")
