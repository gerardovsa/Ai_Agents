"""
Test Xero Quotes Tools Integration

Tests:
1. Schema file exists and is valid JSON
2. All 5 tools are defined in schema
3. Implementation file loads without errors
4. All 5 functions are callable
5. Credential injection prefix exists
6. Tool naming conventions match
"""

import json
import sys
import os

def test_schema():
    """Test 1: Schema file validation"""
    print("\n[TEST 1] Schema File Validation")
    try:
        with open('tools/schemas/xero_quotes_tools.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        assert schema['platform'] == 'xero_quotes', "Platform should be 'xero_quotes'"
        assert len(schema['tools']) == 5, f"Expected 5 tools, found {len(schema['tools'])}"
        
        tool_names = [t['name'] for t in schema['tools']]
        expected_tools = [
            'xero_create_quote',
            'xero_list_quotes',
            'xero_get_quote_by_id',
            'xero_update_quote',
            'xero_get_branding_themes'
        ]
        
        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"
        
        print("   PASS - Schema valid with 5 tools defined")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_implementation():
    """Test 2: Implementation file validation"""
    print("\n[TEST 2] Implementation File Validation")
    try:
        sys.path.insert(0, 'tools/implementations')
        import xero_quotes
        
        # Check all 5 functions exist
        functions = [
            'xero_create_quote',
            'xero_list_quotes',
            'xero_get_quote_by_id',
            'xero_update_quote',
            'xero_get_branding_themes'
        ]
        
        for func_name in functions:
            assert hasattr(xero_quotes, func_name), f"Missing function: {func_name}"
            func = getattr(xero_quotes, func_name)
            assert callable(func), f"Function not callable: {func_name}"
        
        print("   PASS - All 5 functions exist and are callable")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_credential_injection():
    """Test 3: Credential injection prefix"""
    print("\n[TEST 3] Credential Injection Prefix")
    try:
        with open('AI_infrastructure/auth/credential_injector.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "xero_tools_prefixes = ['xero_']" in content, "xero_ prefix not found"
        
        print("   PASS - xero_ prefix detection exists in credential_injector.py")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_function_signatures():
    """Test 4: Function signatures have **kwargs"""
    print("\n[TEST 4] Function Signatures")
    try:
        import inspect
        sys.path.insert(0, 'tools/implementations')
        import xero_quotes
        
        functions = [
            'xero_create_quote',
            'xero_list_quotes',
            'xero_get_quote_by_id',
            'xero_update_quote',
            'xero_get_branding_themes'
        ]
        
        for func_name in functions:
            func = getattr(xero_quotes, func_name)
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            assert 'kwargs' in params, f"{func_name} missing **kwargs parameter"
        
        print("   PASS - All functions accept **kwargs for credential injection")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_schema_tool_match():
    """Test 5: Schema and implementation names match"""
    print("\n[TEST 5] Schema-Implementation Name Match")
    try:
        with open('tools/schemas/xero_quotes_tools.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        sys.path.insert(0, 'tools/implementations')
        import xero_quotes
        
        schema_tools = [t['name'] for t in schema['tools']]
        impl_functions = [
            name for name in dir(xero_quotes)
            if not name.startswith('_') and callable(getattr(xero_quotes, name))
            and name.startswith('xero_')
        ]
        
        for tool_name in schema_tools:
            assert tool_name in impl_functions, f"Schema tool {tool_name} not in implementation"
        
        print(f"   PASS - All {len(schema_tools)} schema tools have matching implementations")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_pagination_parameters():
    """Test 6: List quotes has pagination parameters"""
    print("\n[TEST 6] Pagination Parameters")
    try:
        with open('tools/schemas/xero_quotes_tools.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        list_quotes_tool = next(t for t in schema['tools'] if t['name'] == 'xero_list_quotes')
        params = list_quotes_tool['parameters']['properties']
        
        assert 'page' in params, "Missing 'page' parameter"
        assert 'page_size' in params, "Missing 'page_size' parameter"
        assert params['page'].get('default') == 1, "page should default to 1"
        assert params['page_size'].get('default') == 100, "page_size should default to 100"
        
        print("   PASS - Pagination parameters correct (page=1, page_size=100)")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_branding_theme_support():
    """Test 7: Quote creation supports branding themes"""
    print("\n[TEST 7] Branding Theme Support")
    try:
        with open('tools/schemas/xero_quotes_tools.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        create_quote_tool = next(t for t in schema['tools'] if t['name'] == 'xero_create_quote')
        params = create_quote_tool['parameters']['properties']
        
        assert 'branding_theme_id' in params, "Missing 'branding_theme_id' parameter"
        
        branding_themes_tool = next(t for t in schema['tools'] if t['name'] == 'xero_get_branding_themes')
        assert branding_themes_tool is not None, "Missing xero_get_branding_themes tool"
        
        print("   PASS - Branding theme (template) support exists")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def test_filter_parameters():
    """Test 8: List quotes has filter parameters for 70K records"""
    print("\n[TEST 8] Filter Parameters for Large Dataset")
    try:
        with open('tools/schemas/xero_quotes_tools.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        list_quotes_tool = next(t for t in schema['tools'] if t['name'] == 'xero_list_quotes')
        params = list_quotes_tool['parameters']['properties']
        
        required_filters = ['date_from', 'date_to', 'contact_id', 'status', 'quote_number']
        
        for filter_param in required_filters:
            assert filter_param in params, f"Missing filter parameter: {filter_param}"
        
        print("   PASS - All filter parameters exist (date_from, date_to, contact_id, status, quote_number)")
        return True
    except Exception as e:
        print(f"   FAIL - {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("XERO QUOTES TOOLS VALIDATION")
    print("=" * 70)
    
    tests = [
        test_schema,
        test_implementation,
        test_credential_injection,
        test_function_signatures,
        test_schema_tool_match,
        test_pagination_parameters,
        test_branding_theme_support,
        test_filter_parameters
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"   ERROR - {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n SUCCESS - All Xero quotes tools validation tests passed!")
        return 0
    else:
        print("\n FAILURE - Some tests failed")
        return 1


if __name__ == '__main__':
    exit(main())
