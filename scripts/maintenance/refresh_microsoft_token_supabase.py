"""
Refresh Expired Microsoft OAuth Token in Supabase
==================================================

This script refreshes an expired Microsoft OAuth token using the refresh token.

Usage:
    python scripts/maintenance/refresh_microsoft_token_supabase.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
import json

# Add project root and AI_infrastructure to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

from shared.database_utils import get_database_connection
from dotenv import load_dotenv
import os

# Load environment
env_file = project_root / '.env.master'
load_dotenv(env_file)

def refresh_microsoft_token(user_id=14):
    """
    Refresh Microsoft OAuth token for user
    
    Args:
        user_id: User ID to refresh token for (default: 14)
    """
    print("\n" + "="*80)
    print("MICROSOFT OAUTH TOKEN REFRESH")
    print("="*80)
    
    try:
        # Get connection
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get current token
        print(f"\n1. Fetching current token for user {user_id}...")
        cursor.execute("""
            SELECT 
                id,
                access_token,
                refresh_token,
                expires_at,
                scope
            FROM ai_infrastructure.oauth_tokens
            WHERE user_id = %s AND platform = 'microsoft'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            print(f"   ❌ No Microsoft token found for user {user_id}")
            conn.close()
            return False
        
        token_id = row['id']
        refresh_token = row['refresh_token']
        old_access_token = row['access_token']
        old_expires_at = row['expires_at']
        scope = row['scope']
        
        print(f"   ✅ Found token (ID: {token_id})")
        print(f"      Current expires_at: {old_expires_at}")
        print(f"      Refresh token: {refresh_token[:20]}..." if refresh_token else "      Refresh token: None")
        
        if not refresh_token:
            print("\n   ❌ No refresh token available - user must re-authenticate")
            conn.close()
            return False
        
        # Get Microsoft OAuth config
        client_id = os.getenv('MICROSOFT_CLIENT_ID')
        client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
        tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
        
        if not client_id or not client_secret:
            print("\n   ❌ Microsoft OAuth credentials not found in .env.master")
            print("      Required: MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET")
            conn.close()
            return False
        
        print(f"\n2. Refreshing token with Microsoft...")
        print(f"   Client ID: {client_id[:20]}...")
        print(f"   Tenant ID: {tenant_id}")
        
        # Make token refresh request
        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': scope or 'offline_access User.Read Mail.ReadWrite Calendars.ReadWrite'
        }
        
        response = requests.post(token_url, data=payload)
        
        if response.status_code != 200:
            print(f"\n   ❌ Token refresh failed: {response.status_code}")
            print(f"      Error: {response.text}")
            conn.close()
            return False
        
        token_data = response.json()
        
        new_access_token = token_data['access_token']
        new_refresh_token = token_data.get('refresh_token', refresh_token)  # Some refreshes don't return new refresh token
        expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
        
        # Calculate new expiry
        new_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        print(f"\n   ✅ Token refreshed successfully!")
        print(f"      New access token: {new_access_token[:20]}...")
        print(f"      New expires_at: {new_expires_at.isoformat()}")
        print(f"      Expires in: {expires_in} seconds ({expires_in // 3600} hours)")
        
        # Update token in database
        print(f"\n3. Updating token in Supabase...")
        cursor.execute("""
            UPDATE ai_infrastructure.oauth_tokens
            SET 
                access_token = %s,
                refresh_token = %s,
                expires_at = %s,
                updated_at = CURRENT_TIMESTAMP,
                is_valid = TRUE
            WHERE id = %s
        """, (new_access_token, new_refresh_token, new_expires_at.isoformat(), token_id))
        
        conn.commit()
        print(f"   ✅ Token updated in database (ID: {token_id})")
        
        # Verify update
        cursor.execute("""
            SELECT expires_at, updated_at
            FROM ai_infrastructure.oauth_tokens
            WHERE id = %s
        """, (token_id,))
        
        verify_row = cursor.fetchone()
        print(f"\n4. Verification:")
        print(f"   Expires at: {verify_row['expires_at']}")
        print(f"   Updated at: {verify_row['updated_at']}")
        
        conn.close()
        
        print("\n" + "="*80)
        print("✅ SUCCESS! Microsoft OAuth token refreshed and updated in Supabase")
        print("="*80)
        print("\nYour Render deployment should now work with Microsoft tools!")
        print("Try: microsoft_outlook_search_messages again\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error refreshing token: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print("\n🔄 Microsoft OAuth Token Refresh Tool")
    print("   Purpose: Refresh expired access tokens in Supabase")
    
    success = refresh_microsoft_token(user_id=14)
    
    if not success:
        print("\n⚠️  Token refresh failed. You may need to re-authenticate.")
        print("   Visit your Render deployment and connect Microsoft account again.")
    
    print()


if __name__ == '__main__':
    main()
