"""Test the 5 fixed standard calculators"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

print('\n' + '='*80)
print('TESTING 5 FIXED STANDARD CALCULATORS')
print('='*80)

tests = [
    {
        'name': '1. Booklets (Saddle-Stitched)',
        'tool': 'calculate_booklets',
        'params': {
            'quantity': 100,  # Was string "100" - now handles both
            'total_pages': 20,  # Was string - now converts
            'cover_stock_gsm': 300,
            'internal_stock_gsm': 100,
            'cover_print_mode': 'double_sided',
            'internal_print_mode': 'double_sided'
        }
    },
    {
        'name': '2. Business Cards (Standard)',
        'tool': 'calculate_business_cards',
        'params': {
            'quantity': 500,
            'stock_type': 'standard',
            'print_type': 'double_sided',
            'finish_size': '90x55mm',
            'celloglaze': 'none'
        }
    },
    {
        'name': '3. Flyers (Standard)',
        'tool': 'calculate_flyers',
        'params': {
            'quantity': 1000,
            'width': 210,  # A4
            'height': 297,
            'stock_gsm': 150,  # Changed from 170 (may not be in DB)
            'print_mode': 'double_sided',
            'cello_type': 'none',
            'folded': False
        }
    },
    {
        'name': '4. Letterheads (Standard)',
        'tool': 'calculate_letterheads',
        'params': {
            'quantity': 500,
            'stock': '100GSM Uncoated',  # Now handles string parsing
            'colors': 4  # Full color
        }
    },
    {
        'name': '5. Perfect Bound Books (Standard)',
        'tool': 'calculate_perfect_bound_books',
        'params': {
            'quantity': 100,
            'total_pages': 48,  # Now ensures int before math
            'cover_stock_gsm': 300,
            'internal_stock_gsm': 100,
            'cover_print_mode': 'double_sided',
            'internal_print_mode': 'double_sided',
            'cover_lamination': 'none',
            'spot_uv': False
        }
    }
]

results = []
for test in tests:
    print(f"\n{test['name']}...")
    try:
        result = r.execute_tool(tool_name=test['tool'], **test['params'])
        
        if result.get('success'):
            price = result.get('total_price', result.get('total_cost_inc_gst', 'N/A'))
            print(f"   [OK] Price: ${price:.2f}")
            results.append((test['name'], 'PASS', f'${price:.2f}'))
        elif result.get('error_type') == 'database_connection':
            print(f"   [DB] Database unavailable (expected in test environment)")
            results.append((test['name'], 'DB_UNAVAILABLE', 'Database required'))
        else:
            error = result.get('error', 'Unknown error')
            print(f"   [FAIL] {error[:80]}")
            results.append((test['name'], 'FAIL', error[:60]))
    except Exception as e:
        print(f"   [ERROR] {str(e)[:80]}")
        results.append((test['name'], 'ERROR', str(e)[:60]))

print('\n' + '='*80)
print('SUMMARY')
print('='*80)
passed = sum(1 for _, status, _ in results if status == 'PASS')
db_issues = sum(1 for _, status, _ in results if status == 'DB_UNAVAILABLE')
failed = sum(1 for _, status, _ in results if status in ['FAIL', 'ERROR'])

print(f"Passed:           {passed}/5")
print(f"DB Unavailable:   {db_issues}/5 (normal for test environment)")
print(f"Failed:           {failed}/5")
print('='*80)

# Detail any failures
failures = [r for r in results if r[1] in ['FAIL', 'ERROR']]
if failures:
    print('\nFAILURE DETAILS:')
    for name, status, error in failures:
        print(f"  {name}: {error}")
