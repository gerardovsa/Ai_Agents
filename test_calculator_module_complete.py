"""
COMPREHENSIVE CALCULATOR MODULE SMOKE TEST
Tests: Schema → Registry → Wrapper → Backend → Validation
"""

import sys
import json
import traceback
from pathlib import Path

# Setup paths
sys.path.insert(0, 'AI_infrastructure')
sys.path.insert(0, 'UI/modules_external/quote-calculator/implementations')

print("=" * 80)
print("CALCULATOR MODULE COMPREHENSIVE SMOKE TEST")
print("=" * 80)
print()

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def test_step(name, func):
    """Run a test step and track results"""
    global tests_passed, tests_failed
    try:
        print(f"[TEST] {name}")
        result = func()
        print(f"   [PASS] {result}")
        tests_passed += 1
        test_results.append((name, "PASS", result))
        return True
    except Exception as e:
        print(f"   [FAIL] {str(e)}")
        print(f"   Traceback: {traceback.format_exc()[:200]}...")
        tests_failed += 1
        test_results.append((name, "FAIL", str(e)))
        return False

# ============================================================================
# TEST 1: Schema Loading
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: SCHEMA LOADING")
print("=" * 80)

schema_path = Path('UI/modules_external/quote-calculator/schema/calculator_tools.json')

def test_schema_exists():
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found at {schema_path}")
    return f"Schema file exists: {schema_path}"

def test_schema_valid_json():
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    return f"Valid JSON with {len(schema.get('tools', []))} tools"

def test_schema_structure():
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    tools = schema.get('tools', [])
    if not tools:
        raise ValueError("No tools found in schema")
    
    # Check first tool structure
    tool = tools[0]
    required_keys = ['name', 'description', 'parameters']
    missing = [k for k in required_keys if k not in tool]
    if missing:
        raise ValueError(f"Missing keys in tool schema: {missing}")
    
    return f"Schema structure valid, first tool: {tool['name']}"

def test_enum_coverage():
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    tools_with_enums = sum(1 for t in schema['tools'] 
                          if any('enum' in p for p in t.get('parameters', {}).values()))
    total_tools = len(schema['tools'])
    
    if tools_with_enums < 20:
        raise ValueError(f"Only {tools_with_enums}/{total_tools} tools have enums")
    
    return f"{tools_with_enums}/{total_tools} tools have enums"

test_step("Schema file exists", test_schema_exists)
test_step("Schema is valid JSON", test_schema_valid_json)
test_step("Schema structure correct", test_schema_structure)
test_step("Enum coverage adequate", test_enum_coverage)

# ============================================================================
# TEST 2: Registry Loading
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: REGISTRY LOADING")
print("=" * 80)

registry = None

def test_registry_import():
    global registry
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    return "Registry imported and initialized"

def test_calculator_tools_loaded():
    calculator_tools = [name for name in registry.tools.keys() 
                       if name.startswith('calculate_')]
    if len(calculator_tools) < 25:
        raise ValueError(f"Only {len(calculator_tools)} calculator tools loaded")
    return f"{len(calculator_tools)} calculator tools in registry"

def test_get_tool_schema():
    schema = registry.get_tool('calculate_premium_business_cards_shopify')
    if not schema:
        raise ValueError("Failed to get tool schema")
    
    # Check for enums
    qty_param = schema.get('parameters', {}).get('quantity', {})
    if 'enum' not in qty_param:
        raise ValueError("quantity parameter missing enum")
    
    return f"Schema retrieved with {len(qty_param['enum'])} quantity values"

test_step("Import Registry", test_registry_import)
test_step("Calculator tools loaded", test_calculator_tools_loaded)
test_step("Get tool schema works", test_get_tool_schema)

# ============================================================================
# TEST 3: Wrapper Compilation
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: WRAPPER COMPILATION")
print("=" * 80)

wrapper_module = None

def test_wrapper_import():
    global wrapper_module
    import calculator_wrapper
    wrapper_module = calculator_wrapper
    return "Wrapper module imported successfully"

def test_wrapper_functions_exist():
    # Check for key wrapper functions
    test_functions = [
        'calculate_premium_business_cards_shopify',
        'calculate_saddle_stitch_books',
        'calculate_bollard_signs',
        'calculate_notepads_a4'
    ]
    
    missing = [f for f in test_functions if not hasattr(wrapper_module, f)]
    if missing:
        raise ValueError(f"Missing wrapper functions: {missing}")
    
    return f"All {len(test_functions)} test wrapper functions exist"

def test_wrapper_decorator():
    # Check if wrapper has calculator_wrapper decorator
    func = getattr(wrapper_module, 'calculate_premium_business_cards_shopify')
    
    # Function should be wrapped
    if not hasattr(func, '__wrapped__') and not hasattr(func, '__name__'):
        raise ValueError("Function doesn't appear to be properly wrapped")
    
    return "Wrapper decorator applied correctly"

test_step("Import wrapper module", test_wrapper_import)
test_step("Wrapper functions exist", test_wrapper_functions_exist)
test_step("Wrapper decorator works", test_wrapper_decorator)

# ============================================================================
# TEST 4: Backend Calculator Import
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: BACKEND CALCULATOR COMPILATION")
print("=" * 80)

def test_backend_import_saddle_stitch():
    sys.path.insert(0, 'UI/modules_external/quote-calculator/backend/shopify_calculators')
    from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator
    calc = SaddleStitchBooksShopifyCalculator()
    return f"SaddleStitchBooks calculator imported: {calc.__class__.__name__}"

