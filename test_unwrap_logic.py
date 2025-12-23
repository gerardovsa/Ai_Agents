"""
Ultra-simple test - just test the parameter unwrapping logic
Without loading the full registry
"""

# Test the unwrapping logic directly
params = {
    '_user_id': 14,
    '_injected_credentials': {},
    'parameters': {
        'query': 'SELECT TOP 5 OrderID FROM Orders'
    }
}

print("=" * 80)
print("TEST: Parameter unwrapping logic")
print("=" * 80)

print("\nBEFORE unwrapping:")
print(f"  params keys: {list(params.keys())}")
print(f"  'parameters' in params: {'parameters' in params}")
print(f"  params['parameters']: {params.get('parameters')}")

# Apply the unwrapping logic
if 'parameters' in params and isinstance(params['parameters'], dict):
    nested_params = params.pop('parameters')
    params.update(nested_params)
    print("\n✅ Unwrapping applied!")

print("\nAFTER unwrapping:")
print(f"  params keys: {list(params.keys())}")
print(f"  'parameters' in params: {'parameters' in params}")
print(f"  'query' in params: {'query' in params}")
if 'query' in params:
    print(f"  params['query']: {params['query']}")

print("\n" + "=" * 80)
if 'query' in params and 'parameters' not in params:
    print("✅ SUCCESS: Nested parameters dict unwrapped correctly!")
    print("   - 'parameters' key removed")
    print("   - 'query' key extracted to top level")
else:
    print("❌ FAILED: Parameters not unwrapped correctly")
print("=" * 80)
