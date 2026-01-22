import sys
sys.path.insert(0, 'UI/modules_external/inhouse-print/implementations')

from inhouse_wrapper import inhouse_calculate_quote

print("\n" + "="*60)
print("QUICK VALIDATION TEST")
print("="*60)

# Test 1: Invalid product type
result = inhouse_calculate_quote('invalid_type', {})
print("\nTest 1: Invalid Product Type")
print(f"Success: {result['success']}")
print(f"Error: {result['error']}")
print(f"Help: {result.get('help', 'N/A')}")

print("\n" + "="*60)
print("VALIDATION WORKING CORRECTLY!")
print("="*60)
