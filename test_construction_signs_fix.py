"""
Test Construction Signs Alignment (Jan 23, 2026)
Tests wrapper with JSON format values
"""

import sys
from pathlib import Path

# Add calculator implementations path
calc_impl_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(calc_impl_dir))

from calculator_wrapper import calculate_construction_signs

def test_construction_signs():
    """Test Construction Signs with JSON format values"""
    
    print("=" * 80)
    print("CONSTRUCTION SIGNS ALIGNMENT TEST - JSON FORMAT")
    print("=" * 80)
    
    # Test 1: JSON format values (default size, 5mm)
    print("\n✅ Test 1: JSON format - 10 qty, 600mm x 900mm, 5mm, Single Sided")
    result1 = calculate_construction_signs(
        quantity=10,
        size="600mm x 900mm",  # JSON format
        thickness="5mm",        # JSON format
        sides="Single Sided",   # JSON format with suffix
        eyelets="No Eyelets",
        cutting="Standard square edge",
        artworks=1
    )
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Total Price: ${result1['total_price']:.2f}")
        print(f"Unit Price: ${result1['unit_price']:.2f}")
        print(f"Size in specs: {result1['specifications'].get('size', 'N/A')}")
        print(f"Thickness in specs: {result1['specifications'].get('thickness', 'N/A')}")
        print(f"Sides in specs: {result1['specifications'].get('sides', 'N/A')}")
    else:
        print(f"❌ Error: {result1['error']}")
    
    # Test 2: Different JSON values (larger size, 3mm, double sided)
    print("\n✅ Test 2: JSON format - 25 qty, 1200mm x 2400mm, 3mm, Double Sided")
    result2 = calculate_construction_signs(
        quantity=25,
        size="1200mm x 2400mm",  # JSON format
        thickness="3mm",          # JSON format
        sides="Double Sided",     # JSON format with suffix
        eyelets="4 x Eyelets (1 In Each Corner)",
        cutting="Standard square edge",
        artworks=1
    )
    print(f"Success: {result2['success']}")
    if result2['success']:
        print(f"Total Price: ${result2['total_price']:.2f}")
        print(f"Unit Price: ${result2['unit_price']:.2f}")
        print(f"Size in specs: {result2['specifications'].get('size', 'N/A')}")
        print(f"Thickness in specs: {result2['specifications'].get('thickness', 'N/A')}")
        print(f"Sides in specs: {result2['specifications'].get('sides', 'N/A')}")
    else:
        print(f"❌ Error: {result2['error']}")
    
    # Test 3: Test eyelets and cutting options
    print("\n✅ Test 3: JSON format - With custom eyelets and cutting")
    result3 = calculate_construction_signs(
        quantity=15,
        size="900mm x 1200mm",
        thickness="5mm",
        sides="Single Sided",
        eyelets="6 x Eyelets (3 each top & bottom)",
        cutting="Custom Shape",
        artworks=2
    )
    print(f"Success: {result3['success']}")
    if result3['success']:
        print(f"Total Price: ${result3['total_price']:.2f}")
        print(f"Unit Price: ${result3['unit_price']:.2f}")
        print(f"Eyelets in specs: {result3['specifications'].get('eyelets', 'N/A')}")
        print(f"Cutting in specs: {result3['specifications'].get('cutting', 'N/A')}")
    else:
        print(f"❌ Error: {result3['error']}")
    
    # Test 4: Invalid size (old format should be rejected)
    print("\n❌ Test 4: Invalid size - old format '600x450' should be rejected")
    result4 = calculate_construction_signs(
        quantity=10,
        size="600x450",  # Old format (no spaces, no mm)
        thickness="5mm",
        sides="Single Sided",
        artworks=1
    )
    print(f"Success: {result4['success']}")
    if not result4['success']:
        print(f"✅ Correctly rejected: {result4['error']}")
    else:
        print(f"❌ Should have been rejected but was accepted!")
    
    # Test 5: Invalid sides (without suffix should be rejected)
    print("\n❌ Test 5: Invalid sides - 'Single' without suffix should be rejected")
    result5 = calculate_construction_signs(
        quantity=10,
        size="600mm x 900mm",
        thickness="5mm",
        sides="Single",  # Missing "Sided" suffix
        artworks=1
    )
    print(f"Success: {result5['success']}")
    if not result5['success']:
        print(f"✅ Correctly rejected: {result5['error']}")
    else:
        print(f"❌ Should have been rejected but was accepted!")
    
    # Test 6: Invalid thickness
    print("\n❌ Test 6: Invalid thickness - '4mm' should be rejected")
    result6 = calculate_construction_signs(
        quantity=10,
        size="600mm x 900mm",
        thickness="4mm",  # Not in enum
        sides="Single Sided",
        artworks=1
    )
    print(f"Success: {result6['success']}")
    if not result6['success']:
        print(f"✅ Correctly rejected: {result6['error']}")
    else:
        print(f"❌ Should have been rejected but was accepted!")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    tests_passed = sum([
        result1['success'],
        result2['success'],
        result3['success'],
        not result4['success'],  # Should fail
        not result5['success'],  # Should fail
        not result6['success']   # Should fail
    ])
    print(f"Tests Passed: {tests_passed}/6")
    
    if tests_passed == 6:
        print("✅ ALL TESTS PASSED - Construction Signs fully aligned!")
    else:
        print(f"❌ {6 - tests_passed} tests failed")

if __name__ == "__main__":
    test_construction_signs()
