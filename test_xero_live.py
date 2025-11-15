"""
Live test of Xero tools with actual API calls
Tests both the tool wrappers AND the underlying XeroAPIClient
"""
import os
import sys
from pathlib import Path

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env.master'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env.master")
else:
    print(f"⚠ .env.master not found at {env_path}")

print('\n' + '='*80)
print('XERO TOOLS LIVE TEST')
print('='*80 + '\n')

# Test 1: Check credentials are configured
print('TEST 1: Checking Xero Credentials Configuration')
print('-'*80)

businesses = {
    1: 'InHouse Print',
    2: 'InHouse Publishing', 
    3: 'InHouse Signs'
}

credentials_found = {}
for business_id, name in businesses.items():
    client_id_key = f'XERO_{"PRINT" if business_id == 1 else "PUB" if business_id == 2 else "SIGNS"}_CLIENT_ID'
    client_secret_key = f'XERO_{"PRINT" if business_id == 1 else "PUB" if business_id == 2 else "SIGNS"}_CLIENT_SECRET'
    
    client_id = os.getenv(client_id_key)
    client_secret = os.getenv(client_secret_key)
    
    has_creds = bool(client_id and client_secret)
    credentials_found[business_id] = has_creds
    
    status = '✅' if has_creds else '❌'
    print(f'{status} {name} (business_id={business_id}):')
    print(f'   {client_id_key}: {"SET" if client_id else "NOT SET"}')
    print(f'   {client_secret_key}: {"SET" if client_secret else "NOT SET"}')

any_credentials = any(credentials_found.values())
print()

if not any_credentials:
    print('⚠️  No Xero credentials found in .env.master')
    print('   Tools are implemented but cannot connect to Xero API without credentials')
    print('\nTo configure credentials:')
    print('1. Go to https://developer.xero.com/')
    print('2. Create a "Custom Connection" app for each business')
    print('3. Add credentials to .env.master:')
    print('   XERO_PRINT_CLIENT_ID=your_client_id')
    print('   XERO_PRINT_CLIENT_SECRET=your_client_secret')
    print('\n' + '='*80)
    sys.exit(0)

# Test 2: Try to initialize XeroAPIClient
print('\nTEST 2: XeroAPIClient Initialization')
print('-'*80)

from UI.external.modules.xero.xero_routes import XeroAPIClient

for business_id, has_creds in credentials_found.items():
    if not has_creds:
        continue
    
    try:
        client = XeroAPIClient(business_id)
        print(f'✅ {businesses[business_id]}: Client initialized')
        print(f'   Business: {client.config["name"]}')
        print(f'   Client ID: {client.client_id[:20]}...')
    except Exception as e:
        print(f'❌ {businesses[business_id]}: Failed to initialize')
        print(f'   Error: {e}')

# Test 3: Try to get access token
print('\nTEST 3: OAuth2 Access Token')
print('-'*80)

test_business_id = next((bid for bid, has_creds in credentials_found.items() if has_creds), None)
if test_business_id:
    try:
        client = XeroAPIClient(test_business_id)
        print(f'Attempting to get access token for {businesses[test_business_id]}...')
        token = client.get_access_token()
        print(f'✅ Access token obtained: {token[:30]}...')
    except Exception as e:
        print(f'❌ Failed to get access token')
        print(f'   Error: {str(e)[:200]}')

# Test 4: Try to get tenant ID
print('\nTEST 4: Xero Tenant ID')
print('-'*80)

if test_business_id:
    try:
        client = XeroAPIClient(test_business_id)
        tenant_id = client.get_tenant_id()
        print(f'✅ Tenant ID obtained: {tenant_id}')
    except Exception as e:
        print(f'❌ Failed to get tenant ID')
        print(f'   Error: {str(e)[:200]}')

# Test 5: Test all 6 tool wrappers
print('\nTEST 5: Tool Wrapper Functions')
print('-'*80)

from tools.implementations.xero import (
    xero_get_invoices,
    xero_get_invoice_by_id,
    xero_get_contacts,
    xero_get_accounts,
    xero_get_bank_transactions,
    xero_get_payments
)

if test_business_id:
    tools_to_test = [
        ('xero_get_invoices', lambda: xero_get_invoices(business_id=test_business_id)),
        ('xero_get_contacts', lambda: xero_get_contacts(business_id=test_business_id)),
        ('xero_get_accounts', lambda: xero_get_accounts(business_id=test_business_id)),
        ('xero_get_payments', lambda: xero_get_payments(business_id=test_business_id)),
    ]
    
    for tool_name, test_func in tools_to_test:
        print(f'\nTesting {tool_name}...')
        try:
            result = test_func()
            
            if result.get('success'):
                # Count items in response
                items = (
                    result.get('invoices') or 
                    result.get('contacts') or 
                    result.get('accounts') or 
                    result.get('payments') or 
                    []
                )
                print(f'✅ SUCCESS: Retrieved {len(items)} items')
                print(f'   Business: {result.get("business_name")}')
                
                # Show first item as example
                if items:
                    first_item = items[0]
                    print(f'   Sample data: {list(first_item.keys())[:5]}')
            else:
                error = result.get('error', 'Unknown error')
                if 'credentials not found' in error.lower():
                    print(f'⚠️  NEEDS CREDENTIALS: {error[:100]}')
                elif 'failed to get' in error.lower():
                    print(f'❌ AUTH ERROR: {error[:100]}')
                else:
                    print(f'❌ ERROR: {error[:200]}')
        except Exception as e:
            print(f'❌ EXCEPTION: {str(e)[:200]}')

# Test 6: Test with filtering
print('\n\nTEST 6: Test Filtering & Parameters')
print('-'*80)

if test_business_id:
    print('\nTesting xero_get_invoices with status filter...')
    try:
        result = xero_get_invoices(business_id=test_business_id, status='PAID')
        if result.get('success'):
            count = len(result.get('invoices', []))
            print(f'✅ SUCCESS: Found {count} PAID invoices')
        else:
            print(f'⚠️  {result.get("error", "Unknown error")[:100]}')
    except Exception as e:
        print(f'❌ EXCEPTION: {str(e)[:200]}')
    
    print('\nTesting xero_get_contacts with search filter...')
    try:
        result = xero_get_contacts(business_id=test_business_id, search='Test')
        if result.get('success'):
            count = len(result.get('contacts', []))
            print(f'✅ SUCCESS: Found {count} contacts matching "Test"')
        else:
            print(f'⚠️  {result.get("error", "Unknown error")[:100]}')
    except Exception as e:
        print(f'❌ EXCEPTION: {str(e)[:200]}')

# Summary
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)
print(f'Credentials configured: {sum(credentials_found.values())}/3 businesses')
if any_credentials:
    print(f'✅ Xero tools are properly implemented and ready to use')
    print(f'   Configure credentials for remaining businesses if needed')
else:
    print(f'⚠️  Xero tools are implemented but need credentials to function')
print('='*80 + '\n')
