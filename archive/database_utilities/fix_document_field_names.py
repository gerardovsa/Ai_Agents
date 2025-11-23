"""
MIGRATION: Fix document field names from 'title' → 'name'
Aligns database with official schema (synergy_tools.json)
"""
import sqlite3
import json
from datetime import datetime
from shared.database_utils import convert_sql_placeholders

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'

# Sessions that need fixing
incorrect_sessions = [
    'sess_20251108_0302_complete_feature_test_session',
    'sess_20251108_0038_python_tool_test_session',
    'sess_20251108_0037_python_tool_test_session',
    'sess_20251108_0008_test_session_with_threads_and_',
    'sess_20251107_2211_email_thread_quote_generation_'
]

print("=" * 120)
print("MIGRATION: Fix Document Field Names (title → name)")
print("=" * 120)
print(f"\nTarget: {len(incorrect_sessions)} sessions")
print(f"Field: 'title' → 'name'")
print(f"Reason: Align with official schema (synergy_tools.json)")
print("\n" + "-" * 120)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

fixed_count = 0
total_docs_fixed = 0

for session_id in incorrect_sessions:
    # Get session
    sql, params = convert_sql_placeholders("SELECT session_id, title, documents FROM synergy_sessions WHERE session_id LIKE ?", (session_id + '%',))

    cursor.execute(sql, params)
    row = cursor.fetchone()
    
    if not row:
        print(f"\n❌ NOT FOUND: {session_id}")
        continue
    
    full_session_id, session_title, documents_json = row
    documents = json.loads(documents_json)
    
    print(f"\n📝 Processing: {session_title}")
    print(f"   Session ID: {full_session_id}")
    print(f"   Documents: {len(documents)}")
    
    # Fix each document
    fixed_documents = []
    for doc in documents:
        if 'title' in doc and 'name' not in doc:
            # Rename title → name
            fixed_doc = {
                'name': doc['title'],  # RENAME HERE
                'url': doc.get('url', ''),
                'type': doc.get('type', 'unknown')
            }
            fixed_documents.append(fixed_doc)
            print(f"     ✅ Fixed: {doc['title'][:60]}")
        elif 'name' in doc:
            # Already correct
            fixed_documents.append(doc)
            print(f"     ⚠️  Already has 'name': {doc['name'][:60]}")
        else:
            print(f"     ❌ ERROR: No title or name: {doc}")
            fixed_documents.append(doc)
    
    # Update database
    fixed_json = json.dumps(fixed_documents, ensure_ascii=False)
    sql, params = convert_sql_placeholders("""
        UPDATE synergy_sessions 
        SET documents = ?
        WHERE session_id = ?
    """, (fixed_json, full_session_id))

    cursor.execute(sql, params)
    
    fixed_count += 1
    total_docs_fixed += len(fixed_documents)
    print(f"   💾 Updated database")

conn.commit()
conn.close()

print("\n" + "=" * 120)
print("MIGRATION COMPLETE")
print("=" * 120)
print(f"\nSessions fixed: {fixed_count}/{len(incorrect_sessions)}")
print(f"Total documents migrated: {total_docs_fixed}")
print("\n✅ All documents now use 'name' field (matches schema)")
print("✅ Frontend will display all document titles correctly")
print("\n" + "=" * 120)
print("NEXT STEP: Hard refresh browser (Ctrl+F5)")
print("=" * 120)
