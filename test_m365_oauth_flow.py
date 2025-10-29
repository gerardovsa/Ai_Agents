"""
Test Microsoft 365 OAuth Flow
==============================

Tests the complete OAuth flow to identify where the invalid_client error occurs.
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', 'common')
REDIRECT_URI = "http://localhost:5001/api/auth/microsoft/callback"

print("=" * 70)
print("🧪 MICROSOFT 365 OAUTH FLOW TEST")
print("=" * 70)
print()
print(f"Client ID: {CLIENT_ID}")
print(f"Tenant ID: {TENANT_ID}")
print(f"Client Secret: {'*' * len(CLIENT_SECRET)}")
print(f"Redirect URI: {REDIRECT_URI}")
print()

# Step 1: Generate authorization URL
auth_endpoint = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
scopes = "openid profile email User.Read Mail.Read"

auth_url = (
    f"{auth_endpoint}?"
    f"client_id={CLIENT_ID}&"
    f"response_type=code&"
    f"redirect_uri={REDIRECT_URI}&"
    f"response_mode=query&"
    f"scope={scopes.replace(' ', '%20')}&"
    f"state=test_state"
)

print("=" * 70)
print("STEP 1: Authorization URL")
print("=" * 70)
print(f"✅ Generated: {auth_url[:100]}...")
print()
print("🔗 Full URL:")
print(auth_url)
print()

# Step 2: Simulate token exchange (this is where invalid_client likely occurs)
print("=" * 70)
print("STEP 2: Test Token Endpoint")
print("=" * 70)

token_endpoint = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# Test with a dummy code (will fail, but shows if client credentials are accepted)
test_data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': 'dummy_code_for_testing',
    'redirect_uri': REDIRECT_URI
}

print(f"Token Endpoint: {token_endpoint}")
print(f"Testing client credentials validity...")
print()

try:
    response = requests.post(token_endpoint, data=test_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print()
    
    if response.status_code == 400:
        error_data = response.json()
        error_code = error_data.get('error', 'unknown')
        error_desc = error_data.get('error_description', 'No description')
        
        if error_code == 'invalid_client':
            print("❌ ERROR: invalid_client")
            print()
            print("This means one of:")
            print("1. Client Secret is incorrect")
            print("2. Client ID doesn't exist")
            print("3. App not configured for multi-tenant (should be fixed)")
            print("4. Azure AD changes still propagating (wait 5-10 minutes)")
            print()
            print("🔧 SOLUTION:")
            print("1. Go to Azure Portal: https://portal.azure.com")
            print("2. App registrations → Your app")
            print("3. Certificates & secrets → Create NEW client secret")
            print("4. Copy the VALUE (not Secret ID)")
            print("5. Update .env.master: MICROSOFT_CLIENT_SECRET=<new_value>")
            print("6. Restart: BISTOP then BISTART")
            
        elif error_code == 'invalid_grant':
            print("✅ CLIENT CREDENTIALS ARE VALID!")
            print("(invalid_grant is expected with dummy code)")
            print()
            print("The OAuth flow should work. Try logging in again:")
            print("http://localhost:5001")
            
        else:
            print(f"❓ Unexpected error: {error_code}")
            print(f"Description: {error_desc}")
            
    else:
        print("❓ Unexpected status code")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

print()
print("=" * 70)
print("🎯 NEXT STEPS")
print("=" * 70)
print()
print("If you see 'invalid_client' above:")
print("→ Create a NEW client secret in Azure Portal")
print("→ Update .env.master with the new secret")
print("→ Restart Flask server")
print()
print("If you see 'invalid_grant' above:")
print("→ Client credentials are valid!")
print("→ Try the OAuth login flow again")
print()
