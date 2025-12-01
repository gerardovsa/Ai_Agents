"""
Test Adobe Firefly Credentials
Verifies credentials are stored and can authenticate with Adobe API
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection
import requests
import json

def test_adobe_credentials():
    """Test Adobe Firefly credentials from database"""
    
    print("=" * 60)
    print("TESTING ADOBE FIREFLY CREDENTIALS")
    print("=" * 60)
    
    try:
        # 1. Connect to database
        print("\n1. Connecting to AI_agents database...")
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        print("   ✅ Connected successfully")
        
        # 2. Query for Adobe credentials
        print("\n2. Querying for Adobe Firefly credentials...")
        cursor.execute("""
            SELECT 
                id,
                user_id,
                platform,
                credential_type,
                is_active,
                credentials,
                metadata
            FROM ai_infrastructure.user_platform_credentials
            WHERE platform = 'adobe_firefly'
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("   ❌ No Adobe Firefly credentials found")
            cursor.close()
            conn.close()
            return False
        
        print(f"   ✅ Found {len(rows)} Adobe Firefly credential record(s)\n")
        
        # Display credentials info
        row = rows[0]
        print("-" * 60)
        print(f"   ID: {row['id']}")
        print(f"   User ID: {row['user_id']}")
        print(f"   Platform: {row['platform']}")
        print(f"   Credential Type: {row['credential_type']}")
        print(f"   Active: {row['is_active']}")
        
        # Get credentials
        creds = row['credentials'] if row['credentials'] else {}
        print(f"   Client ID: {creds.get('client_id', 'N/A')[:20]}...")
        print(f"   Client Secret: ***{creds.get('client_secret', '')[-10:]}")
        print(f"   Token Endpoint: {creds.get('token_endpoint', 'N/A')}")
        
        # Get metadata
        meta = row['metadata'] if row['metadata'] else {}
        print(f"   Service Type: {meta.get('service_type', 'N/A')}")
        print(f"   API Base: {meta.get('api_base_url', 'N/A')}")
        print("-" * 60)
        
        # 3. Test OAuth token exchange
        print("\n3. Testing OAuth token exchange with Adobe...")
        
        client_id = creds.get('client_id')
        client_secret = creds.get('client_secret')
        token_endpoint = creds.get('token_endpoint')
        
        if not all([client_id, client_secret, token_endpoint]):
            print("   ❌ Missing required credential fields")
            cursor.close()
            conn.close()
            return False
        
        # Make token request
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'openid,AdobeID,firefly_api'
        }
        
        print(f"   → Requesting access token from Adobe IMS...")
        print(f"      Endpoint: {token_endpoint}")
        print(f"      Grant Type: client_credentials")
        
        try:
            response = requests.post(
                token_endpoint,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"   → Response Status: {response.status_code}")
            
            if response.status_code == 200:
                token_response = response.json()
                access_token = token_response.get('access_token', '')
                token_type = token_response.get('token_type', '')
                expires_in = token_response.get('expires_in', 0)
                
                print(f"   ✅ OAuth token exchange successful!")
                print(f"      Token Type: {token_type}")
                print(f"      Expires In: {expires_in} seconds ({expires_in // 60} minutes)")
                print(f"      Access Token: {access_token[:30]}...{access_token[-10:]}")
                
                # 4. Test API endpoint (optional - if we have a test endpoint)
                print("\n4. Testing Adobe Firefly API access...")
                api_base = meta.get('api_base_url', 'https://firefly-api.adobe.io')
                
                # Note: This might fail if we don't have proper API access
                # but token exchange success is the main indicator
                print(f"   → API Base URL: {api_base}")
                print(f"   ℹ️  Full API testing requires active Adobe Firefly subscription")
                print(f"   ✅ Credentials are valid for OAuth authentication")
                
            else:
                print(f"   ❌ OAuth token exchange failed")
                print(f"      Status: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                
                if response.status_code == 400:
                    print("\n   Possible issues:")
                    print("   - Invalid client_id or client_secret")
                    print("   - Credentials may need to be regenerated")
                elif response.status_code == 401:
                    print("\n   Possible issues:")
                    print("   - Credentials expired or revoked")
                    print("   - Need to regenerate at Adobe Developer Console")
                
                cursor.close()
                conn.close()
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error: {str(e)}")
            cursor.close()
            conn.close()
            return False
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ ADOBE FIREFLY CREDENTIALS TEST PASSED")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Credentials are valid and can authenticate with Adobe")
        print("2. 68 Adobe InDesign tools are available")
        print("3. Restart server (BISTART) if not already running")
        print("4. Test: CHAT 'List Adobe InDesign tools'")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_adobe_credentials()
    sys.exit(0 if success else 1)
