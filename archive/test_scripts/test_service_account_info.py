"""Check service account configuration"""

import os
import json

print("="*70)
print("Service Account Configuration Check")
print("="*70)

# Check environment variable
sa_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
if sa_json:
    print("\n✅ GOOGLE_SERVICE_ACCOUNT_JSON environment variable is set")
    try:
        sa_data = json.loads(sa_json)
        print(f"   Project ID: {sa_data.get('project_id', 'N/A')}")
        print(f"   Client Email: {sa_data.get('client_email', 'N/A')}")
        print(f"   Type: {sa_data.get('type', 'N/A')}")
        
        # Check scopes (not in JSON, but we can see what's configured)
        print("\n📋 Service Account Details:")
        print(f"   Private key: {'SET' if sa_data.get('private_key') else 'NOT SET'}")
        print(f"   Private key ID: {sa_data.get('private_key_id', 'N/A')[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Error parsing JSON: {e}")
else:
    print("\n❌ GOOGLE_SERVICE_ACCOUNT_JSON not set")

# Check if service account file exists
sa_file_path = 'google_workspace/service-account.json'
if os.path.exists(sa_file_path):
    print(f"\n✅ Service account file exists: {sa_file_path}")
    with open(sa_file_path, 'r') as f:
        sa_data = json.load(f)
        print(f"   Project ID: {sa_data.get('project_id', 'N/A')}")
        print(f"   Client Email: {sa_data.get('client_email', 'N/A')}")
else:
    print(f"\n⚠️  Service account file not found: {sa_file_path}")

print("\n" + "="*70)
print("IMPORTANT: Google Forms API Permissions")
print("="*70)
print("""
Google Forms API requires DOMAIN-WIDE DELEGATION for service accounts!

To fix HTTP 500 errors:
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Click on your service account
3. Under "Domain-wide delegation" → ENABLE IT
4. Add OAuth scopes:
   - https://www.googleapis.com/auth/forms.body
   - https://www.googleapis.com/auth/forms.responses.readonly
   - https://www.googleapis.com/auth/drive

Alternatively: Use OAuth user credentials instead of service account
for Google Forms (Forms API doesn't work well with service accounts)
""")
print("="*70)
