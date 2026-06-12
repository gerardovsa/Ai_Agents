"""Test Metal Face A-Frame Alignment (Jan 23, 2026)"""
import sys
from pathlib import Path

calc_impl_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(calc_impl_dir))

from calculator_wrapper import calculate_metal_face_a_frame

print("=" * 80)
print("METAL FACE A-FRAME ALIGNMENT TEST")
print("=" * 80)

# Test 1: JSON format
print("\n✅ Test 1: JSON format - 5 qty, 600mm W x 900mm H")
result1 = calculate_metal_face_a_frame(
    quantity=5,
    size="600mm W x 900mm H",
    artworks=1
)
print(f"Success: {result1['success']}")
if result1['success']:
    print(f"Total: ${result1['total_price']:.2f}, Unit: ${result1['unit_price']:.2f}")
else:
    print(f"❌ Error: {result1['error']}")

# Test 2: Invalid old format
print("\n❌ Test 2: Old format '600x900' should be rejected")
result2 = calculate_metal_face_a_frame(quantity=5, size="600x900", artworks=1)
print(f"Success: {result2['success']}")
if not result2['success']:
    print(f"✅ Correctly rejected: {result2['error']}")

print(f"\n{'='*80}")
print(f"Tests Passed: {result1['success'] and not result2['success']}/2")
