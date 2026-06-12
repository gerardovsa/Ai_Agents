"""
Test corflute signs calculator - should now work with registry parameter injection
"""

import sys
from pathlib import Path

# Add modules to path
calculator_wrapper_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(calculator_wrapper_path))

from calculator_wrapper import calculate_corflute_signs_shopify

# Test 1: Normal call (should work)
print("TEST 1: Normal parameters")
result = calculate_corflute_signs_shopify(
    quantity=50,
    size_preset="600x900",
    thickness="5mm",
    double_sided=True,
    eyelet_option="four_corners",
    artworks=1
)
print(f"Result: {result.get('success')}")
if result['success']:
    print(f"  Total: ${result['total_price']:.2f}")

# Test 2: With internal registry params (simulating registry.execute_tool())
print("\nTEST 2: With internal registry params (_user_id, _injected_credentials)")
result = calculate_corflute_signs_shopify(
    quantity=100,
    size_preset="900x1200",
    thickness="3mm",
    double_sided=False,
    eyelet_option="two_top",
    artworks=2,
    _user_id=1,  # Internal registry param
    _injected_credentials={'test': 'credentials'},  # Internal registry param
    _session_id='test-session-123'  # Internal registry param
)
print(f"Result: {result.get('success')}")
if result['success']:
    print(f"  Total: ${result['total_price']:.2f}")
    print(f"  ✅ Internal params absorbed correctly!")
else:
    print(f"  ❌ Error: {result.get('error')}")

# Test 3: With typo (should error)
print("\nTEST 3: With parameter typo (should detect and error)")
try:
    result = calculate_corflute_signs_shopify(
        quantity=25,
        size_preset="450x600",
        thickness="5mm",
        double_sided=False,
        eyelet_option="none",
        artworks=1,
        _user_id=1,  # Internal param (OK)
        extra_param="typo"  # TYPO - should be caught
    )
    print(f"Result: {result.get('success')}")
    if not result['success']:
        print(f"  ✅ Typo detected: {result.get('error')}")
    else:
        print(f"  ❌ Typo NOT detected - validation failed!")
except TypeError as e:
    # Decorator catches typo before function runs (also valid)
    print(f"  ✅ Typo detected by decorator: {e}")

print("\n🎉 ALL TESTS COMPLETE")
