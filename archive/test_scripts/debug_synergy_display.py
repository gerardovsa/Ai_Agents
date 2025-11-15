"""Debug why synergy card data isn't displaying"""
import sqlite3
from pathlib import Path
import json

root = Path('C:/Users/gpoli/GIT/AI_agents')
db = root / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the email thread quote session
cursor.execute("""
    SELECT * FROM synergy_sessions 
    WHERE session_id LIKE ?
""", ('%email_thread_quote%',))

row = cursor.fetchone()

if row:
    print("="*80)
    print("SESSION DATA IN DATABASE")
    print("="*80)
    print(f"\nSession ID: {row['session_id']}")
    print(f"Title: {row['title']}")
    print(f"Description: {row['description'][:100]}...")
    
    print("\n" + "="*80)
    print("DOCUMENTS FIELD")
    print("="*80)
    
    docs_raw = row['documents']
    print(f"\nRaw type: {type(docs_raw)}")
    print(f"Raw length: {len(docs_raw) if docs_raw else 0}")
    print(f"\nFirst 500 chars:")
    print(docs_raw[:500] if docs_raw else "NULL")
    
    # Try to parse
    if docs_raw:
        try:
            docs = json.loads(docs_raw)
            print(f"\n✅ Parsed successfully!")
            print(f"Count: {len(docs)}")
            print(f"\nFirst 3 documents:")
            for i, doc in enumerate(docs[:3]):
                print(f"\n  Document {i+1}:")
                print(f"    Name: {doc.get('name', 'NO NAME')}")
                print(f"    URL: {doc.get('url', 'NO URL')[:60]}...")
                print(f"    Has 'name' key: {'name' in doc}")
                print(f"    Has 'url' key: {'url' in doc}")
                print(f"    All keys: {list(doc.keys())}")
        except Exception as e:
            print(f"\n❌ Parse error: {e}")
    
    print("\n" + "="*80)
    print("NEXT STEPS FIELD")
    print("="*80)
    
    steps_raw = row['next_steps']
    print(f"\nRaw type: {type(steps_raw)}")
    print(f"Raw value: {steps_raw[:200] if steps_raw else 'NULL'}")
    
    if steps_raw:
        try:
            steps = json.loads(steps_raw)
            print(f"✅ Parsed: {len(steps)} steps")
            for i, step in enumerate(steps[:2]):
                print(f"  {i+1}. {step}")
        except Exception as e:
            print(f"❌ Parse error: {e}")
    
    print("\n" + "="*80)
    print("TAGS FIELD")
    print("="*80)
    
    tags_raw = row['tags']
    print(f"\nRaw: {tags_raw}")
    
    if tags_raw:
        try:
            tags = json.loads(tags_raw)
            print(f"✅ Parsed: {tags}")
        except Exception as e:
            print(f"❌ Parse error: {e}")

conn.close()

print("\n" + "="*80)
print("NOW TEST API ENDPOINT")
print("="*80)

import requests

try:
    response = requests.get('http://localhost:5001/api/synergy/list')
    print(f"\nStatus: {response.status_code}")
    
    if response.ok:
        data = response.json()
        sessions = data.get('sessions', [])
        
        # Find our session
        target_session = None
        for s in sessions:
            if 'email_thread_quote' in s.get('session_id', ''):
                target_session = s
                break
        
        if target_session:
            print(f"\n✅ Found session in API response")
            print(f"Title: {target_session.get('title')}")
            
            docs = target_session.get('documents')
            print(f"\nDocuments field type: {type(docs)}")
            print(f"Documents is list: {isinstance(docs, list)}")
            print(f"Documents count: {len(docs) if isinstance(docs, list) else 'N/A'}")
            
            if isinstance(docs, list) and len(docs) > 0:
                print(f"\nFirst document:")
                print(f"  Type: {type(docs[0])}")
                print(f"  Content: {docs[0]}")
            elif isinstance(docs, str):
                print(f"\n⚠️  Documents is still a STRING in API response!")
                print(f"  Value: {docs[:200]}")
        else:
            print("\n❌ Session not found in API response")
            print(f"Available session IDs: {[s.get('session_id') for s in sessions[:3]]}")
    else:
        print(f"❌ API error: {response.status_code}")
        
except Exception as e:
    print(f"❌ API request failed: {e}")
