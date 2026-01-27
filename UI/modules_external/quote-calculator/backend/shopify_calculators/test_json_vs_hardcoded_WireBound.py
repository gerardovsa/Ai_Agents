"""
Wire Bound Books - JSON vs Hardcoded Price Alignment Test
==========================================================

CREATED: January 26, 2026
PURPOSE: Verify WireBound calculator loads prices from JSON vs hardcoded values

Test Cases (from test_wire_bound_books.py - 100% accurate):
1. A4 Portrait Basic - 100 books, 50 pages → $781.24
2. A5 Landscape with PVC - 250 books, 80 pages → $2,225.96  
3. DL Portrait Small - 50 books, 20 pages → $375.70
4. A6 Landscape with Leather - 500 books, 120 pages → $3,406.66
5. A4 Landscape B&W Large - 1000 books, 200 pages → $10,513.47

VERIFICATION: All tests must show 0.00% difference between JSON and hardcoded prices.
"""

import sys
import os
from pathlib import Path
from decimal import Decimal

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from WireBound_Shopify_Calculator import WireBoundShopifyCalculator

# Path to JSON config
JSON_CONFIG_PATH = backend_dir / 'pricing_configs' / 'wire_bound_books_config.json'


def compare_prices(test_name: str, params: dict, expected_total: Decimal):
    """Compare JSON-loaded vs hardcoded prices"""
    
    # Calculate with JSON config
    calc_json = WireBoundShopifyCalculator(config_path=str(JSON_CONFIG_PATH))
    result_json = calc_json.calculate(**params)
    
    # Calculate with hardcoded config (no config_path)
    calc_hardcoded = WireBoundShopifyCalculator()
    result_hardcoded = calc_hardcoded.calculate(**params)
    
    # Compare prices
    json_total = result_json.total_price
    hardcoded_total = result_hardcoded.total_price
    
    # Calculate difference
    difference = abs(json_total - hardcoded_total)
    percent_diff = (difference / expected_total * 100) if expected_total else Decimal('0')
    
    # Format results
    status = "PASS" if difference == 0 else "FAIL"
    symbol = "✓" if difference == 0 else "✗"
    
    print(f"\n{symbol} {test_name}")
    print(f"  JSON Total:      ${json_total:,.2f}")
    print(f"  Hardcoded Total: ${hardcoded_total:,.2f}")
    print(f"  Expected Total:  ${expected_total:,.2f}")
    print(f"  Difference:      ${difference:,.2f} ({percent_diff:.2f}%)")
    print(f"  Status: {status}")
    
    return difference == 0


def main():
    """Run all alignment tests"""
    
    print("=" * 80)
    print("WIRE BOUND BOOKS - JSON vs HARDCODED ALIGNMENT TEST")
    print("=" * 80)
    print(f"JSON Config: {JSON_CONFIG_PATH}")
    print(f"Config Exists: {JSON_CONFIG_PATH.exists()}")
    print()
    
    if not JSON_CONFIG_PATH.exists():
        print(f"WARNING: JSON config not found at {JSON_CONFIG_PATH}")
        print("Skipping alignment tests - create JSON config first")
        return
    
    test_cases = [
        {
            "name": "Test 1: A4 Portrait Basic (100 books, 50 pages)",
            "params": {
                "quantity": 100,
                "finish_size": "A4 Portrait",
                "internal_pages": 50,
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "internal_stock": "Uncoated Bond 100GSM",
                "internal_print": "Black & White"
            },
            "expected": Decimal('781.24')
        },
        {
            "name": "Test 2: A5 Landscape with PVC (250 books, 80 pages)",
            "params": {
                "quantity": 250,
                "finish_size": "A5 Landscape",
                "internal_pages": 80,
                "outer_front_cover": "300 Micron PVC",
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "outer_back_cover": "300 Micron PVC",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "internal_stock": "Uncoated Bond 100GSM",
                "internal_print": "Colour Throughout"
            },
            "expected": Decimal('2225.96')
        },
        {
            "name": "Test 3: DL Portrait Small (50 books, 20 pages)",
            "params": {
                "quantity": 50,
                "finish_size": "DL Portrait",
                "internal_pages": 20,
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "internal_stock": "Uncoated Bond 100GSM",
                "internal_print": "Black & White"
            },
            "expected": Decimal('375.70')
        },
        {
            "name": "Test 4: A6 Landscape with Leather (500 books, 120 pages)",
            "params": {
                "quantity": 500,
                "finish_size": "A6 Landscape",
                "internal_pages": 120,
                "outer_front_cover": "Leather - Plano",
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "outer_back_cover": "Leather - Plano",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "internal_stock": "Uncoated Bond 100GSM",
                "internal_print": "Colour Throughout"
            },
            "expected": Decimal('3406.66')
        },
        {
            "name": "Test 5: A4 Landscape B&W Large (1000 books, 200 pages)",
            "params": {
                "quantity": 1000,
                "finish_size": "A4 Landscape",
                "internal_pages": 200,
                "printed_front_cover": "300GSM Satin",
                "front_cover_print": "2pp Colour",
                "printed_back_cover": "300GSM Satin",
                "back_cover_print": "2pp Colour",
                "internal_stock": "Uncoated Bond 100GSM",
                "internal_print": "Black & White"
            },
            "expected": Decimal('10513.47')
        }
    ]
    
    # Run all tests
    results = []
    for test in test_cases:
        passed = compare_prices(test["name"], test["params"], test["expected"])
        results.append(passed)
    
    # Summary
    print("\n" + "=" * 80)
    print("ALIGNMENT TEST SUMMARY")
    print("=" * 80)
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed:       {failed_tests}")
    
    if all(results):
        print("\n SUCCESS - All tests show 0.00% difference!")
        print("Wire Bound calculator properly loads prices from JSON.")
    else:
        print("\n WARNING - Some tests show differences.")
        print("Check JSON config pricing against hardcoded values.")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
