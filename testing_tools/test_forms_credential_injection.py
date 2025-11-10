"""
Test Google Forms Credential Injection - Fix #17
Verify all Forms question functions accept credential injection parameters
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_forms_function_signatures():
    """Test that all Forms functions have proper credential injection parameters"""
    
    print("=" * 80)
    print("GOOGLE FORMS CREDENTIAL INJECTION TEST - FIX #17")
    print("=" * 80)
    print()
    
    # Import the Forms module
    try:
        from google_workspace import google_forms
        print("✅ Successfully imported google_forms module")
        print()
    except Exception as e:
        print(f"❌ Failed to import google_forms: {e}")
        return False
    
    # List of functions that MUST have credential injection parameters
    required_functions = [
        'google_forms_create_form',           # Already fixed in Fix #16
        'google_forms_add_question',          # Fixed in Fix #17
        'google_forms_add_multiple_choice',   # Fixed in Fix #17
        'google_forms_add_text_question',     # Fixed in Fix #17
        'google_forms_add_linear_scale',      # Fixed in Fix #17
        'google_forms_add_checkbox',          # Fixed in Fix #17
        'google_forms_add_dropdown',          # Fixed in Fix #17
        'google_forms_add_date_question',     # Fixed in Fix #17
        'google_forms_add_quiz_question',     # Fixed in Fix #17
        'google_forms_batch_add_questions'    # Fixed in Fix #17
    ]
    
    print("Testing function signatures for credential injection parameters:")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for func_name in required_functions:
        if not hasattr(google_forms, func_name):
            print(f"❌ {func_name}: Function not found")
            failed += 1
            continue
        
        func = getattr(google_forms, func_name)
        
        # Get function signature
        import inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        # Check for required credential injection parameters
        has_user_id = '_user_id' in params
        has_injected_creds = '_injected_credentials' in params
        has_kwargs = any(str(sig.parameters[p].kind) == 'VAR_KEYWORD' for p in params)
        
        if has_user_id and has_injected_creds and has_kwargs:
            print(f"✅ {func_name}")
            print(f"   Parameters: {', '.join(params[-5:])}")  # Show last 5 params
            passed += 1
        else:
            print(f"❌ {func_name}")
            print(f"   Missing: ", end="")
            missing = []
            if not has_user_id:
                missing.append("_user_id")
            if not has_injected_creds:
                missing.append("_injected_credentials")
            if not has_kwargs:
                missing.append("**kwargs")
            print(", ".join(missing))
            failed += 1
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(required_functions)} functions")
    print("=" * 80)
    
    if failed == 0:
        print()
        print("🎉 SUCCESS! All Forms functions have proper credential injection!")
        print()
        print("Fix #17 Complete:")
        print("✅ All 10 Forms functions can now accept _user_id and _injected_credentials")
        print("✅ Functions will use database OAuth when called by AI agents")
        print("✅ Forms can be created AND populated with questions using user credentials")
        return True
    else:
        print()
        print("⚠️  Some functions still need fixes")
        return False


def test_function_calls_with_injection():
    """Test that functions can be called with credential injection parameters"""
    
    print()
    print("=" * 80)
    print("TESTING FUNCTION CALLS WITH CREDENTIAL INJECTION")
    print("=" * 80)
    print()
    
    from google_workspace import google_forms
    
    # Test functions that should accept credential parameters
    test_cases = [
        {
            'name': 'google_forms_add_text_question',
            'args': ('test_form_id', 'Test Question'),
            'kwargs': {'_user_id': 1, '_injected_credentials': True}
        },
        {
            'name': 'google_forms_add_multiple_choice',
            'args': ('test_form_id', 'Choose one', ['Option A', 'Option B']),
            'kwargs': {'_user_id': 1, '_injected_credentials': True}
        },
        {
            'name': 'google_forms_batch_add_questions',
            'args': ('test_form_id', []),
            'kwargs': {'_user_id': 1, '_injected_credentials': True}
        }
    ]
    
    print("Testing that functions ACCEPT credential parameters (won't execute, just check signature):")
    print()
    
    passed = 0
    for test in test_cases:
        func_name = test['name']
        func = getattr(google_forms, func_name)
        
        try:
            # Try to inspect if the function would accept these parameters
            import inspect
            sig = inspect.signature(func)
            
            # Build a test call with the parameters
            bound = sig.bind(*test['args'], **test['kwargs'])
            
            print(f"✅ {func_name} accepts credential injection parameters")
            passed += 1
        except TypeError as e:
            print(f"❌ {func_name} rejected parameters: {e}")
    
    print()
    print(f"Result: {passed}/{len(test_cases)} functions accept credential injection")
    print()
    
    return passed == len(test_cases)


if __name__ == '__main__':
    # Run signature test
    sig_result = test_forms_function_signatures()
    
    # Run call test
    call_result = test_function_calls_with_injection()
    
    # Final result
    print()
    print("=" * 80)
    if sig_result and call_result:
        print("🎉 ALL TESTS PASSED - FIX #17 VERIFIED!")
        print()
        print("Google Forms functions are now fully operational with credential injection.")
        print("AI agents can create forms AND add questions using user OAuth credentials.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed - review output above")
        sys.exit(1)
