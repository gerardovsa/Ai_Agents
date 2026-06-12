"""
Test inhouse_calculate_quote() with all three parameter formats
Verifies the wrapper accepts both nested and flattened parameters
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'inhouse-print' / 'implementations'))

from inhouse_wrapper import inhouse_calculate_quote

print("="*80)
print("TESTING inhouse_calculate_quote() PARAMETER FORMATS")
print("="*80)

# TEST 1: NESTED FORMAT (Original schema format)
print("\n[TEST 1] Nested parameters (schema format):")
print("-" * 80)
try:
    result = inhouse_calculate_quote(
        product_type='business_cards',
        parameters={
            'quantity': 1000,
            'stock_type': 'satin',
            'print_type': 'double_sided',
            'finish_size': '90x55mm',
            'celloglaze': '2_side_matt'
        }
    )
    
    if result.get('success'):
        quote = result.get('quote', {})
        cost_ex = quote.get('cost_ex_gst', 0)
        cost_inc = quote.get('cost_inc_gst', 0)
        print(f"✅ PASSED: Quote calculated successfully")
        print(f"   Cost ex GST: ${cost_ex:.2f}")
        print(f"   Cost inc GST: ${cost_inc:.2f}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 2: FLATTENED FORMAT (execute_tool format)
print("\n[TEST 2] Flattened parameters (execute_tool format):")
print("-" * 80)
try:
    result = inhouse_calculate_quote(
        product_type='business_cards',
        quantity=500,
        stock_type='premium',
        print_type='double_sided',
        finish_size='90x55mm',
        celloglaze='2_side_gloss',
        _user_id=14,  # Credential injection (should be ignored)
        _injected_credentials={'test': 'data'}  # Should be ignored
    )
    
    if result.get('success'):
        quote = result.get('quote', {})
        cost_ex = quote.get('cost_ex_gst', 0)
        cost_inc = quote.get('cost_inc_gst', 0)
        print(f"✅ PASSED: Quote calculated successfully")
        print(f"   Cost ex GST: ${cost_ex:.2f}")
        print(f"   Cost inc GST: ${cost_inc:.2f}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 3: MIXED FORMAT (parameters=None with kwargs)
print("\n[TEST 3] Mixed format (parameters=None with kwargs):")
print("-" * 80)
try:
    result = inhouse_calculate_quote(
        product_type='business_cards',
        parameters=None,  # Explicitly None
        quantity=250,
        stock_type='standard',
        print_type='single_sided',
        finish_size='90x55mm',
        celloglaze='none'
    )
    
    if result.get('success'):
        quote = result.get('quote', {})
        cost_ex = quote.get('cost_ex_gst', 0)
        cost_inc = quote.get('cost_inc_gst', 0)
        print(f"✅ PASSED: Quote calculated successfully")
        print(f"   Cost ex GST: ${cost_ex:.2f}")
        print(f"   Cost inc GST: ${cost_inc:.2f}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 4: Via Registry (simulate execute_tool)
print("\n[TEST 4] Via Registry (simulating execute_tool):")
print("-" * 80)
try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    result = registry.execute_tool(
        tool_name='inhouse_calculate_quote',
        product_type='business_cards',
        quantity=100,
        stock_type='premium',
        print_type='double_sided',
        finish_size='90x55mm',
        celloglaze='2_side_matt'
    )
    
    if result.get('success'):
        quote = result.get('quote', {})
        cost_ex = quote.get('cost_ex_gst', 0)
        cost_inc = quote.get('cost_inc_gst', 0)
        print(f"✅ PASSED: Quote calculated successfully via registry")
        print(f"   Cost ex GST: ${cost_ex:.2f}")
        print(f"   Cost inc GST: ${cost_inc:.2f}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print("All formats should work to ensure backward compatibility:")
print("  1. Nested format (original schema) - For direct AI agent calls")
print("  2. Flattened format (execute_tool) - For meta-tool wrapper")
print("  3. Mixed format (parameters=None) - For flexibility")
print("  4. Via Registry - For tool execution framework")
print("="*80)
