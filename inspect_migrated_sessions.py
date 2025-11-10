"""
Inspect the 5 migrated sessions that have "Unknown format" documents
"""
import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the 5 migrated sessions
migrated_ids = [
    'sess_20251101_1410_sarah_customer_onboarding_system',
    'sess_20251101_1410_michael_e-commerce_store_setup',
    'sess_20251101_1410_alex_content_workflow_system',
    'sess_20251101_1410_david_sales_pipeline_automation',
    'sess_20251101_1410_rachel_customer_support_portal'
]

print("\n=== INSPECTING MIGRATED SESSIONS ===\n")

for session_id in migrated_ids:
    cursor.execute('SELECT * FROM synergy_sessions WHERE session_id = ?', (session_id,))
    session = cursor.fetchone()
    
    if not session:
        print(f"SESSION NOT FOUND: {session_id}\n")
        continue
    
    print(f"\n{session_id}")
    print(f"  Title: {session['title']}")
    print(f"  Description: {session['description'][:100] if session['description'] else 'None'}...")
    
    # Check documents field
    documents = session['documents']
    print(f"\n  Documents field:")
    print(f"    Type: {type(documents)}")
    print(f"    Length: {len(documents) if documents else 0}")
    print(f"    First 200 chars: {documents[:200] if documents else 'None'}")
    
    # Check links field  
    links = session['links']
    print(f"\n  Links field:")
    print(f"    Type: {type(links)}")
    print(f"    Length: {len(links) if links else 0}")
    print(f"    First 200 chars: {links[:200] if links else 'None'}")
    
    # Check notes field
    notes = session['notes']
    print(f"\n  Notes field:")
    print(f"    Type: {type(notes)}")
    print(f"    Value: {notes[:200] if notes else 'None'}")
    
    print(f"\n  {'='*80}\n")

conn.close()
