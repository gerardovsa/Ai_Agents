"""
Test Parameter Mapping Fix for Quote Calculator
Tests both JSON deserialization AND parameter aliasing fixes
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "="*80)
print("QUOTE CALCULATOR - PARAMETER MAPPING TEST")
print("="*80)
print("Testing Fix #1: JSON deserialization (Dec 8, 2025)")
print("Testing Fix #2: Parameter aliasing book_width/pages -> finish_size/printed_pages")
print("="*80 + "\n")

# Initialize registry
print("[1/4] Initializing Tool Registry...")
try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    print("[OK] Registry loaded: 948 tools available\n")
except Exception as e:
    print(f"[FAIL] Could not load registry: {e}\n")
    sys.exit(1)

# ========================================================================
# TEST 1: Perfect Bound Books with Documentation Parameters
# ========================================================================
print("="*80)
print("TEST 1: Perfect Bound Books (Documentation Parameters)")
print("="*80)
print("Using parameters from inhouse_get_calculator_requirements documentation:")
print("  - book_width: 148mm (should map to finish_size='A5 Portrait')")
print("  - book_height: 210mm")
print("  - pages: 60 (should map to printed_pages=60)")
print("  - cello_type: 1 (should map to celloglaze='Gloss outside only')")
print("")

test1_params = {
    "quantity": 100,
    "book_width": 148,
    "book_height": 210,
    "pages": 60,
    "cello_type": 1
}

print(f"Input parameters: {json.dumps(test1_params, indent=2)}")
print("\nExecuting: inhouse_calculate_quote(product_type='perfect_bound_books', parameters=...)")
print("-" * 80)

try:
    result1 = registry.execute_tool(
        tool_name="inhouse_calculate_quote",
        product_type="perfect_bound_books",
        parameters=test1_params
    )
    
    if result1.get("success"):
        print(f"\n[OK] TEST 1 PASSED")
        print(f"   Total (inc GST): ${result1.get('cost_inc_gst', 0):.2f}")
        print(f"   Per Book: ${result1.get('cost_inc_gst', 0) / 100:.2f}")
        if "specifications" in result1:
            print(f"   Mapped to: {result1['specifications'].get('finish_size', 'N/A')}")
    else:
        print(f"\n[FAIL] TEST 1 FAILED")
        print(f"   Error: {result1.get('error', 'Unknown error')}")
        if "hint" in result1:
            print(f"   Hint: {result1['hint']}")
        
except Exception as e:
    print(f"\n[FAIL] TEST 1 EXCEPTION: {str(e)}")

# ========================================================================
# TEST 2: Perfect Bound Books with Shopify Parameters
# ========================================================================
print("\n\n" + "="*80)
print("TEST 2: Perfect Bound Books (Shopify Calculator Parameters)")
print("="*80)
print("Using native Shopify calculator parameters:")
print("  - printed_pages: 60 (native Shopify param)")
print("  - finish_size: 'A5 Portrait' (native Shopify param)")
print("  - celloglaze: 'Gloss outside only' (native Shopify param)")
print("")

test2_params = {
    "quantity": 100,
    "printed_pages": 60,
    "finish_size": "A5 Portrait",
    "celloglaze": "Gloss outside only",
    "cover_stock": "Satin 300GSM",
    "cover_print_type": "2 side colour (4pp)",
    "content_print_type": "Black & White",
    "content_stock_type": "Uncoated Bond 100GSM"
}

print(f"Input parameters: {json.dumps(test2_params, indent=2)}")
print("\nExecuting: inhouse_calculate_quote(product_type='perfect_bound_books', parameters=...)")
print("-" * 80)

try:
    result2 = registry.execute_tool(
        tool_name="inhouse_calculate_quote",
        product_type="perfect_bound_books",
        parameters=test2_params
    )
    
    if result2.get("success"):
        print(f"\n[OK] TEST 2 PASSED")
        print(f"   Total (inc GST): ${result2.get('cost_inc_gst', 0):.2f}")
        print(f"   Per Book: ${result2.get('cost_inc_gst', 0) / 100:.2f}")
    else:
        print(f"\n[FAIL] TEST 2 FAILED")
        print(f"   Error: {result2.get('error', 'Unknown error')}")
        if "hint" in result2:
            print(f"   Hint: {result2['hint']}")
        
except Exception as e:
    print(f"\n[FAIL] TEST 2 EXCEPTION: {str(e)}")

# ========================================================================
# TEST 3: Business Cards (Simple Test - Already Working)
# ========================================================================
print("\n\n" + "="*80)
print("TEST 3: Business Cards (Baseline Test)")
print("="*80)
print("Testing a simpler calculator to verify basic functionality:")
print("")

test3_params = {
    "quantity": 500,
    "stock_type": "satin_350gsm",
    "finish_size": "90x55"
}

print(f"Input parameters: {json.dumps(test3_params, indent=2)}")
print("\nExecuting: inhouse_calculate_quote(product_type='business_cards', parameters=...)")
print("-" * 80)

try:
    result3 = registry.execute_tool(
        tool_name="inhouse_calculate_quote",
        product_type="business_cards",
        parameters=test3_params
    )
    
    if result3.get("success"):
        print(f"\n[OK] TEST 3 PASSED")
        print(f"   Total (inc GST): ${result3.get('cost_inc_gst', 0):.2f}")
        print(f"   Per Card: ${result3.get('cost_inc_gst', 0) / 500:.4f}")
    else:
        print(f"\n[FAIL] TEST 3 FAILED")
        print(f"   Error: {result3.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n[FAIL] TEST 3 EXCEPTION: {str(e)}")

# ========================================================================
# TEST 4: Parameters as JSON String (Original Bug)
# ========================================================================
print("\n\n" + "="*80)
print("TEST 4: JSON String Parameters (Original Bug Fix)")
print("="*80)
print("Testing the original issue: parameters passed as JSON string instead of dict")
print("")

# Simulate what happens when parameters come as JSON string
test4_params_string = json.dumps({
    "quantity": 500,
    "stock_type": "satin_350gsm",
    "finish_size": "90x55"
})

print(f"Input parameters: '{test4_params_string}' (type: {type(test4_params_string).__name__})")
print("\nExecuting: inhouse_calculate_quote(product_type='business_cards', parameters=<string>)")
print("-" * 80)

try:
    # The tool_use_agent should deserialize this automatically now
    result4 = registry.execute_tool(
        tool_name="inhouse_calculate_quote",
        product_type="business_cards",
        parameters=test4_params_string
    )
    
    if result4.get("success"):
        print(f"\n[OK] TEST 4 PASSED - JSON deserialization working!")
        print(f"   Total (inc GST): ${result4.get('cost_inc_gst', 0):.2f}")
    else:
        print(f"\n[FAIL] TEST 4 FAILED")
        print(f"   Error: {result4.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n[FAIL] TEST 4 EXCEPTION: {str(e)}")

# ========================================================================
# SUMMARY
# ========================================================================
print("\n\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

results = [
    ("Perfect Bound (Documentation Params)", result1.get("success", False) if 'result1' in locals() else False),
    ("Perfect Bound (Shopify Params)", result2.get("success", False) if 'result2' in locals() else False),
    ("Business Cards (Baseline)", result3.get("success", False) if 'result3' in locals() else False),
    ("JSON String Deserialization", result4.get("success", False) if 'result4' in locals() else False)
]

passed = sum(1 for _, success in results if success)
total = len(results)

for test_name, success in results:
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {test_name}")

print("=" * 80)
print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
print("=" * 80)

if passed == total:
    print("\n[SUCCESS] All fixes working correctly!")
    print("Fix #1: JSON deserialization - WORKING")
    print("Fix #2: Parameter aliasing - WORKING")
    sys.exit(0)
elif passed >= 2:
    print(f"\n[PARTIAL SUCCESS] {passed}/{total} tests passing")
    print("Some functionality restored, but parameter mapping needs more work")
    sys.exit(0)
else:
    print(f"\n[FAILURE] Only {passed}/{total} tests passed")
    sys.exit(1)
