"""
Comprehensive Calculator Test Suite

Tests ALL calculator implementations to ensure they handle parameter parsing correctly.
This checks for the same bug found in inhouse_calculate_quote across all calculator types.

Date: December 8, 2025
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.registry_v3 import RegistryV3


# ==================== TEST DATA ====================

CALCULATOR_TEST_CASES = {
    "business_cards": {
        "tool_name": "calculate_business_cards",
        "valid_params": {
            "quantity": 500,
            "stock_type": "satin_350gsm",
            "sides": 2,
            "finish_size": "90mm x 55mm",
            "celloglaze": "gloss",
            "print_type": "colour",
            "artworks": 1
        }
    },
    
    "flyers": {
        "tool_name": "calculate_flyers",
        "valid_params": {
            "quantity": 1000,
            "width": 210,
            "height": 297,
            "gsm": 150,
            "print_side1": "4C",
            "print_side2": "0C"
        }
    },
    
    "booklets": {
        "tool_name": "calculate_booklets",
        "valid_params": {
            "quantity": 100,
            "pages": 16,
            "width": 210,
            "height": 297,
            "stock_type_id": 29,
            "internal_gsm": 100
        }
    },
    
    "perfect_bound_books": {
        "tool_name": "calculate_perfect_bound_books",
        "valid_params": {
            "quantity": 100,
            "pages": 60,
            "width": 148,
            "height": 210,
            "stock_type_id": 29,
            "internal_stock_gsm": 100
        }
    },
    
    "letterheads": {
        "tool_name": "calculate_letterheads",
        "valid_params": {
            "quantity": 500,
            "stock_type_id": 29,
            "gsm": 100,
            "colors": "4C"
        }
    },
    
    "corflute_signs": {
        "tool_name": "calculate_corflute_signs",
        "valid_params": {
            "quantity": 10,
            "size_preset": "A4",
            "thickness": "3mm",
            "double_sided": False
        }
    },
    
    # GOD Calculators
    "flyers_god": {
        "tool_name": "calculate_flyers_god",
        "valid_params": {
            "quantity": 1000,
            "width": 210,
            "height": 297,
            "gsm": 150,
            "print_sides": 2
        }
    },
    
    "letterheads_god": {
        "tool_name": "calculate_letterheads_god",
        "valid_params": {
            "quantity": 500,
            "stock_id": 29,
            "colors": 4
        }
    },
    
    "perfect_bound_books_god": {
        "tool_name": "calculate_perfect_bound_books_god",
        "valid_params": {
            "quantity": 100,
            "pages": 60,
            "width": 148,
            "height": 210
        }
    },
    
    "corflute_signs_god": {
        "tool_name": "calculate_corflute_signs_god",
        "valid_params": {
            "quantity": 10,
            "width": 210,
            "height": 297,
            "thickness": 3
        }
    },
    
    # Shopify Calculators
    "economical_business_cards_shopify": {
        "tool_name": "calculate_economical_business_cards_shopify",
        "valid_params": {
            "quantity": 500,
            "stock": "300gsm",
            "sides": "double"
        }
    },
    
    "premium_business_cards_shopify": {
        "tool_name": "calculate_premium_business_cards_shopify",
        "valid_params": {
            "quantity": 500,
            "stock": "350gsm satin",
            "finish": "gloss cello"
        }
    },
    
    "folded_flyers_shopify": {
        "tool_name": "calculate_folded_flyers_shopify",
        "valid_params": {
            "quantity": 1000,
            "print_sides": "double",
            "finish_size": "a4",
            "fold_type": "single"
        }
    },
    
    "wire_bound_books_shopify": {
        "tool_name": "calculate_wire_bound_books_shopify",
        "valid_params": {
            "quantity": 50,
            "pages": 40,
            "size": "a4"
        }
    },
    
    "spiral_bound_books_shopify": {
        "tool_name": "calculate_spiral_bound_books_shopify",
        "valid_params": {
            "quantity": 50,
            "pages": 40,
            "size": "a4"
        }
    }
}


# ==================== TEST FUNCTIONS ====================

def test_calculator_with_dict(calc_name: str, tool_name: str, params: dict, registry: RegistryV3) -> tuple:
    """Test calculator with dict parameters"""
    try:
        result = registry.execute_tool(tool_name=tool_name, **params)
        
        if result.get("success"):
            return True, "SUCCESS", result.get("cost_inc_gst", "N/A")
        else:
            error = result.get("error", "Unknown error")
            if "'str' object has no attribute 'items'" in str(error):
                return False, "PARSING_BUG", error
            else:
                return False, "VALIDATION_ERROR", error
    except Exception as e:
        if "'str' object has no attribute 'items'" in str(e):
            return False, "PARSING_BUG", str(e)
        else:
            return False, "EXCEPTION", str(e)


def test_calculator_with_json_string(calc_name: str, tool_name: str, params: dict, registry: RegistryV3) -> tuple:
    """Test calculator with JSON string parameters (bug scenario)"""
    try:
        # Convert params to JSON string
        json_params = json.dumps(params)
        
        # Create tool call with JSON string
        result = registry.execute_tool(tool_name=tool_name, parameters=json_params)
        
        if result.get("success"):
            return True, "SUCCESS", result.get("cost_inc_gst", "N/A")
        else:
            error = result.get("error", "Unknown error")
            if "'str' object has no attribute 'items'" in str(error):
                return False, "PARSING_BUG", error
            else:
                return False, "VALIDATION_ERROR", error
    except Exception as e:
        if "'str' object has no attribute 'items'" in str(e):
            return False, "PARSING_BUG", str(e)
        else:
            return False, "EXCEPTION", str(e)


def run_comprehensive_calculator_tests():
    """Run tests on all calculators"""
    print("\n" + "="*80)
    print("COMPREHENSIVE CALCULATOR TEST SUITE")
    print("="*80)
    print(f"Testing {len(CALCULATOR_TEST_CASES)} calculator implementations")
    print("Checking for parameter parsing bugs across all calculators")
    print("="*80)
    
    registry = RegistryV3()
    
    results = {
        "dict_tests": {},
        "json_string_tests": {}
    }
    
    parsing_bugs_found = []
    working_calculators = []
    failed_calculators = []
    
    # Test each calculator
    for calc_name, config in CALCULATOR_TEST_CASES.items():
        tool_name = config["tool_name"]
        params = config["valid_params"]
        
        print(f"\n{'='*80}")
        print(f"Testing: {calc_name} ({tool_name})")
        print(f"{'='*80}")
        
        # Test 1: Dict parameters
        print(f"\n[Test 1] Dict Parameters...")
        dict_success, dict_status, dict_result = test_calculator_with_dict(
            calc_name, tool_name, params, registry
        )
        results["dict_tests"][calc_name] = {
            "success": dict_success,
            "status": dict_status,
            "result": dict_result
        }
        
        if dict_success:
            print(f"[PASS] Dict parameters work")
            working_calculators.append(calc_name)
        elif dict_status == "PARSING_BUG":
            print(f"[BUG] PARSING BUG DETECTED: {dict_result[:100]}")
            parsing_bugs_found.append(f"{calc_name} (dict)")
        else:
            print(f"[WARN] {dict_status}: {dict_result[:100]}")
            failed_calculators.append(calc_name)
        
        # Test 2: JSON string parameters (known bug scenario)
        print(f"\n[Test 2] JSON String Parameters (Bug Check)...")
        json_success, json_status, json_result = test_calculator_with_json_string(
            calc_name, tool_name, params, registry
        )
        results["json_string_tests"][calc_name] = {
            "success": json_success,
            "status": json_status,
            "result": json_result
        }
        
        if json_success:
            print(f"[PASS] JSON string parameters work (fix applied)")
        elif json_status == "PARSING_BUG":
            print(f"[BUG] PARSING BUG DETECTED: {json_result[:100]}")
            parsing_bugs_found.append(f"{calc_name} (json_string)")
        else:
            print(f"[WARN] {json_status}: Different error (not parsing bug)")
    
    # Generate summary report
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    total_tests = len(CALCULATOR_TEST_CASES) * 2
    passed_tests = sum(1 for r in results["dict_tests"].values() if r["success"])
    passed_tests += sum(1 for r in results["json_string_tests"].values() if r["success"])
    
    print(f"\nTotal Tests Run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    # Parsing bugs report
    print(f"\n{'='*80}")
    print("PARAMETER PARSING BUGS FOUND")
    print(f"{'='*80}")
    if parsing_bugs_found:
        print(f"[CRITICAL] {len(parsing_bugs_found)} calculators have the parsing bug")
        for bug in parsing_bugs_found:
            print(f"   - {bug}")
        print("\n[WARNING] These calculators need the same fix applied:")
        print("   Add JSON deserialization: if isinstance(params, str): params = json.loads(params)")
    else:
        print("[OK] No parameter parsing bugs found!")
        print("   All calculators handle both dict and JSON string parameters correctly")
    
    # Working calculators
    print(f"\n{'='*80}")
    print("WORKING CALCULATORS")
    print(f"{'='*80}")
    if working_calculators:
        print(f"Total: {len(working_calculators)}")
        for calc in working_calculators:
            cost = results["dict_tests"][calc]["result"]
            print(f"   [OK] {calc}: ${cost if isinstance(cost, (int, float)) else 'N/A'}")
    else:
        print("[FAIL] No calculators are working correctly")
    
    # Failed calculators (non-parsing errors)
    print(f"\n{'='*80}")
    print("CALCULATORS WITH OTHER ISSUES")
    print(f"{'='*80}")
    if failed_calculators:
        print(f"Total: {len(failed_calculators)}")
        for calc in failed_calculators:
            error = results["dict_tests"][calc]["result"]
            print(f"   [WARN] {calc}")
            print(f"      Error: {error[:100]}")
    else:
        print("[OK] No other issues found")
    
    # Detailed results table
    print(f"\n{'='*80}")
    print("DETAILED RESULTS TABLE")
    print(f"{'='*80}")
    print(f"{'Calculator':<35} {'Dict':<15} {'JSON String':<15}")
    print("-" * 80)
    
    for calc_name in CALCULATOR_TEST_CASES.keys():
        dict_result = results["dict_tests"][calc_name]
        json_result = results["json_string_tests"][calc_name]
        
        dict_symbol = "[OK]" if dict_result["success"] else ("[BUG]" if dict_result["status"] == "PARSING_BUG" else "[FAIL]")
        json_symbol = "[OK]" if json_result["success"] else ("[BUG]" if json_result["status"] == "PARSING_BUG" else "[FAIL]")
        
        print(f"{calc_name:<35} {dict_symbol:<15} {json_symbol:<15}")
    
    print("="*80)
    
    # Final recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if parsing_bugs_found:
        print("[CRITICAL] ACTION REQUIRED:")
        print("   Apply the same fix to all calculators with parsing bugs")
        print("   See: INHOUSE_CALCULATOR_FIXES.md for implementation details")
    elif passed_tests == total_tests:
        print("[SUCCESS] ALL CALCULATORS PASSING!")
        print("   No action required - all implementations are correct")
    else:
        print("[WARN] MIXED RESULTS:")
        print(f"   {len(parsing_bugs_found)} parsing bugs to fix")
        print(f"   {len(failed_calculators)} other issues to investigate")
    
    print("="*80)
    
    return len(parsing_bugs_found) == 0


if __name__ == "__main__":
    success = run_comprehensive_calculator_tests()
    sys.exit(0 if success else 1)
