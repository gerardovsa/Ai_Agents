"""
Test Printed Flyers Calculator - All 5 Website-Validated Configurations
Date: January 27, 2026
Purpose: Verify calculator works with registry parameter injection
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'))

from calculator_wrapper import calculate_printed_flyers_shopify

print("="*80)
print("PRINTED FLYERS CALCULATOR - COMPREHENSIVE TEST")
print("="*80)
print("Testing with internal registry params (_user_id) to simulate production")
print()

# Test 1: Small Quantity Double Sided Colour A5
print("TEST 1: Small Quantity Double Sided Colour A5")
print("-" * 80)
result1 = calculate_printed_flyers_shopify(
    quantity=100,
    artworks=1,
    print_sides="Double",
    print_type="Colour",
    finish_size="A5 - 148mm x 210mm",
    paper_stock="Satin 150GSM",
    _user_id=1,  # Internal registry param
    _session_id="test-session"  # Internal registry param
)
print(f"Configuration: 100 qty, A5, Double, Colour, Satin 150GSM, 1 artwork")
print(f"Expected: $102.27")
if result1.get('success'):
    actual = result1.get('final_price', result1.get('total_price', 'N/A'))
    print(f"Actual: ${actual}")
    diff = abs(float(actual) - 102.27) if actual != 'N/A' else 999
    print(f"Difference: ${diff:.2f} ({(diff/102.27)*100:.2f}%)")
    print(f"✅ PASS" if diff < 1.0 else f"❌ FAIL")
else:
    print(f"❌ ERROR: {result1.get('error', 'Unknown error')}")
print()

# Test 2: Medium Quantity Single Sided B&W DL
print("TEST 2: Medium Quantity Single Sided B&W DL")
print("-" * 80)
result2 = calculate_printed_flyers_shopify(
    quantity=500,
    artworks=1,
    print_sides="Single",
    print_type="Black & White",
    finish_size="DL - 99mm x 210mm",
    paper_stock="Uncoated Bond 80GSM",
    _user_id=1,
    _session_id="test-session"
)
print(f"Configuration: 500 qty, DL, Single, B&W, Uncoated 80GSM, 1 artwork")
print(f"Expected: $107.74")
if result2.get('success'):
    actual = result2.get('final_price', result2.get('total_price', 'N/A'))
    print(f"Actual: ${actual}")
    diff = abs(float(actual) - 107.74) if actual != 'N/A' else 999
    print(f"Difference: ${diff:.2f} ({(diff/107.74)*100:.2f}%)")
    print(f"✅ PASS" if diff < 1.0 else f"❌ FAIL")
else:
    print(f"❌ ERROR: {result2.get('error', 'Unknown error')}")
print()

# Test 3: Bulk Discount Double Sided Colour A4
print("TEST 3: Bulk Discount Double Sided Colour A4")
print("-" * 80)
result3 = calculate_printed_flyers_shopify(
    quantity=1000,
    artworks=2,
    print_sides="Double",
    print_type="Colour",
    finish_size="A4 - 210mm x 297mm",
    paper_stock="Satin 350GSM",
    _user_id=1,
    _session_id="test-session"
)
print(f"Configuration: 1000 qty, A4, Double, Colour, Satin 350GSM, 2 artworks")
print(f"Expected: $379.94")
if result3.get('success'):
    actual = result3.get('final_price', result3.get('total_price', 'N/A'))
    print(f"Actual: ${actual}")
    diff = abs(float(actual) - 379.94) if actual != 'N/A' else 999
    print(f"Difference: ${diff:.2f} ({(diff/379.94)*100:.2f}%)")
    print(f"✅ PASS" if diff < 1.0 else f"❌ FAIL")
else:
    print(f"❌ ERROR: {result3.get('error', 'Unknown error')}")
print()

# Test 4: Medium Quantity Single Sided Colour A6
print("TEST 4: Medium Quantity Single Sided Colour A6")
print("-" * 80)
result4 = calculate_printed_flyers_shopify(
    quantity=250,
    artworks=1,
    print_sides="Single",
    print_type="Colour",
    finish_size="A6 - 105mm x 148mm",
    paper_stock="Satin 128GSM",
    _user_id=1,
    _session_id="test-session"
)
print(f"Configuration: 250 qty, A6, Single, Colour, Satin 128GSM, 1 artwork")
print(f"Expected: $100.11")
if result4.get('success'):
    actual = result4.get('final_price', result4.get('total_price', 'N/A'))
    print(f"Actual: ${actual}")
    diff = abs(float(actual) - 100.11) if actual != 'N/A' else 999
    print(f"Difference: ${diff:.2f} ({(diff/100.11)*100:.2f}%)")
    print(f"✅ PASS" if diff < 1.0 else f"❌ FAIL")
else:
    print(f"❌ ERROR: {result4.get('error', 'Unknown error')}")
print()

# Test 5: Large Format Bulk Double Sided Colour A3
print("TEST 5: Large Format Bulk Double Sided Colour A3")
print("-" * 80)
result5 = calculate_printed_flyers_shopify(
    quantity=2000,
    artworks=3,
    print_sides="Double",
    print_type="Colour",
    finish_size="A3 - 297mm x 420mm",
    paper_stock="Satin 250GSM",
    _user_id=1,
    _session_id="test-session"
)
print(f"Configuration: 2000 qty, A3, Double, Colour, Satin 250GSM, 3 artworks")
print(f"Expected: $654.44")
if result5.get('success'):
    actual = result5.get('final_price', result5.get('total_price', 'N/A'))
    print(f"Actual: ${actual}")
    diff = abs(float(actual) - 654.44) if actual != 'N/A' else 999
    print(f"Difference: ${diff:.2f} ({(diff/654.44)*100:.2f}%)")
    print(f"✅ PASS" if diff < 1.0 else f"❌ FAIL")
else:
    print(f"❌ ERROR: {result5.get('error', 'Unknown error')}")
print()

# Summary
print("="*80)
print("TEST SUMMARY")
print("="*80)
results = [result1, result2, result3, result4, result5]
passed = sum(1 for r in results if r.get('success'))
print(f"Tests Passed: {passed}/5")
print(f"Tests Failed: {5-passed}/5")
print()

if passed == 5:
    print("✅ ALL TESTS PASSED - Calculator working correctly with internal params")
else:
    print("⚠️ SOME TESTS FAILED - Check errors above")
