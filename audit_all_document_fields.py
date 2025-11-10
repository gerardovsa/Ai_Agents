"""
Audit ALL sessions to find which ones have wrong field names
"""
import sqlite3
import json

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT session_id, title, documents FROM synergy_sessions ORDER BY created_at DESC")
rows = cursor.fetchall()

print("=" * 120)
print(f"AUDIT: {len(rows)} TOTAL SESSIONS")
print("=" * 120)

correct_sessions = []
incorrect_sessions = []
empty_sessions = []

for session_id, title, documents_json in rows:
    if not documents_json:
        empty_sessions.append((session_id, title))
        continue
        
    documents = json.loads(documents_json)
    
    if not documents:
        empty_sessions.append((session_id, title))
        continue
    
    first_doc = documents[0]
    has_name = 'name' in first_doc
    has_title = 'title' in first_doc
    
    if has_name and not has_title:
        correct_sessions.append((session_id, title, len(documents)))
    elif has_title and not has_name:
        incorrect_sessions.append((session_id, title, len(documents)))
    else:
        print(f"\nWEIRD: {session_id} has both or neither!")

conn.close()

print(f"\n✅ CORRECT (using 'name'): {len(correct_sessions)} sessions")
for session_id, title, count in correct_sessions[:5]:
    print(f"   {session_id[:50]}... ({count} docs)")

print(f"\n❌ INCORRECT (using 'title'): {len(incorrect_sessions)} sessions")
for session_id, title, count in incorrect_sessions:
    print(f"   {session_id[:50]}... - '{title[:50]}' ({count} docs)")

print(f"\n⚪ EMPTY (no documents): {len(empty_sessions)} sessions")

print("\n" + "=" * 120)
print("SUMMARY")
print("=" * 120)
print(f"\nTotal sessions: {len(rows)}")
print(f"  Correct (name): {len(correct_sessions)}")
print(f"  Incorrect (title): {len(incorrect_sessions)}")
print(f"  Empty: {len(empty_sessions)}")

if incorrect_sessions:
    print(f"\n🔧 NEED TO FIX: {len(incorrect_sessions)} sessions with wrong field name")
    print("\nCREATE MIGRATION SCRIPT TO:")
    print("  1. Read each incorrect session")
    print("  2. Rename 'title' → 'name' in all documents")
    print("  3. Update database")
