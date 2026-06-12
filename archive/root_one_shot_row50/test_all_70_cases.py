"""
Test All 70 Documented Test Cases
Runs through TEST_QUOTES_BY_CATEGORY_WITH_ANSWERS.md and validates each quote

This tests the wrapper functions (90% of AI traffic) against documented expected results.
"""

import sys
from pathlib import Path
from decimal import Decimal
import json
from typing import Dict, Any, List

# Add paths
project_root = Path(__file__).resolve().parent
implementations_dir = project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(implementations_dir))
sys.path.insert(0, str(project_root))

# Import wrapper functions
from calculator_wrapper import (
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_folded_flyers_shopify,
    calculate_corflute_signs_shopify
)

print("=" * 80)
print("COMPREHENSIVE TEST SUITE - ALL 70 DOCUMENTED TEST CASES")
print("Validating AI Quote Calculations vs Expected Results")
print("January 23, 2026")
print("=" * 80)
print()

# Store results
results = {
    "wire_bound": [],
    "spiral_bound": [],
    "perfect_bound": [],
    "saddle_stitch": [],
    "folded_flyers": [],
    "corflute_signs": []
}

total_tests = 0
passed_tests = 0
failed_tests = 0

# ============================================================================
# WIRE BOUND BOOKS - 5 Tests
# ============================================================================
print("\n" + "="*80)
print("WIRE BOUND BOOKS - 5 Tests")
print("="*80)

# Test 1: Training Manual
print("\n[1/70] Training Manual - 100 books, 50 pages, A4 Portrait")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=100,
        internal_pages=50,
        finish_size="A4 Portrait",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="None",
        outer_front_cover="Not Required",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="None",
        outer_back_cover="None",
        internal_stock="Uncoated Bond 100GSM",
        internal_print="Black & White",
        artworks=1
    )
    
    calculated = result.get('total_price', 0)
    expected = 1125.25
    difference = abs(calculated - expected)
    match = "✅ MATCH" if difference < 0.01 else f"❌ DIFF ${difference:.2f}"
    
    print(f"   Expected: ${expected:.2f}")
    print(f"   Got:      ${calculated:.2f}")
    print(f"   {match}")
    
    total_tests += 1
    if difference < 0.01:
        passed_tests += 1
        results["wire_bound"].append({"test": 1, "status": "PASS", "expected": expected, "got": calculated})
    else:
        failed_tests += 1
        results["wire_bound"].append({"test": 1, "status": "FAIL", "expected": expected, "got": calculated, "diff": float(difference)})
        
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    failed_tests += 1
    total_tests += 1
    results["wire_bound"].append({"test": 1, "status": "ERROR", "error": str(e)})

# Test 2: Conference Program
print("\n[2/70] Conference Program - 250 books, 80 pages, A5 Landscape")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=250,
        internal_pages=80,
        finish_size="A5 Landscape",
        printed_front_cover="350GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="2 Sided Matt",
        outer_front_cover="Clear PVC",
        printed_back_cover="350GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="2 Sided Matt",
        outer_back_cover="Clear PVC",
        internal_stock="Satin 128GSM",
        internal_print="Full Colour",
        artworks=2
    )
    
    calculated = result.get('total_price', 0)
    expected = 4040.77
    difference = abs(calculated - expected)
    match = "✅ MATCH" if difference < 0.01 else f"❌ DIFF ${difference:.2f}"
    
    print(f"   Expected: ${expected:.2f}")
    print(f"   Got:      ${calculated:.2f}")
    print(f"   {match}")
    
    total_tests += 1
    if difference < 0.01:
        passed_tests += 1
        results["wire_bound"].append({"test": 2, "status": "PASS", "expected": expected, "got": calculated})
    else:
        failed_tests += 1
        results["wire_bound"].append({"test": 2, "status": "FAIL", "expected": expected, "got": calculated, "diff": float(difference)})
        
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    failed_tests += 1
    total_tests += 1
    results["wire_bound"].append({"test": 2, "status": "ERROR", "error": str(e)})

