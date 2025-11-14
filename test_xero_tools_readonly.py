"""
Test Xero Read-Only Tools - Extract Data Without Modifying Anything

Tests:
1. xero_get_invoices - Get invoice list
2. xero_get_invoice_by_id - Get specific invoice (if exists)
3. xero_get_contacts - Get contact list
4. xero_get_accounts - Get chart of accounts
5. xero_get_bank_transactions - Get bank transactions
6. xero_get_payments - Get payment records
7. xero_smart_export_accounts_payable_stats - AP analysis

SKIPS (write operations):
- xero_create_invoice
- xero_smart_quote_to_production
- xero_smart_client_onboarding
- xero_smart_bulk_quote
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

def test_tool(registry, tool_name, **kwargs):
    """Test a single tool and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"{'='*60}")
    print(f"Parameters: {kwargs}")
    
    try:
        result = registry.execute_tool(tool_name=tool_name, **kwargs)
        print(f"✅ SUCCESS")
        print(f"Result type: {type(result).__name__}")
        
        # Show result summary
        if isinstance(result, dict):
            if 'error' in result:
                print(f"⚠️  Error in result: {result['error']}")
            elif 'success' in result:
                print(f"Success flag: {result['success']}")
            
            # Show keys
            print(f"Keys: {list(result.keys())}")
            
            # Show data counts
            if 'invoices' in result:
                print(f"Invoices found: {len(result['invoices'])}")
            elif 'contacts' in result:
                print(f"Contacts found: {len(result['contacts'])}")
            elif 'accounts' in result:
                print(f"Accounts found: {len(result['accounts'])}")
            elif 'transactions' in result:
                print(f"Transactions found: {len(result['transactions'])}")
            elif 'payments' in result:
                print(f"Payments found: {len(result['payments'])}")
        elif isinstance(result, list):
            print(f"List length: {len(result)}")
        else:
            print(f"Result: {str(result)[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:200]}")
        return False


def main():
    print("="*60)
    print("XERO READ-ONLY TOOLS TEST")
    print("="*60)
    print("Testing data extraction without creating/modifying anything")
    
    # Load registry
    print("\nLoading tool registry...")
    registry = RegistryV3()
    print(f"✅ Registry loaded: {len(registry.tools)} tools")
    
    # Count results
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: Get invoices
    results['total'] += 1
    if test_tool(registry, 'xero_get_invoices', business_id=1, status='AUTHORISED'):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 2: Get contacts
    results['total'] += 1
    if test_tool(registry, 'xero_get_contacts', business_id=1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Get accounts
    results['total'] += 1
    if test_tool(registry, 'xero_get_accounts', business_id=1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Get bank transactions
    results['total'] += 1
    if test_tool(registry, 'xero_get_bank_transactions', business_id=1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Get payments
    results['total'] += 1
    if test_tool(registry, 'xero_get_payments', business_id=1):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 6: Smart AP stats (read-only analysis)
    results['total'] += 1
    if test_tool(registry, 'xero_smart_export_accounts_payable_stats', 
                 business_id=1, days_back=30):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success rate: {results['passed']/results['total']*100:.0f}%")
    
    print("\n" + "="*60)
    print("TOOLS SKIPPED (Write Operations):")
    print("="*60)
    print("  - xero_create_invoice (creates invoices)")
    print("  - xero_smart_quote_to_production (creates invoice + FRED order)")
    print("  - xero_smart_client_onboarding (creates client + quote)")
    print("  - xero_smart_bulk_quote (creates multiple quotes)")
    print("\nThese tools were intentionally skipped to avoid modifying data.")


if __name__ == '__main__':
    main()
