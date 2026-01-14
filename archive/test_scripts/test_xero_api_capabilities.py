"""
Test Xero API Capabilities - What Can We Access?

Tests all available API endpoints with your current credentials
to determine exact permissions and available operations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

# Load environment variables
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

# Xero endpoints
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_BASE_URL = "https://api.xero.com/api.xro/2.0"

# Test business (InHouse Print)
CLIENT_ID = os.getenv('XERO_PRINT_CLIENT_ID')
CLIENT_SECRET = os.getenv('XERO_PRINT_CLIENT_SECRET')


def get_access_token():
    """Get access token using Client Credentials"""
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(XERO_TOKEN_URL, data=payload, timeout=10)
    response.raise_for_status()
    return response.json()['access_token']


def get_tenant_id(access_token):
    """Get Xero tenant ID"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(XERO_CONNECTIONS_URL, headers=headers, timeout=10)
    response.raise_for_status()
    connections = response.json()
    return connections[0]['tenantId']


def test_endpoint(access_token, tenant_id, endpoint, method='GET', description=''):
    """Test a specific API endpoint"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': tenant_id,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    url = f"{XERO_BASE_URL}/{endpoint}"
    
    try:
        response = requests.request(method, url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return True, f"✅ {description}", data
            except:
                # XML response
                return True, f"✅ {description} (XML format)", None
        elif response.status_code == 403:
            return False, f"❌ {description} - FORBIDDEN (no permission)", None
        elif response.status_code == 404:
            return False, f"❌ {description} - NOT FOUND", None
        else:
            return False, f"❌ {description} - HTTP {response.status_code}", None
            
    except Exception as e:
        return False, f"❌ {description} - ERROR: {str(e)}", None


def main():
    """Test all Xero API capabilities"""
    
    print("=" * 70)
    print("XERO API CAPABILITIES TEST")
    print("Testing what endpoints are accessible with current credentials")
    print("=" * 70)
    
    # Get authentication
    print("\n[1/3] Getting access token...")
    access_token = get_access_token()
    print("✅ Access token obtained")
    
    print("\n[2/3] Getting tenant ID...")
    tenant_id = get_tenant_id(access_token)
    print(f"✅ Tenant ID: {tenant_id}")
    
    print("\n[3/3] Testing API endpoints...")
    print("=" * 70)
    
    # Define all possible endpoints to test
    endpoints = [
        # INVOICES & SALES
        ("Invoices", "GET", "List invoices"),
        ("Invoices?page=1", "GET", "List invoices with pagination"),
        ("Invoices?where=Type==\"ACCREC\"", "GET", "Filter invoices (receivable)"),
        ("CreditNotes", "GET", "List credit notes"),
        ("Prepayments", "GET", "List prepayments"),
        ("Overpayments", "GET", "List overpayments"),
        ("RepeatingInvoices", "GET", "List repeating invoices"),
        
        # CONTACTS & CUSTOMERS
        ("Contacts", "GET", "List contacts/customers"),
        ("Contacts?where=IsCustomer==true", "GET", "Filter contacts (customers only)"),
        ("ContactGroups", "GET", "List contact groups"),
        
        # ACCOUNTS & GENERAL LEDGER
        ("Accounts", "GET", "List chart of accounts"),
        ("Journals", "GET", "List journal entries"),
        ("ManualJournals", "GET", "List manual journals"),
        ("TrackingCategories", "GET", "List tracking categories"),
        
        # PAYMENTS & BANKING
        ("Payments", "GET", "List payments"),
        ("BankTransactions", "GET", "List bank transactions"),
        ("BankTransfers", "GET", "List bank transfers"),
        ("BatchPayments", "GET", "List batch payments"),
        
        # PURCHASE ORDERS & BILLS
        ("PurchaseOrders", "GET", "List purchase orders"),
        
        # QUOTES & ESTIMATES
        ("Quotes", "GET", "List quotes"),
        
        # ITEMS & INVENTORY
        ("Items", "GET", "List items/products"),
        
        # EMPLOYEES & USERS
        ("Employees", "GET", "List employees"),
        ("Users", "GET", "List users"),
        
        # TAX & CURRENCIES
        ("TaxRates", "GET", "List tax rates"),
        ("Currencies", "GET", "List currencies"),
        
        # ORGANIZATION & SETTINGS
        ("Organisation", "GET", "Get organization details"),
        ("BrandingThemes", "GET", "List branding themes"),
        
        # REPORTS
        ("Reports/ProfitAndLoss", "GET", "Profit & Loss report"),
        ("Reports/BalanceSheet", "GET", "Balance Sheet report"),
        ("Reports/TrialBalance", "GET", "Trial Balance report"),
        ("Reports/BankSummary", "GET", "Bank Summary report"),
        ("Reports/AgedReceivablesByContact", "GET", "Aged Receivables report"),
        ("Reports/AgedPayablesByContact", "GET", "Aged Payables report"),
        ("Reports/ExecutiveSummary", "GET", "Executive Summary report"),
        ("Reports/BudgetSummary", "GET", "Budget Summary report"),
    ]
    
    # Test each endpoint
    results = {
        'accessible': [],
        'forbidden': [],
        'not_found': [],
        'error': []
    }
    
    for endpoint, method, description in endpoints:
        success, message, data = test_endpoint(access_token, tenant_id, endpoint, method, description)
        
        print(f"\n{message}")
        print(f"   Endpoint: {method} {endpoint}")
        
        if success:
            results['accessible'].append((endpoint, description))
            # Show sample data for some endpoints
            if data and endpoint in ['Invoices', 'Contacts', 'Accounts', 'Organisation']:
                if endpoint == 'Organisation':
                    org_name = data.get('Organisations', [{}])[0].get('Name', 'N/A')
                    print(f"   Organization: {org_name}")
                elif 'Invoices' in data:
                    count = len(data.get('Invoices', []))
                    print(f"   Found: {count} invoices")
                elif 'Contacts' in data:
                    count = len(data.get('Contacts', []))
                    print(f"   Found: {count} contacts")
                elif 'Accounts' in data:
                    count = len(data.get('Accounts', []))
                    print(f"   Found: {count} accounts")
        elif 'FORBIDDEN' in message:
            results['forbidden'].append((endpoint, description))
        elif 'NOT FOUND' in message:
            results['not_found'].append((endpoint, description))
        else:
            results['error'].append((endpoint, description))
    
    # Summary
    print("\n\n" + "=" * 70)
    print("SUMMARY - ACCESSIBLE ENDPOINTS")
    print("=" * 70)
    
    print(f"\n✅ ACCESSIBLE ({len(results['accessible'])} endpoints):")
    print("-" * 70)
    for endpoint, desc in results['accessible']:
        print(f"   • {desc}")
        print(f"     GET {XERO_BASE_URL}/{endpoint}")
    
    if results['forbidden']:
        print(f"\n❌ FORBIDDEN - No Permission ({len(results['forbidden'])} endpoints):")
        print("-" * 70)
        for endpoint, desc in results['forbidden']:
            print(f"   • {desc}")
    
    if results['not_found']:
        print(f"\n⚠️  NOT FOUND ({len(results['not_found'])} endpoints):")
        print("-" * 70)
        for endpoint, desc in results['not_found']:
            print(f"   • {desc}")
    
    if results['error']:
        print(f"\n❌ ERRORS ({len(results['error'])} endpoints):")
        print("-" * 70)
        for endpoint, desc in results['error']:
            print(f"   • {desc}")
    
    # Generate capabilities document
    print("\n\n" + "=" * 70)
    print("AVAILABLE API OPERATIONS")
    print("=" * 70)
    
    categories = {
        'Invoices': ['Invoices', 'CreditNotes', 'Prepayments', 'Overpayments', 'RepeatingInvoices'],
        'Contacts': ['Contacts', 'ContactGroups'],
        'Accounts': ['Accounts', 'Journals', 'ManualJournals', 'TrackingCategories'],
        'Banking': ['Payments', 'BankTransactions', 'BankTransfers', 'BatchPayments'],
        'Purchasing': ['PurchaseOrders'],
        'Sales': ['Quotes'],
        'Inventory': ['Items'],
        'HR': ['Employees', 'Users'],
        'Settings': ['TaxRates', 'Currencies', 'Organisation', 'BrandingThemes'],
        'Reports': ['Reports/']
    }
    
    for category, keywords in categories.items():
        category_endpoints = [
            (endpoint, desc) for endpoint, desc in results['accessible']
            if any(keyword in endpoint for keyword in keywords)
        ]
        
        if category_endpoints:
            print(f"\n📊 {category.upper()} ({len(category_endpoints)} operations)")
            print("-" * 70)
            for endpoint, desc in category_endpoints:
                print(f"   • {desc}")
    
    print("\n" + "=" * 70)
    print(f"TOTAL: {len(results['accessible'])} API endpoints accessible")
    print("=" * 70)
    
    print("\n📝 NEXT STEPS:")
    print("   1. Review accessible endpoints above")
    print("   2. Implement these as AI agent tools")
    print("   3. Update xero_tools.json schema")
    print("   4. Add tool implementations in xero module")
    
    # Save results to file
    output_file = Path(__file__).parent / 'XERO_API_CAPABILITIES_RESULTS.json'
    with open(output_file, 'w') as f:
        json.dump({
            'accessible': results['accessible'],
            'forbidden': results['forbidden'],
            'not_found': results['not_found'],
            'error': results['error'],
            'total_accessible': len(results['accessible']),
            'tenant_id': tenant_id
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
