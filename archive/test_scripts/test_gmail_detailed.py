"""
Detailed Gmail API Test
Shows exact error messages
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from google_workspace.gmail import gmail_list_messages

print("Testing gmail_list_messages with user 3...")
print("=" * 70)

try:
    result = gmail_list_messages(
        max_results=5,
        _user_id=3,
        _injected_credentials=True
    )
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        messages = result.get('messages', [])
        print(f"✅ Got {len(messages)} messages!")
        for i, msg in enumerate(messages, 1):
            print(f"\n  Message {i}:")
            print(f"    ID: {msg.get('id')}")
            print(f"    From: {msg.get('from', 'N/A')}")
            print(f"    Subject: {msg.get('subject', 'N/A')[:50]}...")
            print(f"    Date: {msg.get('date', 'N/A')}")
    else:
        print(f"\n❌ Failed!")
        print(f"Error: {result.get('error')}")
        print(f"Error Type: {result.get('error_type')}")
        
        if 'full_error' in result:
            print(f"\nFull error details:")
            print(result['full_error'])
            
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
