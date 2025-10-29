"""
Check Flask Environment Variables
==================================

Verifies what environment variables Flask is actually seeing at runtime.
"""

import requests
import json

try:
    # Check if Flask is running
    response = requests.get('http://localhost:5001/health', timeout=5)
    print("✅ Flask is running")
    print()
except:
    print("❌ Flask is not running. Start with: BISTART")
    exit(1)

# Test endpoint to check Microsoft config
print("=" * 70)
print("🔍 CHECKING FLASK ENVIRONMENT VARIABLES")
print("=" * 70)
print()

# We'll need to add a debug endpoint, but first let's check what the OAuth manager sees
print("Checking Microsoft OAuth configuration in Flask...")
print()

# Make a request to the login endpoint and capture the logs
try:
    # This will fail but we can see the logs in Flask console
    response = requests.get('http://localhost:5001/api/auth/microsoft/login', 
                           allow_redirects=False,
                           timeout=5)
    
    if response.status_code == 302:  # Redirect to Microsoft
        redirect_url = response.headers.get('Location', '')
        print(f"✅ Flask generated redirect URL:")
        print(f"   {redirect_url[:100]}...")
        print()
        
        # Parse client_id from URL
        if 'client_id=' in redirect_url:
            client_id_start = redirect_url.index('client_id=') + 10
            client_id_end = redirect_url.index('&', client_id_start)
            client_id = redirect_url[client_id_start:client_id_end]
            print(f"📋 Client ID in URL: {client_id}")
            print(f"📋 Expected:        324f7fef-50ac-4948-9f34-5f95b03ad818")
            print()
            
            if client_id == '324f7fef-50ac-4948-9f34-5f95b03ad818':
                print("✅ Client ID matches!")
            else:
                print("❌ Client ID MISMATCH!")
                print()
                print("This means Flask is loading a different MICROSOFT_CLIENT_ID")
                print("Check .env.master file and Flask startup logs")
        
        # Check tenant
        if '/common/' in redirect_url:
            print("✅ Using multi-tenant endpoint (/common/)")
        elif '/organizations/' in redirect_url:
            print("✅ Using organizations endpoint (/organizations/)")
        else:
            print("⚠️ Using specific tenant endpoint (should be /common/)")
            
    elif response.status_code == 400:
        error_data = response.json()
        if 'setup_required' in error_data:
            print("❌ Microsoft credentials not configured in Flask")
            print(error_data.get('error', 'Unknown error'))
        else:
            print(f"❌ Error: {error_data}")
            
    else:
        print(f"❓ Unexpected status: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Request failed: {e}")

print()
print("=" * 70)
print("💡 CHECK FLASK CONSOLE LOGS")
print("=" * 70)
print()
print("The Flask console should show:")
print("  🔷 Client ID being used: 324f7fef-50ac-4948-9f34-5f95b03ad818")
print("  🔷 Tenant ID: common")
print()
print("If you see different values, Flask is loading wrong .env file!")
print()
