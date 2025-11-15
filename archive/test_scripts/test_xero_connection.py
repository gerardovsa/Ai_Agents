"""
Test Xero OAuth2 Connection - Authorization Code Flow

This script tests the Xero connection using the proper OAuth2 Authorization Code flow.
It will open a browser for you to log in to Xero and authorize the app.
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

@app.route('/callback')
def oauth_callback():
    """Handle OAuth2 callback from Xero"""
    global auth_code
    auth_code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"""
        <h1>❌ Authorization Failed</h1>
        <p>Error: {error}</p>
        <p>Description: {request.args.get('error_description', 'Unknown error')}</p>
        <p>You can close this window.</p>
        """
    
    if auth_code:
        auth_complete.set()
        return """
        <h1>✅ Authorization Successful!</h1>
        <p>You can close this window and return to the terminal.</p>
        <script>setTimeout(() => window.close(), 2000);</script>
        """
    
    return "<h1>❌ No authorization code received</h1>"


def test_xero_connection(business_id=1):
    """Test Xero connection for specified business"""
    
    print("=" * 70)
    print("XERO OAUTH2 CONNECTION TEST")
    print("=" * 70)
    
    config = BUSINESS_CONFIGS.get(business_id)
    if not config:
        print(f"❌ Invalid business_id: {business_id}")
        return
    
    print(f"\n📊 Testing: {config['name']} (Business {business_id})")
    print(f"   Client ID: {config['client_id'][:20]}...")
    print(f"   Client Secret: {config['client_secret'][:20]}...")
    
    # Check credentials
    if not config['client_id'] or not config['client_secret']:
        print("\n❌ Xero credentials not found in .env.master")
        print("   Make sure these variables are set:")
        print(f"   - XERO_{config['name'].upper().replace(' ', '_')}_CLIENT_ID")
        print(f"   - XERO_{config['name'].upper().replace(' ', '_')}_CLIENT_SECRET")
        return
    
    # Start callback server
    print("\n🚀 Starting OAuth callback server on http://localhost:8080...")
    server_thread = threading.Thread(
        target=lambda: app.run(port=8080, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)
    
    # Step 1: Generate authorization URL
    redirect_uri = "http://localhost:8080/callback"
    scopes = "offline_access accounting.transactions.read accounting.contacts.read accounting.settings.read"
    
    auth_url = (
        f"{XERO_AUTH_URL}?"
        f"response_type=code&"
        f"client_id={config['client_id']}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scopes}&"
        f"state=test123"
    )
    
    print("\n🔐 Step 1: Opening browser for Xero login...")
    print("   You will be asked to log in to Xero and authorize this app.")
    print("   After authorization, you'll be redirected back automatically.")
    print("\n   If browser doesn't open, copy this URL:")
    print(f"   {auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Wait for callback (timeout after 60 seconds)
    print("⏳ Waiting for authorization... (60 second timeout)")
    if not auth_complete.wait(timeout=60):
        print("\n❌ Timeout waiting for authorization")
        print("   Please try again and complete the authorization process.")
        return
    
    if not auth_code:
        print("\n❌ No authorization code received")
        return
    
    print("✅ Authorization code received!")
    
    # Step 2: Exchange code for tokens
    print("\n🔄 Step 2: Exchanging authorization code for access token...")
    
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
        expires_in = tokens.get('expires_in', 1800)
        
        print(f"✅ Access token received (expires in {expires_in} seconds)")
        if refresh_token:
            print(f"✅ Refresh token received (can be used to get new access tokens)")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Failed to get access token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return
    
    # Step 3: Get tenant/organization ID
    print("\n🏢 Step 3: Getting Xero organization (tenant) ID...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(XERO_CONNECTIONS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        connections = response.json()
        
        if not connections:
            print("❌ No Xero organizations found")
            print("   Make sure your Xero app is connected to at least one organization.")
            return
        
        print(f"✅ Found {len(connections)} connected organization(s):")
        for conn in connections:
            print(f"   - {conn['tenantName']} (ID: {conn['tenantId']})")
        
        tenant_id = connections[0]['tenantId']
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Failed to get tenant ID: {e}")
        return
    
    # Step 4: Test API call - Get invoices
    print(f"\n📄 Step 4: Testing API call - Fetching invoices...")
    
    headers['Xero-tenant-id'] = tenant_id
    
    try:
        response = requests.get(
            f"{XERO_INVOICES_URL}?page=1&pageSize=5",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        invoices = data.get('Invoices', [])
        print(f"✅ Successfully fetched {len(invoices)} invoices")
        
        if invoices:
            print("\n   Sample invoices:")
            for inv in invoices[:3]:
                inv_num = inv.get('InvoiceNumber', 'N/A')
                contact = inv.get('Contact', {}).get('Name', 'N/A')
                total = inv.get('Total', 0)
                status = inv.get('Status', 'N/A')
                print(f"   - Invoice #{inv_num}: {contact} - ${total:.2f} ({status})")
        else:
            print("   No invoices found (organization may be empty)")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Failed to fetch invoices: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return
    
    # Success summary
    print("\n" + "=" * 70)
    print("✅ CONNECTION TEST SUCCESSFUL!")
    print("=" * 70)
    print(f"\n✅ {config['name']} is properly connected to Xero")
    print(f"✅ Access token: {access_token[:30]}...")
    print(f"✅ Refresh token: {refresh_token[:30]}..." if refresh_token else "⚠️  No refresh token")
    print(f"✅ Tenant ID: {tenant_id}")
    print(f"✅ API calls working correctly")
    
    print("\n📝 NEXT STEPS:")
    print("   1. Store these tokens in your database for this user")
    print("   2. Use the refresh token to get new access tokens when they expire")
    print("   3. Update your AI agent to use Authorization Code flow instead of Client Credentials")
    print("\n   Token details:")
    print(f"   Access Token: {access_token}")
    print(f"   Refresh Token: {refresh_token}")
    print(f"   Tenant ID: {tenant_id}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\nWhich business would you like to test?")
    print("1. InHouse Print")
    print("2. InHouse Publishing")
    print("3. InHouse Signs")
    
    try:
        choice = input("\nEnter business number (1-3): ").strip()
        business_id = int(choice)
        
        if business_id not in [1, 2, 3]:
            print("Invalid choice. Please enter 1, 2, or 3.")
            sys.exit(1)
        
        test_xero_connection(business_id)
        
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
