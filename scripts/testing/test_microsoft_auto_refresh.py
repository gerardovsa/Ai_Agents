"""
Test Microsoft OAuth Auto-Refresh Implementation

This script tests the automatic token refresh for Microsoft OAuth credentials,
verifying that expired tokens are automatically refreshed when tools are executed.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'AI_infrastructure'))

from auth.credential_injector import create_microsoft_service_with_user_credentials
from auth.user_auth import UserAuthManager
from shared.db_connection_wrapper import get_connection
from datetime import datetime, timedelta, timezone

def test_auto_refresh():
    """Test Microsoft token auto-refresh by temporarily expiring a token"""
    
    user_id = 14
    print("\n" + "="*70)
    print("TEST: Microsoft OAuth Auto-Refresh")
    print("="*70)
    
    # Step 1: Get current token
    print("\n1️⃣ Getting current token state...")
    auth_manager = UserAuthManager()
    creds_before = auth_manager.get_user_microsoft_oauth_credentials(user_id)
    
    if not creds_before:
        print("❌ No Microsoft credentials found for user 14")
        return
    
    print(f"   Access Token: {creds_before['access_token'][:50]}...")
    print(f"   Expires At: {creds_before['expires_at']}")
    print(f"   Has Refresh Token: {bool(creds_before.get('refresh_token'))}")
    
    # Step 2: Temporarily set token to expired (1 minute ago)
    print("\n2️⃣ Temporarily setting token to expired (for testing)...")
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Save original expiry time for restoration
    cursor.execute("""
        SELECT expires_at FROM oauth_tokens 
        WHERE user_id = %s AND platform = 'microsoft'
    """, (user_id,))
    result = cursor.fetchone()
    original_expiry = result['expires_at'] if isinstance(result, dict) else result[0] if result else None
    
    # Set to expired
    cursor.execute("""
        UPDATE oauth_tokens
        SET expires_at = %s
        WHERE user_id = %s AND platform = 'microsoft'
    """, (expired_time.isoformat(), user_id))
    conn.commit()
    conn.close()
    
    print(f"   ✅ Token set to expired: {expired_time.isoformat()}")
    
    # Step 3: Try to create service (should trigger auto-refresh)
    print("\n3️⃣ Creating Microsoft service (should auto-refresh expired token)...")
    try:
        service = create_microsoft_service_with_user_credentials(user_id)
        print("   ✅ Service created successfully!")
        print(f"   New Access Token: {service['access_token'][:50]}...")
        print(f"   New Expires At: {service['expires_at']}")
        
        # Step 4: Verify token was refreshed in database
        print("\n4️⃣ Verifying token was saved to database...")
        auth_manager = UserAuthManager()
        creds_after = auth_manager.get_user_microsoft_oauth_credentials(user_id)
        
        print(f"   Access Token Changed: {creds_after['access_token'] != creds_before['access_token']}")
        print(f"   New Expires At: {creds_after['expires_at']}")
        
        # Parse new expiry
        new_expiry = datetime.fromisoformat(str(creds_after['expires_at']))
        if new_expiry.tzinfo is None:
            new_expiry = new_expiry.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        time_until_expiry = new_expiry - now
        
        print(f"   Token Valid For: {time_until_expiry.total_seconds() / 60:.1f} minutes")
        
        if time_until_expiry.total_seconds() > 0:
            print("\n✅ SUCCESS! Auto-refresh working correctly!")
            print("   - Token was expired")
            print("   - Auto-refresh detected expiry")
            print("   - New token obtained from Microsoft")
            print("   - New token saved to database")
            print("   - Service created with fresh token")
        else:
            print("\n⚠️ WARNING: Token still appears expired")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("Test complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_auto_refresh()
