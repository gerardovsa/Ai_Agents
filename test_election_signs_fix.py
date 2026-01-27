"""Test Election Signs Alignment (Jan 23, 2026)"""
import sys
from pathlib import Path

calc_impl_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(calc_impl_dir))

from calculator_wrapper import calculate_election_signs

print("=" * 80)
print("ELECTION SIGNS ALIGNMENT TEST")
print("=" * 80)

# Test 1: JSON format
print("\n✅ Test 1: JSON format - 10 qty, 600mm x 900mm, 5mm, Single Sided")
result1 = calculate_election_signs(
    quantity=10,
    size="600mm x 900mm",
    thickness="5mm",
    sides="Single Sided",
    eyelets="No Eyelets",
    cutting="Standard square edge",
    artworks=1
)
print(f"Success: {result1['success']}")
if result1['success']:
    print(f"Total: ${result1['total_price']:.2f}, Unit: ${result1['unit_price']:.2f}")
else:
    print(f"❌ Error: {result1['error']}")

# Test 2: Invalid old format
print("\n❌ Test 2: Old format '600x450' should be rejected")
result2 = calculate_election_signs(quantity=10, size="600x450", thickness="5mm", sides="Single Sided", artworks=1)
print(f"Success: {result2['success']}")
if not result2['success']:
    print(f"✅ Correctly rejected: {result2['error']}")

print(f"\n{'='*80}")
print(f"Tests Passed: {result1['success'] and not result2['success']}/2")
