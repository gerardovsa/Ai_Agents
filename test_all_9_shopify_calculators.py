#!/usr/bin/env python3
"""
Complete Shopify Calculator Alignment Test
Tests all 9 Shopify calculators with wrapper functions
Verifies JSON → Backend → Schema → Wrapper consistency

Author: AI Agent
Date: January 23, 2026
Purpose: Comprehensive alignment testing post-fixes
"""

import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "UI" / "modules_external" / "quote-calculator" / "implementations"))
sys.path.insert(0, str(project_root / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"))

from calculator_wrapper import (
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_folded_flyers_shopify,
    calculate_corflute_signs_shopify,
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify,
    calculate_spiral_books_simple_shopify
)


def test_calculator(name, calc_func, params, expected_success=True):
    """Test a single calculator with given parameters"""
    try:
        result = calc_func(**params)
        success = result.get("success", False)
        
        if success and expected_success:
            total = result.get("total_price", 0)
            print(f"✅ {name}: ${total:.2f}")
            return True
        elif not success and not expected_success:
            error = result.get("error", "Unknown error")
            print(f"✅ {name}: Expected failure - {error}")
            return True
        else:
            error = result.get("error", "Unexpected result")
            print(f"❌ {name}: {error}")
            return False
    except Exception as e:
        print(f"❌ {name}: Exception - {e}")
        return False


def main():
    print("=" * 80)
    print("SHOPIFY CALCULATOR ALIGNMENT TEST - ALL 9 CALCULATORS")
    print("=" * 80)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # ========================================================================
    # 1. WIRE BOUND BOOKS (8 sizes)
    # ========================================================================
    print("1. WIRE BOUND BOOKS (8 sizes)")
    print("-" * 60)
    
    # Test valid size
    if test_calculator(
        "Wire Bound - A4 Portrait",
        calculate_wire_bound_books_shopify,
        {
            "quantity": 100,
            "internal_pages": 100,
            "finish_size": "A4 Portrait",
            "printed_front_cover": "300GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "None",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "300GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "None",
            "internal_stock": "Uncoated Bond 100GSM",
            "internal_print": "Black & White",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test invalid size (should fail)
    if test_calculator(
        "Wire Bound - Invalid Size",
        calculate_wire_bound_books_shopify,
        {
            "quantity": 100,
            "internal_pages": 100,
            "finish_size": "B5 Portrait",  # Invalid
            "artworks": 1
        },
        expected_success=False
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 2. SPIRAL BOUND BOOKS (8 sizes)
    # ========================================================================
    print("2. SPIRAL BOUND BOOKS (8 sizes)")
    print("-" * 60)
    
    # Test DL size (was broken, now fixed)
    if test_calculator(
        "Spiral Bound - DL Landscape",
        calculate_spiral_bound_books_shopify,
        {
            "quantity": 100,
            "internal_pages": 100,
            "finish_size": "DL Landscape",
            "printed_front_cover": "300GSM Satin",
            "internal_stock": "Uncoated Bond 100GSM",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test A6 size (was broken, now fixed)
    if test_calculator(
        "Spiral Bound - A6 Portrait",
        calculate_spiral_bound_books_shopify,
        {
            "quantity": 100,
            "internal_pages": 100,
            "finish_size": "A6 Portrait",
            "printed_front_cover": "300GSM Satin",
            "internal_stock": "Uncoated Bond 100GSM",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 3. PERFECT BOUND BOOKS (4 sizes)
    # ========================================================================
    print("3. PERFECT BOUND BOOKS (4 sizes)")
    print("-" * 60)
    
    # Test US Trade size (was broken, now fixed)
    if test_calculator(
        "Perfect Bound - US Trade",
        calculate_perfect_bound_books_shopify,
        {
            "quantity": 100,
            "printed_pages": 100,
            "finish_size": "US Trade - 152mm x 229mm",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "None",
            "content_print_type": "Black & White",
            "content_stock_type": "Uncoated Bond 100GSM"
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 4. SADDLE STITCH BOOKS (3 sizes)
    # ========================================================================
    print("4. SADDLE STITCH BOOKS (3 sizes)")
    print("-" * 60)
    
    # Test valid size
    if test_calculator(
        "Saddle Stitch - A5 Portrait",
        calculate_saddle_stitch_books_shopify,
        {
            "quantity": 100,
            "finish_size": "A5 Portrait",
            "cover_stock": "Satin 200GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "None",
            "printed_pages": "20pp",
            "content_print_type": "Black & White",
            "content_stock_type": "Uncoated Bond 100GSM",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test invalid size A6 (was in schema, now removed)
    if test_calculator(
        "Saddle Stitch - A6 Portrait (Invalid)",
        calculate_saddle_stitch_books_shopify,
        {
            "quantity": 100,
            "finish_size": "A6 Portrait",  # Invalid - not in JSON
            "artworks": 1
        },
        expected_success=False
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 5. FOLDED FLYERS (5 sizes - includes DL custom)
    # ========================================================================
    print("5. FOLDED FLYERS (5 sizes including DL)")
    print("-" * 60)
    
    # Test DL size (custom addition Jan 22, 2026)
    if test_calculator(
        "Folded Flyers - DL",
        calculate_folded_flyers_shopify,
        {
            "quantity": 500,
            "size": "DL",
            "stock": "Satin 150GSM",
            "print_type": "Colour",
            "double_sided": True,
            "folding": "Single Fold",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test A4 size
    if test_calculator(
        "Folded Flyers - A4",
        calculate_folded_flyers_shopify,
        {
            "quantity": 500,
            "size": "A4",
            "stock": "Satin 150GSM",
            "print_type": "Colour",
            "double_sided": True,
            "folding": "Single Fold",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 6. CORFLUTE SIGNS (Custom dimensions + presets)
    # ========================================================================
    print("6. CORFLUTE SIGNS (Preset + Custom dimensions)")
    print("-" * 60)
    
    # Test preset size
    if test_calculator(
        "Corflute - 600x900 Preset",
        calculate_corflute_signs_shopify,
        {
            "quantity": 10,
            "size_preset": "600x900",
            "thickness": "5mm",
            "double_sided": False,
            "eyelet_option": "none",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test custom dimensions
    if test_calculator(
        "Corflute - Custom 800x1000",
        calculate_corflute_signs_shopify,
        {
            "quantity": 10,
            "size_preset": "custom",
            "custom_width_mm": 800,
            "custom_height_mm": 1000,
            "thickness": "5mm",
            "double_sided": False,
            "eyelet_option": "none",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 7. ECONOMICAL BUSINESS CARDS (Fixed size 90x55mm)
    # ========================================================================
    print("7. ECONOMICAL BUSINESS CARDS (90x55mm)")
    print("-" * 60)
    
    # Test basic configuration
    if test_calculator(
        "Economical Cards - Double Sided",
        calculate_economical_business_cards_shopify,
        {
            "quantity": 500,
            "print_type": "Colour",
            "double_sided": True,
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test single sided
    if test_calculator(
        "Economical Cards - Single Sided",
        calculate_economical_business_cards_shopify,
        {
            "quantity": 1000,
            "print_type": "Colour",
            "double_sided": False,
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 8. PREMIUM BUSINESS CARDS (2 sizes + premium stocks)
    # ========================================================================
    print("8. PREMIUM BUSINESS CARDS (90x55mm, 90x45mm)")
    print("-" * 60)
    
    # Test standard size with Satin 350GSM
    if test_calculator(
        "Premium Cards - Standard 90x55mm",
        calculate_premium_business_cards_shopify,
        {
            "quantity": 500,
            "print_type": "Colour",
            "double_sided": True,
            "finish_size": "90mm x 55mm",
            "paper_stock": "Satin 350GSM",
            "celloglaze": "1 Side Gloss",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test slim size
    if test_calculator(
        "Premium Cards - Slim 90x45mm",
        calculate_premium_business_cards_shopify,
        {
            "quantity": 500,
            "print_type": "Colour",
            "double_sided": True,
            "finish_size": "90mm x 45mm",
            "paper_stock": "Satin 350GSM",
            "celloglaze": "2 Side Matt",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # 9. SPIRAL BOOKS SIMPLE (Alias for Spiral Bound)
    # ========================================================================
    print("9. SPIRAL BOOKS SIMPLE (Alias)")
    print("-" * 60)
    
    # Test that alias works (calls main Spiral Bound)
    if test_calculator(
        "Spiral Simple - A5 Portrait",
        calculate_spiral_books_simple_shopify,
        {
            "quantity": 100,
            "internal_pages": 100,
            "finish_size": "A5 Portrait",
            "printed_front_cover": "300GSM Satin",
            "internal_stock": "Uncoated Bond 100GSM",
            "artworks": 1
        }
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed} ({tests_passed/(tests_passed+tests_failed)*100:.1f}%)")
    print(f"Failed: {tests_failed} ({tests_failed/(tests_passed+tests_failed)*100:.1f}%)")
    print()
    
    if tests_failed == 0:
        print("✅ ALL TESTS PASSED - All 9 calculators aligned!")
    else:
        print(f"❌ {tests_failed} test(s) failed - Review alignment issues")
    
    print("=" * 80)
    
    return tests_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
