"""
Direct calculator testing - imports and tests each calculator function
Tests with the exact parameters defined in the function signatures
"""
import sys
import os
from pathlib import Path

# Add root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_all_calculators():
    """Test each calculator with correct parameters"""
    
    print("\n" + "="*80)
    print("DIRECT CALCULATOR FUNCTION TESTS")
    print("="*80)
    print("Testing each calculator with documented parameters\n")
    
    # Import the wrapper module
    try:
        # Import using the module path with hyphen converted to underscore for Python
        calculator_wrapper_path = root_dir / "UI" / "modules_external" / "quote-calculator" / "implementations" / "calculator_wrapper.py"
        
        # Load the module dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location("calculator_wrapper", calculator_wrapper_path)
        calc_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calc_module)
        
        print("[OK] Successfully loaded calculator_wrapper module\n")
    except Exception as e:
        print(f"[FAIL] Could not load calculator module: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Define test cases based on actual function signatures
    test_cases = [
        {
            "name": "Business Cards",
            "function": "calculate_business_cards",
            "params": {
                "quantity": 500,
                "stock_type": "standard",  # or "premium"
                "sides": 2
            }
        },
        {
            "name": "Flyers",
            "function": "calculate_flyers",
            "params": {
                "quantity": 1000,
                "size": "A4",
                "stock": "170gsm",
                "sides": 2
            }
        },
        {
            "name": "Booklets",
            "function": "calculate_booklets",
            "params": {
                "quantity": 100,
                "pages": 24,
                "cover_stock": "250gsm",
                "inner_stock": "100gsm",
                "size": "A5"
            }
        },
        {
            "name": "Perfect Bound Books",
            "function": "calculate_perfect_bound_books",
            "params": {
                "quantity": 100,
                "pages": 60,
                "cover_stock": "250gsm",
                "inner_stock": "100gsm",
                "size": "A5"
            }
        },
        {
            "name": "Letterheads",
            "function": "calculate_letterheads",
            "params": {
                "quantity": 500,
                "stock": "100gsm",
                "colors": 4
            }
        },
        {
            "name": "Corflute Signs",
            "function": "calculate_corflute_signs",
            "params": {
                "quantity": 10,
                "size": "A3",
                "thickness": "5mm",
                "sides": 1
            }
        }
    ]
    
    results = []
    
    for test in test_cases:
        print("-" * 80)
        print(f"\nTesting: {test['name']}")
        print(f"Function: {test['function']}")
        print(f"Parameters: {test['params']}")
        print()
        
        try:
            # Get the function from the module
            func = getattr(calc_module, test['function'])
            
            # Call with parameters
            result = func(**test['params'])
            
            # Check result
            if isinstance(result, dict):
                if result.get('success'):
                    print(f"[SUCCESS] Calculator returned result:")
                    
                    # Print key fields
                    for key in ['total_price', 'per_unit_price', 'per_book_price', 'quantity', 'product']:
                        if key in result:
                            print(f"  {key}: {result[key]}")
                    
                    results.append({
                        "calculator": test['name'],
                        "status": "SUCCESS",
                        "result": result
                    })
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"[FAIL] Calculator returned error: {error}")
                    results.append({
                        "calculator": test['name'],
                        "status": "FAILED",
                        "error": error
                    })
            else:
                print(f"[SUCCESS] Got non-dict result: {result}")
                results.append({
                    "calculator": test['name'],
                    "status": "SUCCESS",
                    "result": result
                })
                
        except TypeError as e:
            error_msg = str(e)
            print(f"[FAIL] TypeError: {error_msg}")
            
            # Parse the error to understand what's wrong
            if "required positional argument" in error_msg:
                missing = error_msg.split("'")[1] if "'" in error_msg else "unknown"
                print(f"  Missing required parameter: {missing}")
            elif "unexpected keyword argument" in error_msg:
                unexpected = error_msg.split("'")[1] if "'" in error_msg else "unknown"
                print(f"  Unexpected parameter: {unexpected}")
            elif "takes" in error_msg and "positional" in error_msg:
                print(f"  Wrong number of parameters")
            
            results.append({
                "calculator": test['name'],
                "status": "FAILED",
                "error": error_msg
            })
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[FAIL] {error_msg}")
            results.append({
                "calculator": test['name'],
                "status": "FAILED",
                "error": error_msg
            })
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_count = len(results)
    
    print(f"\nResults: {success_count}/{total_count} calculators working ({success_count/total_count*100:.0f}%)\n")
    
    if success_count > 0:
        print("WORKING CALCULATORS:")
        for r in results:
            if r['status'] == 'SUCCESS':
                result = r['result']
                price = result.get('total_price') or result.get('per_unit_price') or 'N/A'
                print(f"  [OK] {r['calculator']} - Price: ${price}")
    
    if success_count < total_count:
        print("\nFAILED CALCULATORS:")
        for r in results:
            if r['status'] == 'FAILED':
                print(f"  [FAIL] {r['calculator']}")
                print(f"         Error: {r['error']}")
    
    print("\n" + "="*80)
    
    return success_count == total_count


if __name__ == "__main__":
    try:
        success = test_all_calculators()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
