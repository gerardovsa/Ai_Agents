"""Test fixed calculators"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

print('\n' + '='*60)
print('TESTING FIXED CALCULATORS')
print('='*60)

# Test 1: Economical Business Cards
print('\n1. Economical Business Cards...')
result = r.execute_tool(
    tool_name='calculate_economical_business_cards_shopify',
    quantity=500,
    print_sides='Double side print',
    print_type='Colour',
    artworks=1
)
if result.get('success'):
    print(f'   [OK] Price: ${result["total_price"]:.2f}')
else:
    print(f'   [FAIL] {result.get("error", "Unknown")}')

# Test 2: Premium Business Cards  
print('\n2. Premium Business Cards...')
result = r.execute_tool(
    tool_name='calculate_premium_business_cards_shopify',
    quantity=500,
    print_sides='Double side print',
    print_type='Colour',
    celloglaze='Gloss Cellophane',
    artworks=1
)
if result.get('success'):
    print(f'   [OK] Price: ${result["total_price"]:.2f}')
else:
    print(f'   [FAIL] {result.get("error", "Unknown")}')

# Test 3: Corflute Signs GOD
print('\n3. Corflute Signs GOD...')
result = r.execute_tool(
    tool_name='calculate_corflute_signs_god',
    quantity=10,
    width=600,
    height=900,
    thickness=5,
    print_sides='double'
)
if result.get('success'):
    print(f'   [OK] Price: ${result["total_cost_inc_gst"]:.2f}')
else:
    print(f'   [FAIL] {result.get("error", "Unknown")}')

print('\n' + '='*60)
