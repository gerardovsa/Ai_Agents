"""
Test All Xero OAuth2 Connections - Automated Testing

This script automatically tests all 3 Xero business connections sequentially.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from flask import Flask, request
import webbrowser
import threading
import time

# Load environment variables
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

# Xero OAuth2 endpoints
XERO_AUTH_URL = "https://login.xero.com/identity/connect/authorize"
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_INVOICES_URL = "https://api.xero.com/api.xro/2.0/Invoices"

# Get credentials from .env.master
BUSINESS_CONFIGS = {
    1: {
        'name': 'InHouse Print',
        'client_id': os.getenv('XERO_PRINT_CLIENT_ID'),
        'client_secret': os.getenv('XERO_PRINT_CLIENT_SECRET')
    },
    2: {
        'name': 'InHouse Publishing',
        'client_id': os.getenv('XERO_PUB_CLIENT_ID'),
        'client_secret': os.getenv('XERO_PUB_CLIENT_SECRET')
    },
    3: {
        'name': 'InHouse Signs',
        'client_id': os.getenv('XERO_SIGNS_CLIENT_ID'),
        'client_secret': os.getenv('XERO_SIGNS_CLIENT_SECRET')
    }
}

# OAuth callback server
app = Flask(__name__)
auth_code = None
auth_complete = threading.Event()
server_started = False

@app.route('/callback')
def oauth_callback():
    """Handle OAuth2 callback from Xero"""
    global auth_code
    auth_code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        auth_complete.set()
        return f"""
        <html><body style="font-family: Arial, sans-serif; padding: 40px;">
        <h1 style="color: #d32f2f;">❌ Authorization Failed</h1>
        <p><strong>Error:</strong> {error}</p>
        <p><strong>Description:</strong> {request.args.get('error_description', 'Unknown error')}</p>
        <p style="margin-top: 30px; color: #666;">You can close this window and return to the terminal.</p>
        </body></html>
        """
    
    if auth_code:
        auth_complete.set()
        return """
        <html><body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
        <h1 style="color: #388e3c;">✅ Authorization Successful!</h1>
        <p style="font-size: 18px;">Authorization code received.</p>
        <p style="margin-top: 30px; color: #666;">You can close this window and return to the terminal.</p>
        <script>setTimeout(() => window.close(), 3000);</script>
        </body></html>
        """
    
    return "<html><body><h1>❌ No authorization code received</h1></body></html>"


def start_callback_server():
    """Start OAuth callback server"""
    global server_started
    if not server_started:
        server_thread = threading.Thread(
            target=lambda: app.run(port=8080, debug=False, use_reloader=False)
        )
        server_thread.daemon = True
        server_thread.start()
        time.sleep(1)
        server_started = True


def test_xero_connection(business_id):
    """Test Xero connection for specified business"""
    
    global auth_code, auth_complete
    auth_code = None
    auth_complete.clear()
    
    config = BUSINESS_CONFIGS.get(business_id)
    if not config:
        print(f"❌ Invalid business_id: {business_id}")
        return False
    
    print("\n" + "=" * 70)
    print(f"TESTING: {config['name']} (Business {business_id})")
    print("=" * 70)
    
    # Check credentials
    if not config['client_id'] or not config['client_secret']:
        print(f"❌ Xero credentials not found for {config['name']}")
        return False
    
    print(f"✅ Client ID found: {config['client_id'][:20]}...")
    print(f"✅ Client Secret found: {config['client_secret'][:20]}...")
    
    # Generate authorization URL
    redirect_uri = "http://localhost:8080/callback"
    scopes = "offline_access accounting.transactions.read accounting.contacts.read accounting.settings.read"
    
    auth_url = (
        f"{XERO_AUTH_URL}?"
        f"response_type=code&"
        f"client_id={config['client_id']}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scopes}&"
        f"state=business_{business_id}"
    )
    
    print(f"\n🔐 Opening browser for Xero login...")
    print(f"   Please log in and authorize access for {config['name']}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Wait for callback
    print("⏳ Waiting for authorization... (60 second timeout)")
    if not auth_complete.wait(timeout=60):
        print("❌ Timeout - No response from Xero")
        return False
    
    if not auth_code:
        print("❌ No authorization code received")
        return False
    
    print("✅ Authorization code received")
    
    # Exchange code for tokens
    print("🔄 Exchanging code for access token...")
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': config['client_id'],
        'client_secret': config['client_secret']
    }
    
    try:
        response = requests.post(XERO_TOKEN_URL, data=token_data, timeout=10)
        response.raise_for_status()
        tokens = response.json()
        
        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token')
        
        print(f"✅ Access token received")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get access token: {e}")
        return False
    
    # Get tenant ID
    print("🏢 Getting organization ID...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(XERO_CONNECTIONS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        connections = response.json()
        
        if not connections:
            print("❌ No organizations found")
            return False
        
        print(f"✅ Found {len(connections)} organization(s)")
        for conn in connections:
            print(f"   - {conn['tenantName']}")
        
        tenant_id = connections[0]['tenantId']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get organizations: {e}")
        return False
    
    # Test API call
    print("📄 Testing API - Fetching invoices...")
    
    headers['Xero-tenant-id'] = tenant_id
    
    try:
        response = requests.get(
            f"{XERO_INVOICES_URL}?page=1&pageSize=3",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        invoices = data.get('Invoices', [])
        print(f"✅ Successfully fetched {len(invoices)} invoices")
        
        if invoices:
            for inv in invoices:
                inv_num = inv.get('InvoiceNumber', 'N/A')
                contact = inv.get('Contact', {}).get('Name', 'N/A')
                total = inv.get('Total', 0)
                status = inv.get('Status', 'N/A')
                print(f"   • Invoice #{inv_num}: {contact} - ${total:.2f} ({status})")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch invoices: {e}")
        return False
    
    # Success
    print(f"\n✅ {config['name']} - CONNECTION SUCCESSFUL!")
    print(f"   Tenant ID: {tenant_id}")
    print(f"   Access Token: {access_token[:40]}...")
    if refresh_token:
        print(f"   Refresh Token: {refresh_token[:40]}...")
    
    return True


def main():
    """Test all three Xero connections"""
    
    print("\n" + "=" * 70)
    print("XERO CONNECTION TEST - ALL BUSINESSES")
    print("=" * 70)
    print("\nThis will test connections for:")
    print("  1. InHouse Print")
    print("  2. InHouse Publishing")
    print("  3. InHouse Signs")
    print("\nYou will need to authorize each one in your browser.")
    print("=" * 70)
    
    input("\nPress ENTER to start testing...")
    
    # Start callback server
    print("\n🚀 Starting OAuth callback server on http://localhost:8080...")
    start_callback_server()
    
    results = {}
    
    # Test each business
    for business_id in [1, 2, 3]:
        success = test_xero_connection(business_id)
        results[business_id] = success
        
        if business_id < 3 and success:
            print(f"\n{'='*70}")
            input("Press ENTER to test next business...")
    
    # Final summary
    print("\n\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    for business_id, config in BUSINESS_CONFIGS.items():
        status = "✅ PASSED" if results.get(business_id) else "❌ FAILED"
        print(f"{status} - {config['name']}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("=" * 70)
    print(f"Total: {passed}/{total} connections successful")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All Xero connections are working!")
        print("\n📝 Next steps:")
        print("   1. Store the access/refresh tokens in your database")
        print("   2. Update xero_routes.py to use Authorization Code flow")
        print("   3. Implement token refresh logic in your AI agent")
    else:
        print("\n⚠️  Some connections failed. Please check the errors above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