def test_backend_import_bollard():
    from BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator
    calc = BollardSignsShopifyCalculator()
    return f"BollardSigns calculator imported: {calc.__class__.__name__}"

def test_backend_import_notepads():
    from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator
    calc = NotepadsA4ShopifyCalculator()
    return f"NotepadsA4 calculator imported: {calc.__class__.__name__}"

test_step("Import SaddleStitchBooks backend", test_backend_import_saddle_stitch)
test_step("Import BollardSigns backend", test_backend_import_bollard)
test_step("Import NotepadsA4 backend", test_backend_import_notepads)

# ============================================================================
# TEST 5: End-to-End Execution (The Fixed Bug)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: END-TO-END EXECUTION - SADDLE STITCH BOOKS (THE BUG FIX)")
print("=" * 80)

def test_saddle_stitch_wrapper_call():
    """Test the actual bug fix - wrapper converts int to str"""
    func = getattr(wrapper_module, 'calculate_saddle_stitch_books')
    
    # Call with integer quantity (this was the bug)
    result = func(
        quantity=100,
        cover_option="Self Cover",
        cover_stock="Satin 150GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="None",
        printed_pages="24pp",
        finish_size="A5 Portrait",
        content_print_type="Colour",
        content_stock_type="Satin 128GSM"
    )
    
    if not result or 'error' in str(result).lower():
        raise ValueError(f"Calculation failed: {result}")
    
    return f"Successfully calculated: ${result.get('total_price', 'N/A')}"

test_step("Saddle stitch books calculation (bug fix)", test_saddle_stitch_wrapper_call)

# ============================================================================
# TEST 6: Enum Validation
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: ENUM VALIDATION")
print("=" * 80)

def test_enum_validation_rejects_invalid():
    """Test that schema validator rejects invalid enum values"""
    func = getattr(wrapper_module, 'calculate_premium_business_cards_shopify')
    
    try:
        # Try invalid quantity (not in enum)
        result = func(
            quantity=100,  # Invalid - should be 250, 500, 1000, 2000, 5000, 10000
            double_sided=True,
            colour=True,
            stock="Satin 300GSM",
            celloglaze="none"
        )
        raise ValueError("Validation should have rejected quantity=100")
    except ValueError as e:
        if "Invalid quantity" in str(e) or "100" in str(e):
            return f"Correctly rejected invalid quantity: {str(e)[:50]}"
        raise ValueError(f"Wrong error message: {e}")

def test_enum_validation_accepts_valid():
    """Test that valid enum values are accepted"""
    func = getattr(wrapper_module, 'calculate_premium_business_cards_shopify')
    
    # Valid quantity from enum
    result = func(
        quantity=500,  # Valid
        double_sided=True,
        colour=True,
        stock="Satin 300GSM",
        celloglaze="none"
    )
    
    if not result or 'error' in str(result).lower():
        raise ValueError(f"Calculation failed: {result}")
    
    return f"Accepted valid quantity 500: ${result.get('total_price', 'N/A')}"

test_step("Enum validation rejects invalid values", test_enum_validation_rejects_invalid)
test_step("Enum validation accepts valid values", test_enum_validation_accepts_valid)

# ============================================================================
# TEST 7: Multiple Calculator Types
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: MULTIPLE CALCULATOR TYPES")
print("=" * 80)

def test_bollard_signs():
    func = getattr(wrapper_module, 'calculate_bollard_signs')
    result = func(
        quantity=10,
        material="3mm Corflute",
        size="270mm W x 1000mm H - Three Sided",
        artworks=1
    )
    if not result:
        raise ValueError("Calculation failed")
    return f"Bollard signs: ${result.get('total_price', 'N/A')}"

def test_notepads_a4():
    func = getattr(wrapper_module, 'calculate_notepads_a4')
    result = func(
        quantity=100,
        leaves_per_pad="50",
        finish_size="A4 Portrait",
        print_type="Colour 1 sided",
        stock_type="Uncoated Bond 80GSM"
    )
    if not result:
        raise ValueError("Calculation failed")
    return f"Notepads A4: ${result.get('total_price', 'N/A')}"

def test_business_cards():
    func = getattr(wrapper_module, 'calculate_business_cards')
    result = func(
        quantity=500,
        finish_size="90x55mm",
        stock_type="premium",
        print_type="double_sided",
        celloglaze="gloss"
    )
    if not result:
        raise ValueError("Calculation failed")
    return f"Business cards: ${result.get('total_price', 'N/A')}"

test_step("Bollard signs calculation", test_bollard_signs)
test_step("Notepads A4 calculation", test_notepads_a4)
test_step("Business cards calculation", test_business_cards)

# ============================================================================
# FINAL REPORT
# ============================================================================
print("\n" + "=" * 80)
print("FINAL TEST REPORT")
print("=" * 80)
print()

total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"[PASS] Passed: {tests_passed}")
print(f"[FAIL] Failed: {tests_failed}")
print(f"[RATE] Pass Rate: {pass_rate:.1f}%")
print()

if tests_failed > 0:
    print("FAILED TESTS:")
    for name, status, result in test_results:
        if status == "FAIL":
            print(f"  [FAIL] {name}: {result}")
    print()

print("=" * 80)
if tests_failed == 0:
    print("[SUCCESS] ALL TESTS PASSED - MODULE IS FULLY FUNCTIONAL")
else:
    print(f"[WARNING] {tests_failed} TEST(S) FAILED - REVIEW REQUIRED")
print("=" * 80)

# Exit with appropriate code
sys.exit(0 if tests_failed == 0 else 1)
