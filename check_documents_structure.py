"""Check if documents are stored correctly in database"""
import sqlite3
from pathlib import Path
import json

root = Path('C:/Users/gpoli/GIT/AI_agents')
db = root / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT session_id, title, documents 
    FROM synergy_sessions 
    WHERE session_id LIKE ?
""", ('%email_thread_quote%',))

row = cursor.fetchone()

if row:
    print("="*80)
    print("ANALYZING DOCUMENTS FIELD STRUCTURE")
    print("="*80)
    
    docs_raw = row['documents']
    print(f"\nRaw string length: {len(docs_raw)}")
    print(f"\nFirst 1000 characters:")
    print(docs_raw[:1000])
    
    # Try to parse
    try:
        docs = json.loads(docs_raw)
        print(f"\n✅ JSON parsed successfully!")
        print(f"Type: {type(docs)}")
        print(f"Length: {len(docs)}")
        
        if isinstance(docs, list):
            print(f"\nIt's a list with {len(docs)} items")
            print(f"First item type: {type(docs[0])}")
            print(f"First item: {docs[0]}")
            
            # Check if items are strings (wrong) or dicts (correct)
            if isinstance(docs[0], str):
                print("\n❌ ERROR: List contains strings, not objects!")
                print("The list items should be dicts like: {\"name\": \"...\", \"url\": \"...\"}")
                print(f"\nFirst 5 items:")
                for i, item in enumerate(docs[:5]):
                    print(f"  {i+1}. {item[:100]}")
            elif isinstance(docs[0], dict):
                print("\n✅ CORRECT: List contains dictionaries")
                print(f"\nFirst 3 documents:")
                for i, doc in enumerate(docs[:3]):
                    print(f"\n  Document {i+1}:")
                    for key, value in doc.items():
                        print(f"    {key}: {str(value)[:60]}")
            else:
                print(f"\n⚠️  Unexpected type: {type(docs[0])}")
        elif isinstance(docs, dict):
            print("\n⚠️  It's a dict, not a list")
            print(f"Keys: {list(docs.keys())}")
        else:
            print(f"\n❌ Unexpected type: {type(docs)}")
            
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error: {e}")
        print(f"Error position: {e.pos}")
        print(f"Context: {docs_raw[max(0, e.pos-50):e.pos+50]}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

conn.close()
