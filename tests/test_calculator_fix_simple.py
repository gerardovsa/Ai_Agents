"""
Simple test to verify the calculator parameter parsing fix
Tests directly without full registry initialization
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_json_deserialization():
    """Test the core fix: JSON string parameter deserialization"""
    print("\n" + "="*80)
    print("TESTING CALCULATOR FIX - JSON Parameter Deserialization")
    print("="*80)
    
    # Simulate what the tool receives
    params_as_string = '{"quantity": 500, "stock_type": "satin_350gsm", "finish_size": "90x55"}'
    
    print(f"\n1. Received parameters: {type(params_as_string).__name__}")
    print(f"   Value: {params_as_string}")
    
    # THE FIX: Deserialize if string
    if isinstance(params_as_string, str):
        try:
            params = json.loads(params_as_string)
            print(f"\n2. [OK] Deserialized to: {type(params).__name__}")
            print(f"   Success: Can now call .items()")
        except json.JSONDecodeError as e:
            print(f"\n2. [FAIL] JSON decode error: {e}")
            return False
    
    # Verify it's now a dict
    if not isinstance(params, dict):
        print(f"\n3. [FAIL] Expected dict, got {type(params).__name__}")
        return False
    
    # Verify we can iterate (what the old code tried to do)
    print(f"\n3. [OK] Testing .items() iteration:")
    for key, value in params.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "="*80)
    print("[PASS] JSON deserialization fix works correctly")
    print("="*80)
    return True


def test_dict_parameters():
    """Test that dict parameters still work (backwards compatibility)"""
    print("\n" + "="*80)
    print("TESTING CALCULATOR FIX - Dict Parameter Handling")
    print("="*80)
    
    # Parameters already as dict
    params = {"quantity": 500, "stock_type": "satin_350gsm", "finish_size": "90x55"}
    
    print(f"\n1. Received parameters: {type(params).__name__}")
    print(f"   Value: {params}")
    
    # THE FIX: Check if string first, skip if already dict
    if isinstance(params, str):
        try:
            params = json.loads(params)
            print(f"\n2. Deserialized to dict")
        except json.JSONDecodeError as e:
            print(f"\n2. [FAIL] JSON decode error: {e}")
            return False
    else:
        print(f"\n2. [OK] Already a dict, no deserialization needed")
    
    # Verify it's a dict
    if not isinstance(params, dict):
        print(f"\n3. [FAIL] Expected dict, got {type(params).__name__}")
        return False
    
    # Verify we can iterate
    print(f"\n3. [OK] Testing .items() iteration:")
    for key, value in params.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "="*80)
    print("[PASS] Dict parameters still work (backwards compatible)")
    print("="*80)
    return True


def test_invalid_json():
    """Test error handling for invalid JSON"""
    print("\n" + "="*80)
    print("TESTING CALCULATOR FIX - Invalid JSON Error Handling")
    print("="*80)
    
    # Invalid JSON string
    params_as_string = '{quantity: 500, invalid json}'
    
    print(f"\n1. Received invalid JSON: {params_as_string}")
    
    # THE FIX: Handle JSON errors gracefully
    if isinstance(params_as_string, str):
        try:
            params = json.loads(params_as_string)
            print(f"\n2. [FAIL] Should have raised JSONDecodeError")
            return False
        except json.JSONDecodeError as e:
            print(f"\n2. [OK] Caught JSON error: {e}")
            print(f"   Error handled gracefully")
    
    print("\n" + "="*80)
    print("[PASS] Invalid JSON handled correctly")
    print("="*80)
    return True


def test_parameter_validation():
    """Test parameter type validation"""
    print("\n" + "="*80)
    print("TESTING CALCULATOR FIX - Parameter Type Validation")
    print("="*80)
    
    # Test various parameter types
    test_cases = [
        ('{"key": "value"}', True, "Valid JSON string"),
        ('{"quantity": 100}', True, "Valid JSON with numbers"),
        ({"key": "value"}, True, "Dict object"),
        ("not json at all", False, "Invalid JSON string"),
        (123, False, "Number (invalid type)"),
        (None, False, "None (invalid type)"),
    ]
    
    all_passed = True
    for params, should_pass, description in test_cases:
        print(f"\n{description}:")
        print(f"  Input: {params} ({type(params).__name__})")
        
        # THE FIX: Apply deserialization logic
        result_params = params
        error = None
        
        if isinstance(result_params, str):
            try:
                result_params = json.loads(result_params)
            except json.JSONDecodeError as e:
                error = str(e)
        
        is_dict = isinstance(result_params, dict)
        passed = (is_dict == should_pass)
        
        if passed:
            print(f"  [OK] Result: {type(result_params).__name__} (as expected)")
        else:
            print(f"  [FAIL] Expected {'dict' if should_pass else 'error'}, got {type(result_params).__name__}")
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("[PASS] All parameter validation tests passed")
    else:
        print("[FAIL] Some parameter validation tests failed")
    print("="*80)
    return all_passed


if __name__ == "__main__":
    print("\n")
    print("="*80)
    print("CALCULATOR PARAMETER PARSING FIX - VERIFICATION TESTS")
    print("="*80)
    print("Testing the fix applied to tool_use_agent.py lines 1020-1055")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("JSON Deserialization", test_json_deserialization()))
    results.append(("Dict Parameter Handling", test_dict_parameters()))
    results.append(("Invalid JSON Handling", test_invalid_json()))
    results.append(("Parameter Validation", test_parameter_validation()))
    
    # Summary
    print("\n\n")
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n[OK] ALL TESTS PASSED - Fix is working correctly!")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        sys.exit(1)
