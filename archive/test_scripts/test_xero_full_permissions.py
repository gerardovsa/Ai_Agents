"""
Test ALL Xero Scopes from Authorization Screenshot

Based on your Xero app scopes:
- accounting.contacts.read ✓
- accounting.reports.tenninetynine.read ✓
- accounting.reports.read ✓
- accounting.transactions.read ✓
- projects.read ✓
- assets.read ✓
- accounting.contacts ✓
- files.read ✓
- accounting.attachments ✓
- accounting.attachments.read ✓
- assets ✓
- projects ✓
- accounting.transactions ✓
- accounting.budgets.read ✓
- accounting.journals.read ✓
- files ✓
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
XERO_ACCOUNTING_BASE = "https://api.xero.com/api.xro/2.0"
XERO_ASSETS_BASE = "https://api.xero.com/assets.xro/1.0"
XERO_FILES_BASE = "https://api.xero.com/files.xro/1.0"
XERO_PROJECTS_BASE = "https://api.xero.com/projects.xro/2.0"

# Test business
CLIENT_ID = os.getenv('XERO_PRINT_CLIENT_ID')
CLIENT_SECRET = os.getenv('XERO_PRINT_CLIENT_SECRET')


def get_access_token():
    """Get access token"""
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(XERO_TOKEN_URL, data=payload, timeout=10)
    response.raise_for_status()
    return response.json()['access_token']


def get_tenant_id(access_token):
    """Get tenant ID"""
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    response = requests.get(XERO_CONNECTIONS_URL, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()[0]['tenantId']


def test_endpoint(access_token, tenant_id, base_url, endpoint, description):
    """Test endpoint"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': tenant_id,
        'Accept': 'application/json'
    }
    
    url = f"{base_url}/{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Get count if possible
                count = 0
                for key in data:
                    if isinstance(data[key], list):
                        count = len(data[key])
                        break
                return True, count
            except:
                return True, 0
        elif response.status_code == 403:
            return False, "FORBIDDEN"
        elif response.status_code == 401:
            return False, "UNAUTHORIZED"
        elif response.status_code == 404:
            return False, "NOT FOUND"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"ERROR: {str(e)[:50]}"


