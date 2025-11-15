"""Test that synergy API is now parsing JSON fields correctly"""
import requests
import json

print("="*80)
print("TESTING SYNERGY API AFTER FIX")
print("="*80)

try:
    response = requests.get('http://localhost:5001/api/synergy/list')
    print(f"\n✅ API Status: {response.status_code}")
    
    if response.ok:
        data = response.json()
        sessions = data.get('sessions', [])
        print(f"✅ Got {len(sessions)} sessions")
        
        # Find our target session
        target = None
        for s in sessions:
            if 'email_thread_quote' in s.get('session_id', ''):
                target = s
                break
        
        if target:
            print(f"\n✅ Found target session: {target['session_id']}")
            print(f"   Title: {target['title']}")
            
            print("\n" + "="*80)
            print("CHECKING ALL 10 JSON FIELDS")
            print("="*80)
            
            json_fields = ['platforms_involved', 'tags', 'documents', 'links', 
                          'next_steps', 'assignees', 'recent_activity', 'checklist',
                          'thread_ids', 'assigned_agents']
            
            all_good = True
            for field in json_fields:
                value = target.get(field)
                is_list = isinstance(value, list)
                is_dict = isinstance(value, dict)
                is_string = isinstance(value, str)
                
                status = "✅" if (is_list or is_dict) else "❌"
                type_str = type(value).__name__
                count = len(value) if isinstance(value, (list, dict)) else 0
                
                print(f"{status} {field:25} Type: {type_str:10} Count: {count}")
                
                if is_string:
                    print(f"   ⚠️  STILL A STRING! Value: {value[:100]}")
                    all_good = False
                elif is_list and count > 0:
                    print(f"   Sample: {value[0] if isinstance(value[0], str) else list(value[0].keys())[:3]}")
            
            print("\n" + "="*80)
            if all_good:
                print("✅ ✅ ✅  ALL FIELDS PARSED CORRECTLY!")
            else:
                print("❌ ❌ ❌  SOME FIELDS STILL STRINGS!")
            print("="*80)
            
            # Test documents specifically
            docs = target.get('documents')
            if isinstance(docs, list) and len(docs) > 0:
                print(f"\n✅ Documents is a list with {len(docs)} items")
                print(f"\nFirst 3 documents:")
                for i, doc in enumerate(docs[:3]):
                    if isinstance(doc, dict):
                        print(f"  {i+1}. Name: {doc.get('name', 'NO NAME')}")
                        print(f"      URL: {doc.get('url', 'NO URL')[:60]}...")
                    else:
                        print(f"  {i+1}. ❌ Not a dict: {type(doc)}")
            else:
                print(f"\n❌ Documents issue: type={type(docs)}, value={str(docs)[:100]}")
                
        else:
            print("\n❌ Target session not found")
    else:
        print(f"❌ API error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")
    import traceback
    traceback.print_exc()