# Test 3: Property Brochure
print("\n[3/70] Property Brochure - 50 books, 20 pages, DL Portrait")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=50,
        internal_pages=20,
        finish_size="DL Portrait",
        printed_front_cover="250GSM Satin",
        front_cover_print="1pp Colour",
        front_celloglaze="1 Side Gloss",
        outer_front_cover="Not Required",
        printed_back_cover="250GSM Satin",
        back_cover_print="1pp Colour",
        back_celloglaze="None",
        outer_back_cover="None",
        internal_stock="Uncoated Bond 80GSM",
        internal_print="Black & White",
        artworks=1
    )
    
    calculated = result.get('total_price', 0)
    expected = 461.51
    difference = abs(calculated - expected)
    match = "✅ MATCH" if difference < 0.01 else f"❌ DIFF ${difference:.2f}"
    
    print(f"   Expected: ${expected:.2f}")
    print(f"   Got:      ${calculated:.2f}")
    print(f"   {match}")
    
    total_tests += 1
    if difference < 0.01:
        passed_tests += 1
        results["wire_bound"].append({"test": 3, "status": "PASS", "expected": expected, "got": calculated})
    else:
        failed_tests += 1
        results["wire_bound"].append({"test": 3, "status": "FAIL", "expected": expected, "got": calculated, "diff": float(difference)})
        
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    failed_tests += 1
    total_tests += 1
    results["wire_bound"].append({"test": 3, "status": "ERROR", "error": str(e)})

# Test 4: School Newsletter
print("\n[4/70] School Newsletter - 500 books, 120 pages, A6 Landscape")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=500,
        internal_pages=120,
        finish_size="A6 Landscape",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="None",
        outer_front_cover="Not Required",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="None",
        outer_back_cover="Black Leather",
        internal_stock="Satin 150GSM",
        internal_print="Full Colour",
        artworks=3
    )
    
    calculated = result.get('total_price', 0)
    expected = 5003.56
    difference = abs(calculated - expected)
    match = "✅ MATCH" if difference < 0.01 else f"❌ DIFF ${difference:.2f}"
    
    print(f"   Expected: ${expected:.2f}")
    print(f"   Got:      ${calculated:.2f}")
    print(f"   {match}")
    
    total_tests += 1
    if difference < 0.01:
        passed_tests += 1
        results["wire_bound"].append({"test": 4, "status": "PASS", "expected": expected, "got": calculated})
    else:
        failed_tests += 1
        results["wire_bound"].append({"test": 4, "status": "FAIL", "expected": expected, "got": calculated, "diff": float(difference)})
        
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    failed_tests += 1
    total_tests += 1
    results["wire_bound"].append({"test": 4, "status": "ERROR", "error": str(e)})

# Test 5: Corporate Report
print("\n[5/70] Corporate Report - 1000 books, 200 pages, A4 Landscape")
try:
    result = calculate_wire_bound_books_shopify(
        quantity=1000,
        internal_pages=200,
        finish_size="A4 Landscape",
        printed_front_cover="300GSM Satin",
        front_cover_print="1pp Black & White",
        front_celloglaze="None",
        outer_front_cover="Not Required",
        printed_back_cover="300GSM Satin",
        back_cover_print="1pp Black & White",
        back_celloglaze="None",
        outer_back_cover="None",
        internal_stock="Uncoated Bond 90GSM",
        internal_print="Black & White",
        artworks=1
    )
    
    calculated = result.get('total_price', 0)
    expected = 17145.32
    difference = abs(calculated - expected)
    match = "✅ MATCH" if difference < 0.01 else f"❌ DIFF ${difference:.2f}"
    
    print(f"   Expected: ${expected:.2f}")
    print(f"   Got:      ${calculated:.2f}")
    print(f"   {match}")
    
    total_tests += 1
    if difference < 0.01:
        passed_tests += 1
        results["wire_bound"].append({"test": 5, "status": "PASS", "expected": expected, "got": calculated})
    else:
        failed_tests += 1
        results["wire_bound"].append({"test": 5, "status": "FAIL", "expected": expected, "got": calculated, "diff": float(difference)})
        
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    failed_tests += 1
    total_tests += 1
    results["wire_bound"].append({"test": 5, "status": "ERROR", "error": str(e)})

print(f"\n{'─'*80}")
print(f"Wire Bound Summary: {sum(1 for r in results['wire_bound'] if r['status'] == 'PASS')}/5 passed")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

print("\n" + "="*80)
print("NOTE: This is a partial implementation showing the pattern.")
print("To complete all 70 tests, we need to add:")
print("  - Spiral Bound Books (5 tests)")
print("  - Perfect Bound Books (20 tests)")
print("  - Saddle Stitch Books (20 tests)")
print("  - Folded Flyers (10 tests)")
print("  - Corflute Signs (10 tests)")
print("="*80)

# Save results
with open('test_70_cases_results.json', 'w') as f:
    json.dump({
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "results": results
    }, f, indent=2)

print(f"\n📄 Results saved to: test_70_cases_results.json")
