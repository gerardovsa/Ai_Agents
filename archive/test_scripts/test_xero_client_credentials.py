"""
Test Xero Client Credentials Flow - Direct Token Request
Mimics the VB.NET code: Client.RequestClientCredentialsTokenAsync()
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

# Load environment variables
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

# Xero OAuth2 endpoint
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_INVOICES_URL = "https://api.xero.com/api.xro/2.0/Invoices"

# Business configurations
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


def test_client_credentials(business_id):
    """Test Client Credentials flow (mimics VB.NET code)"""
    
    config = BUSINESS_CONFIGS[business_id]
    
    print("=" * 70)
    print(f"Testing: {config['name']} (Business {business_id})")
    print("=" * 70)
    
    # Step 1: Verify credentials loaded
    print("\n[STEP 1] Checking credentials...")
    print(f"   Client ID: {config['client_id']}")
    print(f"   Client Secret: {config['client_secret'][:20]}...{config['client_secret'][-10:]}")
    
    if not config['client_id'] or not config['client_secret']:
        print("   ❌ FAILED - Credentials not found")
        return False
    print("   ✅ Credentials loaded")
    
    # Step 2: Request Client Credentials Token (like VB.NET RequestClientCredentialsTokenAsync)
    print("\n[STEP 2] Requesting access token (Client Credentials flow)...")
    print(f"   POST {XERO_TOKEN_URL}")
    
    # Prepare request - EXACTLY like VB.NET XeroClient does
    # Try different scope formats - Client Credentials may not need scopes at all!
    payload = {
        'grant_type': 'client_credentials',
        'client_id': config['client_id'],
        'client_secret': config['client_secret']
        # NO SCOPE - Custom connections/Private apps don't use scopes
    }
    
    print(f"   Payload:")
    print(f"      grant_type: client_credentials")
    print(f"      client_id: {config['client_id']}")
    print(f"      client_secret: {config['client_secret'][:10]}...")
    print(f"      scope: (none - Custom connection doesn't require scopes)")
    
    try:
        response = requests.post(
            XERO_TOKEN_URL,
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        print(f"\n   Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ FAILED - HTTP {response.status_code}")
            print(f"\n   Response Body:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            
            # Diagnose the error
            print("\n[DIAGNOSIS]")
            if response.status_code == 400:
                print("   400 Bad Request - Common causes:")
                print("   1. App is NOT configured for Client Credentials flow")
                print("      → Check Xero Developer Portal: Integration type should be 'Custom connection'")
                print("   2. Client ID or Secret is wrong")
                print("      → Verify credentials match exactly with Xero Developer Portal")
                print("   3. App is not connected to any organizations")
                print("      → Check Xero Settings → Connected Apps")
                print("   4. Scopes are invalid for Client Credentials")
                print("      → Client Credentials only supports specific scopes")
            elif response.status_code == 401:
                print("   401 Unauthorized - Invalid credentials")
                print("      → Client ID or Secret is incorrect")
            
            return False
        
        # Success!
        tokens = response.json()
        access_token = tokens.get('access_token')
        expires_in = tokens.get('expires_in', 1800)
        token_type = tokens.get('token_type', 'Bearer')
        
        print(f"   ✅ SUCCESS - Access token received!")
        print(f"      Token type: {token_type}")
        print(f"      Expires in: {expires_in} seconds ({expires_in//60} minutes)")
        print(f"      Access token: {access_token[:50]}...")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED - Network error: {e}")
        return False
    
    # Step 3: Get tenant/organization ID
    print("\n[STEP 3] Getting Xero organization (tenant) ID...")
    print(f"   GET {XERO_CONNECTIONS_URL}")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(XERO_CONNECTIONS_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ FAILED - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        connections = response.json()
        
        if not connections:
            print("   ❌ FAILED - No organizations connected")
            print("   → Go to Xero Settings → Connected Apps and connect your app")
            return False
        
        print(f"   ✅ Found {len(connections)} organization(s):")
        for conn in connections:
            print(f"      - {conn['tenantName']} (ID: {conn['tenantId']})")
            print(f"        Type: {conn['tenantType']}")
        
        tenant_id = connections[0]['tenantId']
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED - Network error: {e}")
        return False
    
    # Step 4: Test API call - Get invoices
    print("\n[STEP 4] Testing Accounting API - Fetching invoices...")
    print(f"   GET {XERO_INVOICES_URL}?page=1&pageSize=5")
    
    headers['Xero-tenant-id'] = tenant_id
    
    try:
        response = requests.get(
            f"{XERO_INVOICES_URL}?page=1&pageSize=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"   ❌ FAILED - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        try:
            data = response.json()
        except:
            print(f"   ⚠️  Response is not JSON: {response.text[:200]}")
            # Still count as success if we got HTTP 200
            print(f"   ✅ But API is accessible (HTTP 200)")
            return True
        
        invoices = data.get('Invoices', [])
        
        print(f"   ✅ Successfully fetched {len(invoices)} invoices")
        
        if invoices:
            print("\n   Sample invoices:")
            for inv in invoices[:3]:
                inv_num = inv.get('InvoiceNumber', 'N/A')
                contact = inv.get('Contact', {}).get('Name', 'N/A')
                total = inv.get('Total', 0)
                status = inv.get('Status', 'N/A')
                date = inv.get('Date', 'N/A')
                print(f"      • {date} - Invoice #{inv_num}")
                print(f"        {contact} - ${total:.2f} ({status})")
        else:
            print("   ℹ️  No invoices found (organization may be empty)")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED - Network error: {e}")
        return False
    
    # Success!
    print("\n" + "=" * 70)
    print(f"✅ {config['name']} - ALL TESTS PASSED!")
    print("=" * 70)
    print(f"\nConnection Details:")
    print(f"   Access Token: {access_token}")
    print(f"   Tenant ID: {tenant_id}")
    print(f"   Expires: {expires_in} seconds")
    print("\n" + "=" * 70)
    
    return True


def main():
    """Test all three businesses"""
    
    print("\n" + "=" * 70)
    print("XERO CLIENT CREDENTIALS FLOW TEST")
    print("Testing like VB.NET: RequestClientCredentialsTokenAsync()")
    print("=" * 70)
    
    results = {}
    
    for business_id in [1, 2, 3]:
        success = test_client_credentials(business_id)
        results[business_id] = success
        print("\n")
        
        if not success:
            print(f"⚠️  Stopping tests - {BUSINESS_CONFIGS[business_id]['name']} failed")
            break
    
    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    for business_id, config in BUSINESS_CONFIGS.items():
        if business_id in results:
            status = "✅ PASSED" if results[business_id] else "❌ FAILED"
            print(f"   {status} - {config['name']}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} connections successful")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All Xero connections working with Client Credentials!")
        print("\nYour VB.NET code pattern is correct:")
        print("   XeroConfig.ClientId = PubClientId")
        print("   XeroConfig.ClientSecret = PubClientSecret")
        print("   Client = New XeroClient(XeroConfig)")
        print("   xeroToken = Client.RequestClientCredentialsTokenAsync()")
        print("\nThe Python implementation in xero_routes.py should work too!")
    else:
        print("\n⚠️  Some connections failed.")
        print("\nNext steps:")
        print("   1. Check Xero Developer Portal app configuration")
        print("   2. Verify app is 'Custom connection' type")
        print("   3. Ensure app is connected to organizations")
        print("   4. Verify Client ID and Secret match exactly")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
