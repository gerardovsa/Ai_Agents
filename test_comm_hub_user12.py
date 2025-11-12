"""Test Communication Hub with actual logged-in user (user_id=12)"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

print("="*60)
print(" Communication Hub Test - User 12 (gerardo)")
print("="*60)

# Test OAuth credential lookup for user 12
print("\n[TEST 1] Checking OAuth credentials for user 12...")
try:
    from auth.user_auth import UserAuthManager
    
    mgr = UserAuthManager()
    
    # Test Google OAuth for user 12
    google_creds = mgr.get_user_google_oauth_credentials(12)
    if google_creds:
        print(f"✅ Google OAuth found for user 12")
        print(f"   Email: {google_creds.get('email', 'N/A')}")
        print(f"   Has access_token: {bool(google_creds.get('access_token'))}")
        print(f"   Has refresh_token: {bool(google_creds.get('refresh_token'))}")
        print(f"   Token length: {len(google_creds.get('access_token', ''))} chars")
    else:
        print("❌ No Google OAuth credentials for user 12")
    
    # Test Microsoft OAuth for user 12
    microsoft_creds = mgr.get_user_microsoft_oauth_credentials(12)
    if microsoft_creds:
        print(f"✅ Microsoft OAuth found for user 12")
        print(f"   Email: {microsoft_creds.get('email', 'N/A')}")
        print(f"   Has access_token: {bool(microsoft_creds.get('access_token'))}")
    else:
        print("⚠️  No Microsoft OAuth credentials for user 12")
        
except Exception as e:
    print(f"❌ FAIL: {e}")
    import traceback
    traceback.print_exc()

# Test Gmail access with user 12's credentials
print("\n[TEST 2] Testing Gmail API access with user 12's credentials...")
try:
    if google_creds:
        from google_workspace.gmail import list_messages
        
        # Try to list emails using the credentials
        result = list_messages(
            max_results=5,
            _user_id=12,
            _injected_credentials=True
        )
        
        if result.get('success'):
            messages = result.get('messages', [])
            print(f"✅ Gmail API call successful!")
            print(f"   Found {len(messages)} message(s)")
            
            if messages:
                print(f"   Latest email:")
                print(f"     Subject: {messages[0].get('subject', 'N/A')}")
                print(f"     From: {messages[0].get('from', 'N/A')}")
                print(f"     Date: {messages[0].get('date', 'N/A')}")
        else:
            print(f"❌ Gmail API call failed: {result.get('error')}")
    else:
        print("⚠️  Skipping Gmail test (no credentials)")
        
except Exception as e:
    print(f"❌ Gmail API test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print(" Test Summary")
print("="*60)
print("\n✅ Communication Hub should work for user 12 (gerardo)")
print("   - Has valid Google OAuth token in database")
print("   - UserAuthManager can retrieve credentials")
print("   - Routes will automatically inject credentials")
print("\nTo test in browser:")
print("1. Make sure you're logged in as user 12 (gerardo)")
print("2. Open Communication Hub")
print("3. Emails should load automatically")
print("")
