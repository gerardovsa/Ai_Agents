"""
Test Xero Markdown Enhancement
Tests that Xero tools now return markdown_table and export_options
"""

from tools.registry_v3 import RegistryV3
import json

print('='*70)
print('=== Testing Xero Markdown Enhancement ===')
print('='*70)

# Initialize registry
print('\nInitializing registry...')
r = RegistryV3()
print('Registry loaded successfully')

# Test 1: xero_get_contacts
print('\n' + '-'*70)
print('Test 1: xero_get_contacts')
print('-'*70)
try:
    result = r.execute_tool(
        tool_name='xero_get_contacts',
        business_id=1,
        _injected_credentials=True
    )
    
    if result.get('success'):
        print(f'✅ Success: {result.get("contact_count", 0)} contacts returned')
        print(f'   - Business: {result.get("business_name")}')
        print(f'   - Has markdown_table: {"markdown_table" in result}')
        print(f'   - Has export_options: {"export_options" in result}')
        
        if 'markdown_table' in result:
            md = result['markdown_table']
            lines = md.split('\n')
            print(f'\n   📊 Markdown Table Preview (first 10 lines):')
            for i, line in enumerate(lines[:10], 1):
                print(f'      {i}: {line[:80]}')
            print(f'      ... ({len(lines)} total lines)')
        
        if 'export_options' in result:
            export_opts = result['export_options']
            print(f'\n   📤 Export Options:')
            print(f'      - Google Sheets: {export_opts.get("google_sheets", False)}')
            print(f'      - Excel: {export_opts.get("excel", False)}')
    else:
        print(f'❌ Error: {result.get("error", "Unknown error")}')
        
except Exception as e:
    print(f'❌ Exception: {str(e)}')

# Test 2: xero_get_invoices
print('\n' + '-'*70)
print('Test 2: xero_get_invoices')
print('-'*70)
try:
    result = r.execute_tool(
        tool_name='xero_get_invoices',
        business_id=1,
        limit=5,  # Get just 5 invoices for testing
        _injected_credentials=True
    )
    
    if result.get('success'):
        print(f'✅ Success: {result.get("invoice_count", 0)} invoices returned')
        print(f'   - Has markdown_table: {"markdown_table" in result}')
        print(f'   - Has export_options: {"export_options" in result}')
        
        if 'markdown_table' in result:
            md = result['markdown_table']
            lines = md.split('\n')
            print(f'\n   📊 Markdown Table Preview (first 8 lines):')
            for i, line in enumerate(lines[:8], 1):
                print(f'      {i}: {line[:80]}')
    else:
        print(f'❌ Error: {result.get("error", "Unknown error")}')
        
except Exception as e:
    print(f'❌ Exception: {str(e)}')

# Test 3: xero_get_accounts
print('\n' + '-'*70)
print('Test 3: xero_get_accounts')
print('-'*70)
try:
    result = r.execute_tool(
        tool_name='xero_get_accounts',
        business_id=1,
        _injected_credentials=True
    )
    
    if result.get('success'):
        print(f'✅ Success: {result.get("account_count", 0)} accounts returned')
        print(f'   - Has markdown_table: {"markdown_table" in result}')
        print(f'   - Has export_options: {"export_options" in result}')
    else:
        print(f'❌ Error: {result.get("error", "Unknown error")}')
        
except Exception as e:
    print(f'❌ Exception: {str(e)}')

# Test 4: xero_get_invoices_by_date_range (date-range tool)
print('\n' + '-'*70)
print('Test 4: xero_get_invoices_by_date_range (date-range tool)')
print('-'*70)
try:
    result = r.execute_tool(
        tool_name='xero_get_invoices_by_date_range',
        business_id=1,
        from_date='2024-11-01',
        to_date='2024-11-30',
        limit=5,
        _injected_credentials=True
    )
    
    if result.get('success'):
        print(f'✅ Success: {result.get("invoice_count", 0)} invoices returned')
        print(f'   - Date range: {result.get("date_range")}')
        print(f'   - Has markdown_table: {"markdown_table" in result}')
        print(f'   - Has export_options: {"export_options" in result}')
        
        if 'markdown_table' in result:
            md = result['markdown_table']
            lines = md.split('\n')
            print(f'\n   📊 Markdown Table Preview:')
            for i, line in enumerate(lines[:8], 1):
                print(f'      {i}: {line[:80]}')
    else:
        print(f'❌ Error: {result.get("error", "Unknown error")}')
        
except Exception as e:
    print(f'❌ Exception: {str(e)}')

print('\n' + '='*70)
print('=== Test Summary ===')
print('='*70)
print('All Xero tools should now return:')
print('  1. ✅ markdown_table (string) - Full Markdown table with all data')
print('  2. ✅ export_options (object) - Google Sheets/Excel availability')
print('\nEnhanced tools:')
print('  - xero_get_invoices')
print('  - xero_get_contacts')
print('  - xero_get_payments')
print('  - xero_get_accounts')
print('  - xero_get_bank_transactions')
print('  - xero_get_invoices_by_date_range')
print('  - xero_get_contacts_by_date_range')
print('  - xero_get_payments_by_date_range')
print('  - xero_get_bank_transactions_by_date_range')
print('='*70)
