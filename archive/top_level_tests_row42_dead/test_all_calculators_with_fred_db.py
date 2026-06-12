"""
Test all InHouse Print calculators with real FRED database connection.
Systematically tests each calculator to discover actual parameter requirements.
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'inhouse_modules'))

import json
from inhouse_modules.db_connector import InHousePrintDB
from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(title)
    print("="*80)

def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def test_calculator(calc, method_name, test_name, **params):
    """Test a specific calculator with given parameters"""
    print(f"\n[TEST] {test_name}")
    print(f"  Method: {method_name}")
    print(f"  Params: {json.dumps(params, indent=4)}")
    
    try:
        # Get the calculator method
        if not hasattr(calc, method_name):
            print(f"  [FAIL] Calculator has no method '{method_name}'")
            return False, {"error": f"Method {method_name} not found"}
        
        calc_method = getattr(calc, method_name)
        
        # Call the calculator with unpacked parameters
        result = calc_method(**params)
        
        # Check if result is a dict with success or just a cost
        if isinstance(result, dict):
            if result.get('success') or 'cost_inc_gst' in result:
                cost = result.get('cost_inc_gst', result.get('price', 'N/A'))
                print(f"  [PASS] Cost: ${cost:.2f}" if isinstance(cost, (int, float)) else f"  [PASS] Result: {cost}")
                return True, result
            else:
                print(f"  [FAIL] {result.get('error', 'Unknown error')}")
                return False, result
        else:
            # Result might be just a number
            print(f"  [PASS] Cost: ${result:.2f}")
            return True, {"cost_inc_gst": result}
        
            
    except TypeError as e:
        error_msg = str(e)
        print(f"  [ERROR] TypeError: {error_msg}")
        
        # Extract what parameter is missing/wrong
        if "missing" in error_msg.lower():
            print(f"  HINT: Missing required parameter")
        elif "unexpected keyword" in error_msg.lower():
            print(f"  HINT: Parameter name is wrong")
        elif "positional argument" in error_msg.lower():
            print(f"  HINT: May need positional instead of keyword argument")
            
        return False, {"error": error_msg}
        
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {str(e)}")
        return False, {"error": str(e)}

def main():
    print_header("INHOUSE PRINT CALCULATOR TESTING - FRED DATABASE CONNECTION")
    
    # Connect to FRED database
    print_section("Database Connection")
    try:
        config_path = r"c:\Users\gpoli\GIT\In_House_SQL\config\database-config.json"
        print(f"Connecting to FRED database...")
        print(f"Config: {config_path}")
        
        db = InHousePrintDB(config_path)
        print("[OK] Connected to InHousePrint database (FRED)")
        
        # Test database connectivity - find table names first
        tables_result = db.execute_query("SELECT TOP 10 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        print(f"[OK] Database query successful - {len(tables_result)} tables found")
        print(f"Available tables: {tables_result['TABLE_NAME'].tolist()}")
        
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        print("Cannot proceed without database connection.")
        return
    
    # Initialize calculator
    print_section("Calculator Initialization")
    try:
        calc = ComprehensiveQuoteCalculator(db)
        print("[OK] ComprehensiveQuoteCalculator initialized")
    except Exception as e:
        print(f"[FAIL] Calculator initialization failed: {e}")
        return
    
    # TEST SUITE - Test each calculator systematically
    print_header("CALCULATOR TEST SUITE")
    
    results = []
    
    # TEST 1: Business Cards
    print_section("1. BUSINESS CARDS")
    success, result = test_calculator(
        calc, "calculate_business_cards", "Business Cards - Basic Test",
        quantity=500,
        stock_type="satin_350gsm",
        finish_size="90x55"
    )
    results.append(("business_cards", success, result))
    
    # Try with different parameter names
    if not success:
        success, result = test_calculator(
            calc, "calculate_business_cards", "Business Cards - Alt Parameters",
            quantity=500,
            stock="satin_350gsm",
            size="90x55"
        )
        results.append(("business_cards_alt", success, result))
    
    # TEST 2: Flyers
    print_section("2. FLYERS")
    success, result = test_calculator(
        calc, "calculate_flyers", "Flyers - A5",
        quantity=1000,
        width=148,
        height=210,
        gsm=170,
        finish="satin",
        sides=2
    )
    results.append(("flyers", success, result))
    
    # TEST 3: Perfect Bound Books
    print_section("3. PERFECT BOUND BOOKS")
    success, result = test_calculator(
        calc, "calculate_perfect_bound_book", "Books - A5",
        quantity=100,
        book_width=148,
        book_height=210,
        printed_pages=60,
        cover_stock_id=29,
        internal_stock_gsm=100,
        cello_gloss=True
    )
    results.append(("perfect_bound", success, result))
    
    # TEST 4: Booklets
    print_section("4. BOOKLETS")
    success, result = test_calculator(
        calc, "calculate_booklets", "Booklets - A5",
        quantity=200,
        width=148,
        height=210,
        pages=24,
        gsm=100,
        finish="satin"
    )
    results.append(("booklets", success, result))
    
    # TEST 5: Letterheads
    print_section("5. LETTERHEADS")
    success, result = test_calculator(
        calc, "calculate_letterheads", "Letterheads - A4",
        quantity=500,
        width=210,
        height=297,
        gsm=100,
        finish="laser",
        sides=1
    )
    results.append(("letterheads", success, result))
    
    # RESULTS SUMMARY
    print_header("TEST RESULTS SUMMARY")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    print("\n" + "-"*80)
    print("DETAILED RESULTS:")
    print("-"*80)
    
    for test_name, success, result in results:
        status = "[PASS]" if success else "[FAIL]"
        error = result.get('error', 'No error')[:60] if not success else ""
        cost = f"${result.get('cost_inc_gst', 0):.2f}" if success else error
        print(f"{status} {test_name:25s} {cost}")
    
    # SUCCESSFUL CALCULATOR ANALYSIS
    print_header("SUCCESSFUL CALCULATORS - PARAMETER ANALYSIS")
    
    successful_tests = [(name, res) for name, success, res in results if success]
    
    if successful_tests:
        print("\nCalculators that worked:")
        for name, result in successful_tests:
            print(f"\n{name}:")
            print(f"  Parameters used: {result.get('specifications', {})}")
    else:
        print("\n[WARNING] No calculators succeeded!")
        print("This suggests a deeper issue with parameter handling or database queries.")
    
    # FAILURE PATTERN ANALYSIS
    print_header("FAILURE PATTERN ANALYSIS")
    
    failed_tests = [(name, res) for name, success, res in results if not success]
    
    if failed_tests:
        error_patterns = {}
        for name, result in failed_tests:
            error = result.get('error', 'Unknown')
            
            # Categorize error
            if 'missing' in error.lower() and 'positional' in error.lower():
                category = "Missing Positional Argument"
            elif 'unexpected keyword' in error.lower():
                category = "Unexpected Keyword Argument"
            elif 'missing' in error.lower():
                category = "Missing Parameter"
            elif 'type' in error.lower():
                category = "Type Error"
            else:
                category = "Other Error"
            
            if category not in error_patterns:
                error_patterns[category] = []
            error_patterns[category].append((name, error))
        
        for category, errors in error_patterns.items():
            print(f"\n{category}: ({len(errors)} occurrences)")
            for name, error in errors[:3]:  # Show first 3 of each type
                print(f"  - {name}: {error[:70]}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
