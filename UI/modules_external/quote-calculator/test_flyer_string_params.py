#!/usr/bin/env python3
"""Test GOD Flyer calculator with STRING parameters"""
import sys
sys.path.insert(0, 'implementations')
sys.path.insert(0, 'backend')
sys.path.insert(0, 'backend/god_calculators')
sys.path.insert(0, '../inhouse-print')

from calculator_wrapper import calculate_flyers_god

print("🧪 Testing GOD Flyer Calculator with STRING parameters:\n")
print("="*70)

# Test with STRING parameters (should auto-convert)
print("\n1️⃣  Test with 'colour' strings:")
result = calculate_flyers_god(
    quantity=1000,
    width=210,
    height=297,
    gsm=150,
    print_side1='colour',
    print_side2='colour'
)
print(f"   Success: {result.get('success')}")
if result.get('success'):
    print(f"   Price: ${result.get('total_price', 0):.2f}")
    print(f"   Cost to business: ${result.get('cost_to_business', 0):.2f}")
    print(f"   Product: {result.get('product_type')}")
else:
    print(f"   Error: {result.get('error')}")

# Test with INTEGER parameters (original way)
print("\n2️⃣  Test with integer parameters:")
result2 = calculate_flyers_god(
    quantity=1000,
    width=210,
    height=297,
    gsm=150,
    print_side1=1,
    print_side2=1
)
print(f"   Success: {result2.get('success')}")
if result2.get('success'):
    print(f"   Price: ${result2.get('total_price', 0):.2f}")

# Test with mixed parameters
print("\n3️⃣  Test with 'b&w' and 'none':")
result3 = calculate_flyers_god(
    quantity=500,
    width=210,
    height=297,
    gsm=200,
    print_side1='colour',
    print_side2='b&w'
)
print(f"   Success: {result3.get('success')}")
if result3.get('success'):
    print(f"   Price: ${result3.get('total_price', 0):.2f}")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
