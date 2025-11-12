"""
Test Communication Hub Authentication
Shows if Communication Hub can access OAuth tokens correctly
"""

import sqlite3
from pathlib import Path

# Test 1: Check oauth_tokens directly
print("=" * 70)
print("TEST 1: OAuth Tokens in Database")
print("=" * 70)

db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT user_id, platform, email, account_identifier, 
           LENGTH(access_token) as token_length, is_active
    FROM oauth_tokens
    ORDER BY user_id
""")

tokens = cursor.fetchall()
conn.close()

print(f"Found {len(tokens)} OAuth tokens:\n")
for token in tokens:
    print(f"  User {token['user_id']}: {token['platform']}")
    print(f"    Email: {token['email'] or token['account_identifier'] or '(none)'}")
    print(f"    Token: {token['token_length']} chars")
    print(f"    Active: {token['is_active']}")
    print()

# Test 2: Test UserAuthManager method
print("=" * 70)
print("TEST 2: UserAuthManager.get_user_google_oauth_credentials()")
print("=" * 70)

try:
    import sys
    sys.path.insert(0, 'AI_infrastructure')
    from auth.user_auth import UserAuthManager
    
    auth_manager = UserAuthManager()
    
    # Test each user with Google tokens
    google_users = [t['user_id'] for t in tokens if t['platform'] == 'google']
    
    for user_id in google_users:
        print(f"\nTesting user {user_id}...")
        try:
            creds = auth_manager.get_user_google_oauth_credentials(user_id)
            if creds:
                print(f"  ✅ SUCCESS! Got credentials")
                print(f"     Keys: {list(creds.keys())}")
                print(f"     Has access_token: {len(creds.get('access_token', '')) > 0}")
                print(f"     Has refresh_token: {len(creds.get('refresh_token', '')) > 0}")
            else:
                print(f"  ❌ FAILED: No credentials returned")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
except Exception as e:
    print(f"❌ Failed to import UserAuthManager: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test Gmail tool with credential injection
print("\n" + "=" * 70)
print("TEST 3: Gmail Tool with Credential Injection")
print("=" * 70)

try:
    from google_workspace.gmail import gmail_list_messages
    
    # Test with first Google user
    if google_users:
        user_id = google_users[0]
        print(f"\nTesting gmail_list_messages with user {user_id}...")
        print("Calling: gmail_list_messages(max_results=5, _user_id={user_id}, _injected_credentials=True)\n")
        
        result = gmail_list_messages(
            max_results=5,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if result.get('success'):
            messages = result.get('messages', [])
            print(f"✅ SUCCESS! Got {len(messages)} messages")
            if messages:
                print(f"\nFirst message:")
                print(f"  From: {messages[0].get('from', 'N/A')}")
                print(f"  Subject: {messages[0].get('subject', 'N/A')}")
                print(f"  Date: {messages[0].get('date', 'N/A')}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    else:
        print("No Google users found to test")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
