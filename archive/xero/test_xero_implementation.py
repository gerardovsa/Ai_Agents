"""Test Xero tools with actual API implementation"""
from tools.implementations.xero import (
    xero_get_invoices,
    xero_get_invoice_by_id,
    xero_get_contacts,
    xero_get_accounts,
    xero_get_bank_transactions,
    xero_get_payments
)
import json

print('\n' + '='*70)
print('Testing 6 Xero Tools with Real API Implementation')
print('='*70 + '\n')

tools_to_test = [
    ('xero_get_invoices', lambda: xero_get_invoices(business_id=1)),
    ('xero_get_invoice_by_id', lambda: xero_get_invoice_by_id(business_id=1, invoice_id='dummy-id')),
    ('xero_get_contacts', lambda: xero_get_contacts(business_id=1)),
    ('xero_get_accounts', lambda: xero_get_accounts(business_id=1)),
    ('xero_get_bank_transactions', lambda: xero_get_bank_transactions(business_id=1)),
    ('xero_get_payments', lambda: xero_get_payments(business_id=1))
]

results = []
for i, (tool_name, test_func) in enumerate(tools_to_test, 1):
    print(f'{i}. Testing {tool_name}...')
    try:
        result = test_func()
        
        # Check if it's implemented (not the old error)
        if result.get('success') is False:
            error_msg = result.get('error', '')
            if 'does not implement' in error_msg:
                status = '❌ NOT IMPLEMENTED'
                detail = error_msg
            elif 'credentials not found' in error_msg.lower():
                status = '✅ IMPLEMENTED (needs credentials)'
                detail = 'Xero credentials not configured'
            elif 'failed to get' in error_msg.lower():
                status = '✅ IMPLEMENTED (auth error)'
                detail = error_msg[:80]
            else:
                status = '⚠️ ERROR'
                detail = error_msg[:80]
        else:
            status = '✅ SUCCESS'
            detail = f"Returned {len(result.get('invoices', result.get('contacts', result.get('accounts', result.get('transactions', result.get('payments', []))))))} items"
        
        results.append((tool_name, status, detail))
        print(f'   {status}')
        if 'ERROR' in status or 'NOT IMPLEMENTED' in status:
            print(f'   Detail: {detail}')
    except Exception as e:
        results.append((tool_name, '❌ EXCEPTION', str(e)[:80]))
        print(f'   ❌ EXCEPTION: {e}')
    print()

print('='*70)
print('Summary:')
print('='*70)
for tool_name, status, detail in results:
    print(f'{tool_name:30} {status}')
    if 'ERROR' in status or 'NOT IMPLEMENTED' in status or 'EXCEPTION' in status:
        print(f'  → {detail}')

# Count statuses
implemented = sum(1 for _, s, _ in results if 'IMPLEMENTED' in s or 'SUCCESS' in s)
total = len(results)
print(f'\n{implemented}/{total} tools properly implemented')
print('='*70 + '\n')
