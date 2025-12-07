"""
Systematic discovery of actual calculator parameters
Tests each calculator one by one to see what it expects
"""
import sys
import os
import json
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Minimal imports to avoid Unicode issues
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_calculator_discovery():
    """Discover parameters for each calculator by testing"""
    
    print("\n" + "="*80)
    print("CALCULATOR PARAMETER DISCOVERY TEST")
    print("="*80)
    print("Testing each calculator to discover actual parameter requirements\n")
    
    # Import the calculator wrapper functions directly
    try:
        from UI.modules_external.quote_calculator.implementations.calculator_wrapper import (
            calculate_business_cards,
            calculate_flyers,
            calculate_booklets,
            calculate_perfect_bound_books,
            calculate_brochures,
            calculate_posters,
            calculate_banners,
            calculate_stickers,
            calculate_folders,
            calculate_letterheads,
            calculate_compliment_slips,
            calculate_ncr_books,
            calculate_envelopes,
            calculate_notepads,
            calculate_presentation_folders
        )
        print("[OK] Successfully imported calculator wrapper functions\n")
    except Exception as e:
        print(f"[FAIL] Could not import calculator wrappers: {e}")
        print(traceback.format_exc())
        return False
    
    # Test cases - start with minimal parameters and add as needed
    calculators = [
        {
            "name": "Business Cards",
            "function": calculate_business_cards,
            "test_params": [
                {"quantity": 500},
                {"quantity": 500, "stock_type": "350gsm"},
                {"quantity": 500, "stock_type": "350gsm", "finish": "gloss"},
                {"quantity": 500, "width": 90, "height": 55},
            ]
        },
        {
            "name": "Flyers", 
            "function": calculate_flyers,
            "test_params": [
                {"quantity": 1000},
                {"quantity": 1000, "size": "A4"},
                {"quantity": 1000, "size": "A4", "stock": "170gsm"},
                {"quantity": 1000, "width": 210, "height": 297, "gsm": 170},
            ]
        },
        {
            "name": "Booklets",
            "function": calculate_booklets,
            "test_params": [
                {"quantity": 100},
                {"quantity": 100, "pages": 24},
                {"quantity": 100, "pages": 24, "size": "A5"},
                {"quantity": 100, "printed_pages": 24, "width": 148, "height": 210},
            ]
        },
        {
            "name": "Perfect Bound Books",
            "function": calculate_perfect_bound_books,
            "test_params": [
                {"quantity": 100},
                {"quantity": 100, "pages": 60},
                {"quantity": 100, "printed_pages": 60},
                {"quantity": 100, "printed_pages": 60, "width": 148, "height": 210},
                {"quantity": 100, "printed_pages": 60, "finish_size": "A5"},
                {"quantity": 100, "printed_pages": 60, "cello": 1},
                {"quantity": 100, "printed_pages": 60, "cello_required": True},
            ]
        },
        {
            "name": "Brochures",
            "function": calculate_brochures,
            "test_params": [
                {"quantity": 500},
                {"quantity": 500, "pages": 8},
                {"quantity": 500, "panels": 3},
                {"quantity": 500, "size": "DL"},
            ]
        },
        {
            "name": "Posters",
            "function": calculate_posters,
            "test_params": [
                {"quantity": 50},
                {"quantity": 50, "size": "A3"},
                {"quantity": 50, "width": 297, "height": 420},
                {"quantity": 50, "width": 297, "height": 420, "stock": "200gsm"},
            ]
        },
        {
            "name": "Banners",
            "function": calculate_banners,
            "test_params": [
                {"quantity": 10},
                {"quantity": 10, "width": 1000, "height": 2000},
                {"quantity": 10, "width": 1000, "height": 2000, "material": "vinyl"},
            ]
        },
        {
            "name": "Stickers",
            "function": calculate_stickers,
            "test_params": [
                {"quantity": 1000},
                {"quantity": 1000, "size": "50x50"},
                {"quantity": 1000, "width": 50, "height": 50},
                {"quantity": 1000, "width": 50, "height": 50, "finish": "gloss"},
            ]
        },
        {
            "name": "Folders",
            "function": calculate_folders,
            "test_params": [
                {"quantity": 250},
                {"quantity": 250, "size": "A4"},
                {"quantity": 250, "pockets": 2},
            ]
        },
        {
            "name": "Letterheads",
            "function": calculate_letterheads,
            "test_params": [
                {"quantity": 500},
                {"quantity": 500, "size": "A4"},
                {"quantity": 500, "stock": "100gsm"},
            ]
        },
        {
            "name": "Compliment Slips",
            "function": calculate_compliment_slips,
            "test_params": [
                {"quantity": 500},
                {"quantity": 500, "size": "DL"},
            ]
        },
        {
            "name": "NCR Books",
            "function": calculate_ncr_books,
            "test_params": [
                {"quantity": 50},
                {"quantity": 50, "sets": 3},
                {"quantity": 50, "sets": 3, "sheets_per_set": 50},
            ]
        },
        {
            "name": "Envelopes",
            "function": calculate_envelopes,
            "test_params": [
                {"quantity": 1000},
                {"quantity": 1000, "size": "DL"},
                {"quantity": 1000, "size": "DL", "window": True},
            ]
        },
        {
            "name": "Notepads",
            "function": calculate_notepads,
            "test_params": [
                {"quantity": 100},
                {"quantity": 100, "sheets": 50},
                {"quantity": 100, "sheets": 50, "size": "A5"},
            ]
        },
        {
            "name": "Presentation Folders",
            "function": calculate_presentation_folders,
            "test_params": [
                {"quantity": 100},
                {"quantity": 100, "size": "A4"},
                {"quantity": 100, "pockets": 2, "stock": "350gsm"},
            ]
        }
    ]
    
    results = []
    
    for calc in calculators:
        print("-" * 80)
        print(f"\nTesting: {calc['name']}")
        print("-" * 80)
        
        working_params = None
        error_messages = []
        
        for i, params in enumerate(calc['test_params'], 1):
            print(f"\n  Test {i}: {json.dumps(params, indent=None)}")
            
            try:
                result = calc['function'](**params)
                
                # Check if result is successful
                if isinstance(result, dict):
                    if result.get('success') or 'cost' in str(result).lower() or 'price' in str(result).lower():
                        print(f"    [SUCCESS] Got result: {result}")
                        working_params = params
                        break
                    else:
                        error_msg = result.get('error', result.get('message', str(result)))
                        print(f"    [FAIL] {error_msg}")
                        error_messages.append((params, error_msg))
                else:
                    print(f"    [SUCCESS] Got result: {result}")
                    working_params = params
                    break
                    
            except TypeError as e:
                error_msg = str(e)
                print(f"    [FAIL] TypeError: {error_msg}")
                error_messages.append((params, error_msg))
                
                # Try to extract what parameter is missing or wrong
                if "required positional argument" in error_msg:
                    missing = error_msg.split("'")[1] if "'" in error_msg else "unknown"
                    print(f"    [HINT] Missing required parameter: {missing}")
                elif "unexpected keyword argument" in error_msg:
                    unexpected = error_msg.split("'")[1] if "'" in error_msg else "unknown"
                    print(f"    [HINT] Parameter '{unexpected}' not accepted")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"    [FAIL] {type(e).__name__}: {error_msg}")
                error_messages.append((params, error_msg))
        
        # Summary for this calculator
        if working_params:
            print(f"\n  [OK] {calc['name']} - WORKING PARAMETERS FOUND:")
            print(f"       {json.dumps(working_params, indent=8)}")
            results.append({
                "calculator": calc['name'],
                "status": "SUCCESS",
                "working_params": working_params
            })
        else:
            print(f"\n  [FAIL] {calc['name']} - NO WORKING PARAMETERS FOUND")
            print(f"  Error summary:")
            for params, error in error_messages[-3:]:  # Show last 3 errors
                print(f"    - {error}")
            results.append({
                "calculator": calc['name'],
                "status": "FAILED",
                "errors": error_messages
            })
    
    # Final summary
    print("\n\n" + "="*80)
    print("DISCOVERY TEST SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_count = len(results)
    
    print(f"\nResults: {success_count}/{total_count} calculators working\n")
    
    print("WORKING CALCULATORS:")
    for r in results:
        if r['status'] == 'SUCCESS':
            print(f"  [OK] {r['calculator']}")
            print(f"       Parameters: {json.dumps(r['working_params'], indent=None)}")
    
    print("\nFAILED CALCULATORS:")
    for r in results:
        if r['status'] == 'FAILED':
            print(f"  [FAIL] {r['calculator']}")
            if r['errors']:
                last_error = r['errors'][-1][1]
                print(f"         Last error: {last_error}")
    
    print("\n" + "="*80)
    
    return success_count > 0


if __name__ == "__main__":
    try:
        success = test_calculator_discovery()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        print(traceback.format_exc())
        sys.exit(1)
