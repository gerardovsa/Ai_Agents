"""
Fix the 5 migrated sessions - convert title to name in documents/links
"""
import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get the 5 migrated sessions
migrated_ids = [
    'sess_20251101_1410_sarah_customer_onboarding_system',
    'sess_20251101_1410_michael_e-commerce_store_setup',
    'sess_20251101_1410_alex_content_workflow_system',
    'sess_20251101_1410_david_sales_pipeline_automation',
    'sess_20251101_1410_rachel_customer_support_portal'
]

print("\n=== FIXING MIGRATED SESSIONS ===\n")

fixed_count = 0

for session_id in migrated_ids:
    cursor.execute('SELECT documents, links FROM synergy_sessions WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"SESSION NOT FOUND: {session_id}")
        continue
    
    documents_raw, links_raw = row
    
    print(f"\n{session_id}")
    
    # Fix documents - convert 'title' to 'name'
    documents = []
    if documents_raw and documents_raw.strip() != '[]':
        try:
            docs_data = json.loads(documents_raw)
            for doc in docs_data:
                if isinstance(doc, dict):
                    # Convert 'title' to 'name'
                    if 'title' in doc and 'name' not in doc:
                        doc['name'] = doc.pop('title')
                    documents.append(doc)
            print(f"  Fixed {len(documents)} documents (title → name)")
        except Exception as e:
            print(f"  ERROR fixing documents: {e}")
            continue
    
    # Fix links - convert 'title' to 'name' (or just add 'name' field)
    links = []
    if links_raw and links_raw.strip() != '[]':
        try:
            links_data = json.loads(links_raw)
            for link in links_data:
                if isinstance(link, dict):
                    # Convert 'title' to 'name' for consistency
                    if 'title' in link and 'name' not in link:
                        link['name'] = link.pop('title')
                    links.append(link)
            print(f"  Fixed {len(links)} links (title → name)")
        except Exception as e:
            print(f"  ERROR fixing links: {e}")
            continue
    
    # Update database
    try:
        cursor.execute(
            'UPDATE synergy_sessions SET documents = ?, links = ? WHERE session_id = ?',
            (json.dumps(documents), json.dumps(links), session_id)
        )
        fixed_count += 1
        print(f"  Updated database")
    except Exception as e:
        print(f"  ERROR updating database: {e}")

conn.commit()
conn.close()

print(f"\n\n=== SUMMARY ===")
print(f"Fixed: {fixed_count}/5 sessions")
print(f"\nDone! All migrated sessions now use 'name' field consistently.")
