"""Test Stackable Cubes Alignment (Jan 23, 2026)"""
import sys
from pathlib import Path

calc_impl_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(calc_impl_dir))

from calculator_wrapper import calculate_stackable_cubes

print("=" * 80)
print("STACKABLE CUBES ALIGNMENT TEST")
print("=" * 80)

# Test 1: JSON format
print("\n✅ Test 1: JSON format - 10 qty, 5mm Corflute, Medium 400mm x 400mm")
result1 = calculate_stackable_cubes(
    quantity=10,
    material="5mm Corflute",
    cube_size="Medium 400mm x 400mm",
    artworks=1
)
print(f"Success: {result1['success']}")
if result1['success']:
    print(f"Total: ${result1['total_price']:.2f}, Unit: ${result1['unit_price']:.2f}")
else:
    print(f"❌ Error: {result1['error']}")

# Test 2: Invalid old format
print("\n❌ Test 2: Old material format 'Corrugated' should be rejected")
result2 = calculate_stackable_cubes(quantity=10, material="Corrugated", cube_size="Medium 400mm x 400mm", artworks=1)
print(f"Success: {result2['success']}")
if not result2['success']:
    print(f"✅ Correctly rejected: {result2['error']}")

print(f"\n{'='*80}")
print(f"Tests Passed: {result1['success'] and not result2['success']}/2")
