"""Test Google credentials for user_id=12"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from auth.credential_injector import CredentialInjector

print("="*70)
print("Testing Google Credentials for user_id=12")
print("="*70)

injector = CredentialInjector()

# Try to get credentials
try:
    creds = injector.get_google_credentials(user_id=12)
    
    if creds:
        print("\n✅ Credentials found for user_id=12")
        print(f"  Access token: {creds.get('access_token', 'N/A')[:50]}...")
        print(f"  Token expiry: {creds.get('token_expiry', 'N/A')}")
        
        # Check if token is expired
        from datetime import datetime
        if creds.get('token_expiry'):
            expiry = datetime.fromisoformat(creds['token_expiry'].replace('Z', '+00:00'))
            now = datetime.now(expiry.tzinfo)
            if expiry < now:
                print(f"  ⚠️  Token EXPIRED (expired {(now - expiry).total_seconds() / 3600:.1f} hours ago)")
            else:
                print(f"  ✅ Token valid (expires in {(expiry - now).total_seconds() / 3600:.1f} hours)")
    else:
        print("\n❌ No credentials found for user_id=12")
        print("  User needs to authenticate with Google OAuth")
        
except Exception as e:
    print(f"\n❌ Error getting credentials: {e}")
    import traceback
    traceback.print_exc()

print("="*70)