def main():
    print("=" * 70)
    print("XERO FULL PERMISSIONS TEST")
    print("Testing ALL scopes from your Xero app authorization")
    print("=" * 70)
    
    # Get auth
    print("\n[AUTH] Getting access token...")
    access_token = get_access_token()
    tenant_id = get_tenant_id(access_token)
    print(f"✅ Connected to: InHouse Print & Design Pty Ltd")
    
    # Test all endpoints by scope category
    results = {}
    
    print("\n" + "=" * 70)
    print("TESTING: ACCOUNTING.TRANSACTIONS.READ")
    print("=" * 70)
    
    accounting_transactions = [
        ("Invoices", "Invoices (sales invoices)"),
        ("CreditNotes", "Credit notes"),
        ("Prepayments", "Prepayments"),
        ("Overpayments", "Overpayments"),
        ("BankTransactions", "Bank transactions"),
        ("BankTransfers", "Bank transfers"),
        ("Payments", "Payments"),
        ("PurchaseOrders", "Purchase orders"),
        ("Quotes", "Quotes"),
        ("RepeatingInvoices", "Repeating invoices"),
        ("BatchPayments", "Batch payments"),
        ("LinkedTransactions", "Linked transactions"),
    ]
    
    for endpoint, desc in accounting_transactions:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[desc] = success
    
    print("\n" + "=" * 70)
    print("TESTING: ACCOUNTING.CONTACTS.READ / ACCOUNTING.CONTACTS")
    print("=" * 70)
    
    accounting_contacts = [
        ("Contacts", "Contacts"),
        ("ContactGroups", "Contact groups"),
    ]
    
    for endpoint, desc in accounting_contacts:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[desc] = success
    
    print("\n" + "=" * 70)
    print("TESTING: ACCOUNTING.REPORTS.READ")
    print("=" * 70)
    
    reports = [
        ("Reports/ProfitAndLoss", "Profit & Loss"),
        ("Reports/BalanceSheet", "Balance Sheet"),
        ("Reports/TrialBalance", "Trial Balance"),
        ("Reports/BankSummary", "Bank Summary"),
        ("Reports/ExecutiveSummary", "Executive Summary"),
        ("Reports/BudgetSummary", "Budget Summary"),
        ("Reports/AgedReceivablesByContact", "Aged Receivables by Contact"),
        ("Reports/AgedPayablesByContact", "Aged Payables by Contact"),
        ("Reports/TenNinetyNine", "Ten Ninety Nine (1099)"),
    ]
    
    for endpoint, desc in reports:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{error_info}")
        results[desc] = success
    
    print("\n" + "=" * 70)
    print("TESTING: ACCOUNTING.BUDGETS.READ")
    print("=" * 70)
    
    budgets = [
        ("Budgets", "Budgets"),
    ]
    
    for endpoint, desc in budgets:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[desc] = success
    
    print("\n" + "=" * 70)
    print("TESTING: ACCOUNTING.JOURNALS.READ")
    print("=" * 70)
    
    journals = [
        ("Journals", "Journal entries"),
        ("ManualJournals", "Manual journals"),
    ]
    
    for endpoint, desc in journals:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[desc] = success
    
    print("\n" + "=" * 70)
    print("TESTING: ACCOUNTING.ATTACHMENTS.READ / ACCOUNTING.ATTACHMENTS")
    print("=" * 70)
    
    # Test attachments for different object types
    attachments_test = [
        ("Invoices?page=1", "Invoice attachments (check if invoices exist)"),
        ("Contacts?page=1", "Contact attachments (check if contacts exist)"),
        ("BankTransactions?page=1", "Bank transaction attachments"),
    ]
    
    for endpoint, desc in attachments_test:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[f"Attachments - {desc}"] = success
    
    print("\n" + "=" * 70)
    print("TESTING: ASSETS.READ / ASSETS")
    print("=" * 70)
    
    assets = [
        ("Assets", "Fixed assets"),
        ("AssetTypes", "Asset types"),
        ("Settings", "Asset settings"),
    ]
    
    for endpoint, desc in assets:
        success, result = test_endpoint(access_token, tenant_id, XERO_ASSETS_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[f"Assets - {desc}"] = success
    
    print("\n" + "=" * 70)
    print("TESTING: FILES.READ / FILES")
    print("=" * 70)
    
    files = [
        ("Files", "Files"),
        ("Folders", "Folders"),
        ("Inbox", "Inbox folder"),
    ]
    
    for endpoint, desc in files:
        success, result = test_endpoint(access_token, tenant_id, XERO_FILES_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[f"Files - {desc}"] = success
    
    print("\n" + "=" * 70)
    print("TESTING: PROJECTS.READ / PROJECTS")
    print("=" * 70)
    
    projects = [
        ("Projects", "Projects"),
    ]
    
    for endpoint, desc in projects:
        success, result = test_endpoint(access_token, tenant_id, XERO_PROJECTS_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[f"Projects - {desc}"] = success
    
    # Additional accounting endpoints
    print("\n" + "=" * 70)
    print("TESTING: ADDITIONAL ACCOUNTING ENDPOINTS")
    print("=" * 70)
    
    additional = [
        ("Accounts", "Chart of accounts"),
        ("Items", "Items/inventory"),
        ("TrackingCategories", "Tracking categories"),
        ("TaxRates", "Tax rates"),
        ("Currencies", "Currencies"),
        ("Employees", "Employees"),
        ("Users", "Users"),
        ("Organisation", "Organization details"),
        ("BrandingThemes", "Branding themes"),
    ]
    
    for endpoint, desc in additional:
        success, result = test_endpoint(access_token, tenant_id, XERO_ACCOUNTING_BASE, endpoint, desc)
        status = "✅" if success else "❌"
        count_info = f" ({result} items)" if isinstance(result, int) and result > 0 else ""
        error_info = f" - {result}" if not success else ""
        print(f"{status} {desc}{count_info}{error_info}")
        results[desc] = success
    
    # Summary
    accessible = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("\n\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"\n✅ ACCESSIBLE: {accessible} endpoints")
    print(f"❌ BLOCKED: {total - accessible} endpoints")
    print(f"📊 SUCCESS RATE: {accessible/total*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ WORKING ENDPOINTS (What You Can Use)")
    print("=" * 70)
    
    categories = {
        "Invoicing & Sales": ["Invoices", "Credit notes", "Quotes", "Repeating invoices"],
        "Contacts": ["Contacts", "Contact groups"],
        "Banking": ["Payments", "Bank transactions", "Bank transfers", "Batch payments"],
        "Purchasing": ["Purchase orders", "Prepayments", "Overpayments"],
        "Journals": ["Journal entries", "Manual journals"],
        "Reports": ["Profit & Loss", "Balance Sheet", "Trial Balance", "Bank Summary", 
                    "Executive Summary", "Budget Summary"],
        "Assets": ["Assets - Fixed assets", "Assets - Asset types", "Assets - Asset settings"],
        "Files": ["Files - Files", "Files - Folders", "Files - Inbox folder"],
        "Projects": ["Projects - Projects"],
    }
    
    for category, keywords in categories.items():
        category_items = [k for k in results.keys() if results[k] and any(kw in k for kw in keywords)]
        if category_items:
            print(f"\n📂 {category} ({len(category_items)} endpoints)")
            for item in category_items:
                print(f"   ✅ {item}")
    
    print("\n" + "=" * 70)
    
    # Save results
    output_file = Path(__file__).parent / 'XERO_FULL_PERMISSIONS_RESULTS.json'
    with open(output_file, 'w') as f:
        json.dump({
            'accessible': [k for k, v in results.items() if v],
            'blocked': [k for k, v in results.items() if not v],
            'total_accessible': accessible,
            'total_tested': total,
            'success_rate': f"{accessible/total*100:.1f}%"
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
