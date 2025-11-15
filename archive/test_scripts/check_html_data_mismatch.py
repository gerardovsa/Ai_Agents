"""
Check each JSON field to see if HTML code expects wrong structure
"""

import requests

# Get API data
r = requests.get('http://localhost:5001/api/synergy/list')
sessions = r.json()['sessions']
session = [x for x in sessions if 'email_thread' in x['session_id']][0]

print("="*100)
print("DATA STRUCTURE VS HTML EXPECTATIONS")
print("="*100)

# 1. DOCUMENTS
print("\n1. DOCUMENTS")
print("-"*80)
docs = session['documents']
print(f"API returns: {type(docs)}")
print(f"First item: {type(docs[0]) if len(docs) > 0 else 'N/A'}")
if len(docs) > 0:
    print(f"First item keys: {docs[0].keys() if isinstance(docs[0], dict) else 'NOT A DICT'}")
print(f"HTML expects: doc.name, doc.url, doc.size")
print(f"Match: {'✅ YES' if len(docs) > 0 and isinstance(docs[0], dict) and 'name' in docs[0] else '❌ NO'}")

# 2. TAGS
print("\n2. TAGS")
print("-"*80)
tags = session['tags']
print(f"API returns: {type(tags)}")
print(f"First item: {type(tags[0]) if len(tags) > 0 else 'N/A'}")
if len(tags) > 0:
    print(f"First item value: {tags[0]}")
print(f"HTML expects: Just string values in array")
print(f"Match: {'✅ YES' if len(tags) > 0 and isinstance(tags[0], str) else '❌ NO'}")

# 3. NEXT STEPS
print("\n3. NEXT STEPS")
print("-"*80)
steps = session['next_steps']
print(f"API returns: {type(steps)}")
print(f"First item: {type(steps[0]) if len(steps) > 0 else 'N/A'}")
if len(steps) > 0:
    print(f"First item value: {steps[0][:80]}")
print(f"HTML expects: step.description, step.completed, step.due_date")
print(f"Match: {'❌ NO - STRINGS NOT OBJECTS!' if len(steps) > 0 and isinstance(steps[0], str) else '✅ YES'}")

# 4. CHECKLIST
print("\n4. CHECKLIST")
print("-"*80)
checklist = session['checklist']
print(f"API returns: {type(checklist)}")
print(f"Length: {len(checklist)}")
if len(checklist) > 0:
    print(f"First item: {type(checklist[0])}")
    print(f"First item: {checklist[0]}")
print(f"HTML expects: item.item, item.completed")
print(f"Match: {'✅ YES' if len(checklist) > 0 and isinstance(checklist[0], dict) else '⚠️ EMPTY ARRAY'}")

# 5. LINKS
print("\n5. LINKS")
print("-"*80)
links = session['links']
print(f"API returns: {type(links)}")
print(f"Length: {len(links)}")
if len(links) > 0:
    print(f"First item: {type(links[0])}")
    print(f"First item keys: {links[0].keys()}")
print(f"HTML expects: link.url, link.title, link.type")
print(f"Match: {'✅ YES' if len(links) > 0 and isinstance(links[0], dict) else '⚠️ EMPTY ARRAY'}")

# 6. ASSIGNEES
print("\n6. ASSIGNEES")
print("-"*80)
assignees = session['assignees']
print(f"API returns: {type(assignees)}")
print(f"Length: {len(assignees)}")
if len(assignees) > 0:
    print(f"First item: {type(assignees[0])}")
    print(f"First item value: {assignees[0]}")
print(f"HTML expects: Just string values in array, then .join(', ')")
print(f"Match: {'✅ YES' if len(assignees) > 0 and isinstance(assignees[0], str) else '⚠️ EMPTY ARRAY'}")

# 7. THREAD_IDS
print("\n7. THREAD_IDS")
print("-"*80)
threads = session['thread_ids']
print(f"API returns: {type(threads)}")
print(f"First item: {type(threads[0]) if len(threads) > 0 else 'N/A'}")
if len(threads) > 0:
    print(f"First item value: {threads[0]}")
print(f"HTML expects: Array of strings, then renderLinkedThreads(threadIds) fetches details")
print(f"Match: {'✅ YES' if len(threads) > 0 and isinstance(threads[0], str) else '❌ NO'}")

# 8. ASSIGNED_AGENTS
print("\n8. ASSIGNED_AGENTS")
print("-"*80)
agents = session['assigned_agents']
print(f"API returns: {type(agents)}")
print(f"First item: {type(agents[0]) if len(agents) > 0 else 'N/A'}")
if len(agents) > 0:
    print(f"First item value: {agents[0]}")
print(f"HTML expects: Just string values in array")
print(f"Match: {'✅ YES' if len(agents) > 0 and isinstance(agents[0], str) else '❌ NO'}")

print("\n" + "="*100)
print("SUMMARY OF MISMATCHES")
print("="*100)
print("""
❌ CRITICAL ISSUE: next_steps

   API returns: Array of STRINGS
   ["Create quote for...", "Create quote for...", ...]
   
   HTML expects: Array of OBJECTS
   [{description: "...", completed: false, due_date: null}, ...]
   
   Result: HTML filters out ALL items because it's checking:
   step.description && step.description.trim() !== ''
   But step IS a string, not an object with .description!
   
   FIX NEEDED: Change HTML to handle plain strings OR
              Change database to store objects

✅ documents - Correct structure (dict with name, url, type)
✅ tags - Correct structure (plain strings)
✅ thread_ids - Correct structure (plain strings)
✅ assigned_agents - Correct structure (plain strings)
⚠️  checklist - Empty but expects correct structure
⚠️  links - Empty but expects correct structure
⚠️  assignees - Empty but expects correct structure
""")

