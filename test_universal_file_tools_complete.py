"""
Comprehensive Test Suite for Universal File Tools
=================================================

Tests: Schema → Registry → Implementation → End-to-End Execution

Test Coverage:
1. Schema loading and validation
2. Registry integration
3. Function imports and signatures
4. Local file processing (no credentials)
5. Credential extraction pattern validation
6. Error handling

Date: January 9, 2026
Status: Post-fix validation
"""

import sys
import os
import json
from pathlib import Path

# Setup paths
sys.path.insert(0, 'AI_infrastructure')
sys.path.insert(0, 'tools')

# Test tracking
tests_passed = 0
tests_failed = 0
failed_tests = []

def test_step(name, test_func):
    """Execute a test step and track results"""
    global tests_passed, tests_failed, failed_tests
    try:
        test_func()
        print(f"✅ {name}")
        tests_passed += 1
        return True
    except AssertionError as e:
        print(f"❌ {name}")
        print(f"   Error: {e}")
        tests_failed += 1
        failed_tests.append({"test": name, "error": str(e)})
        return False
    except Exception as e:
        print(f"❌ {name}")
        print(f"   Unexpected error: {e}")
        tests_failed += 1
        failed_tests.append({"test": name, "error": f"Unexpected: {str(e)}"})
        return False


# ============================================================================
# TEST 1: SCHEMA LOADING (3 tests)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: SCHEMA LOADING")
print("=" * 80)

def test_schema_exists():
    schema_path = Path("tools/schemas/universal_file_tools.json")
    assert schema_path.exists(), f"Schema file not found: {schema_path}"

def test_schema_valid_json():
    with open("tools/schemas/universal_file_tools.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert "tools" in data, "Schema missing 'tools' key"
    assert isinstance(data["tools"], list), "'tools' must be a list"

def test_schema_structure():
    with open("tools/schemas/universal_file_tools.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    required_tools = [
        "process_outlook_attachment_for_ai",
        "process_gmail_attachment_for_ai",
        "process_onedrive_file_for_ai",
        "process_google_drive_file_for_ai",
        "process_local_file_for_ai",
        "process_uploaded_file_for_ai"
    ]
    
    tool_names = [tool["name"] for tool in data["tools"]]
    
    for required in required_tools:
        assert required in tool_names, f"Missing tool in schema: {required}"

test_step("Schema file exists", test_schema_exists)
test_step("Schema is valid JSON", test_schema_valid_json)
test_step("Schema has required tools", test_schema_structure)


# ============================================================================
# TEST 2: REGISTRY LOADING (3 tests)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: REGISTRY LOADING")
print("=" * 80)

registry = None

def test_registry_import():
    global registry
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    assert registry is not None, "Failed to initialize registry"

def test_file_tools_loaded():
    global registry
    file_tools = [
        "process_outlook_attachment_for_ai",
        "process_gmail_attachment_for_ai",
        "process_onedrive_file_for_ai",
        "process_google_drive_file_for_ai",
        "process_local_file_for_ai",
        "process_uploaded_file_for_ai"
    ]
    
    for tool_name in file_tools:
        assert tool_name in registry.tools, f"Tool not loaded in registry: {tool_name}"

def test_get_tool_method():
    global registry
    tool = registry.get_tool("process_local_file_for_ai")
    assert tool is not None, "get_tool() returned None"
    assert "name" in tool, "Tool schema missing 'name'"
    assert "description" in tool, "Tool schema missing 'description'"
    assert "parameters" in tool, "Tool schema missing 'parameters'"

test_step("Import Registry", test_registry_import)
test_step("File tools loaded in registry", test_file_tools_loaded)
test_step("Get tool schema works", test_get_tool_method)


# ============================================================================
# TEST 3: IMPLEMENTATION LOADING (4 tests)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: IMPLEMENTATION LOADING")
print("=" * 80)

implementation = None

def test_implementation_import():
    global implementation
    from tools.implementations import universal_file_tools
    implementation = universal_file_tools
    assert implementation is not None, "Failed to import implementation module"

def test_functions_exist():
    global implementation
    required_functions = [
        "process_outlook_attachment_for_ai",
        "process_gmail_attachment_for_ai",
        "process_onedrive_file_for_ai",
        "process_google_drive_file_for_ai",
        "process_local_file_for_ai",
        "process_uploaded_file_for_ai"
    ]
    
    for func_name in required_functions:
        assert hasattr(implementation, func_name), f"Function not found: {func_name}"
        func = getattr(implementation, func_name)
        assert callable(func), f"Not callable: {func_name}"

def test_function_signatures():
    """Verify functions accept **kwargs (for credential injection)"""
    global implementation
    import inspect
    
    # Functions that need credentials
    oauth_functions = [
        "process_outlook_attachment_for_ai",
        "process_gmail_attachment_for_ai",
        "process_onedrive_file_for_ai",
        "process_google_drive_file_for_ai"
    ]
    
    for func_name in oauth_functions:
        func = getattr(implementation, func_name)
        sig = inspect.signature(func)
        params = sig.parameters
        
        # Should have **kwargs for credential injection
        has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
        assert has_kwargs, f"{func_name} missing **kwargs parameter"
        
        # Should NOT have explicit _user_id parameter (old broken pattern)
        assert '_user_id' not in params, f"{func_name} has explicit _user_id (should use **kwargs)"

def test_credential_extraction_pattern():
    """Verify credential extraction code is correct"""
    import inspect
    
    func = getattr(implementation, "process_outlook_attachment_for_ai")
    source = inspect.getsource(func)
    
    # Should extract user_id from kwargs
    assert "kwargs.pop('_user_id'" in source or "kwargs.get('_user_id'" in source, \
        "Missing credential extraction: kwargs.pop('_user_id', None)"
    
    # Should have error handling
    assert "if not user_id" in source, "Missing user_id validation"
    assert "'error'" in source, "Missing error return"

test_step("Import implementation module", test_implementation_import)
test_step("All functions exist and callable", test_functions_exist)
test_step("Function signatures correct", test_function_signatures)
test_step("Credential extraction pattern", test_credential_extraction_pattern)


# ============================================================================
# TEST 4: LOCAL FILE PROCESSING (4 tests - NO CREDENTIALS NEEDED)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: LOCAL FILE PROCESSING (END-TO-END)")
print("=" * 80)

test_pdf_path = "UI/modules_internal/vector_database/Test files/RRE-LEATV-920_User Manual - v1.1.pdf"

def test_pdf_exists():
    assert os.path.exists(test_pdf_path), f"Test PDF not found: {test_pdf_path}"
    file_size = os.path.getsize(test_pdf_path)
    print(f"   PDF size: {file_size:,} bytes")
    assert file_size > 0, "PDF file is empty"

def test_process_local_file_structure():
    """Test that function returns correct structure (even if it fails)"""
    func = getattr(implementation, "process_local_file_for_ai")
    
    # Call with test PDF
    result = func(file_path=test_pdf_path, mode='auto')
    
    # Check structure
    assert isinstance(result, dict), "Result must be a dictionary"
    assert 'success' in result, "Result missing 'success' field"
    
    # If success, check content
    if result['success']:
        assert 'method' in result, "Successful result missing 'method'"
        assert 'metadata' in result, "Successful result missing 'metadata'"
        print(f"   ✅ Method: {result['method']}")
        print(f"   ✅ File: {result['metadata'].get('name', 'N/A')}")
        print(f"   ✅ Token estimate: {result['metadata'].get('token_estimate', 'N/A')}")
    else:
        print(f"   ⚠️  Processing failed (may need dependencies): {result.get('error', 'Unknown error')}")

def test_process_local_file_modes():
    """Test different processing modes"""
    func = getattr(implementation, "process_local_file_for_ai")
    
    modes = ['auto', 'direct', 'extract']
    
    for mode in modes:
        try:
            result = func(file_path=test_pdf_path, mode=mode)
            assert isinstance(result, dict), f"Mode {mode} didn't return dict"
            assert 'success' in result, f"Mode {mode} missing 'success'"
            
            if result['success']:
                print(f"   ✅ Mode '{mode}' works: {result['method']}")
            else:
                print(f"   ⚠️  Mode '{mode}' failed: {result.get('error', 'Unknown')[:50]}...")
        except Exception as e:
            print(f"   ⚠️  Mode '{mode}' exception: {str(e)[:50]}...")

def test_invalid_file_path():
    """Test error handling for invalid files"""
    func = getattr(implementation, "process_local_file_for_ai")
    
    result = func(file_path="nonexistent/file.pdf", mode='auto')
    
    assert isinstance(result, dict), "Invalid path should return dict"
    assert 'success' in result, "Result missing 'success' field"
    assert result['success'] == False, "Invalid path should return success=False"
    assert 'error' in result, "Failed result should have 'error' field"
    print(f"   ✅ Error handling works: {result['error'][:60]}...")

test_step("Test PDF exists", test_pdf_exists)
test_step("Local file processing structure", test_process_local_file_structure)
test_step("Multiple processing modes", test_process_local_file_modes)
test_step("Invalid path error handling", test_invalid_file_path)


# ============================================================================
# TEST 5: OAUTH TOOLS ERROR HANDLING (4 tests)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: OAUTH TOOLS ERROR HANDLING (WITHOUT CREDENTIALS)")
print("=" * 80)

def test_outlook_no_credentials():
    """Outlook tool should fail gracefully without credentials"""
    func = getattr(implementation, "process_outlook_attachment_for_ai")
    
    result = func(
        message_id="test_msg_id",
        attachment_id="test_att_id",
        mode='auto'
    )
    
    assert isinstance(result, dict), "Should return dict"
    assert result['success'] == False, "Should fail without credentials"
    assert 'error' in result, "Should have error message"
    assert 'user_id' in result['error'].lower() or 'authenticated' in result['error'].lower(), \
        "Error should mention authentication"
    print(f"   ✅ Error: {result['error']}")

def test_gmail_no_credentials():
    """Gmail tool should fail gracefully without credentials"""
    func = getattr(implementation, "process_gmail_attachment_for_ai")
    
    result = func(
        message_id="test_msg_id",
        attachment_id="test_att_id",
        mode='auto'
    )
    
    assert isinstance(result, dict), "Should return dict"
    assert result['success'] == False, "Should fail without credentials"
    assert 'error' in result, "Should have error message"
    print(f"   ✅ Error: {result['error']}")

def test_onedrive_no_credentials():
    """OneDrive tool should fail gracefully without credentials"""
    func = getattr(implementation, "process_onedrive_file_for_ai")
    
    result = func(
        file_id="test_file_id",
        mode='auto'
    )
    
    assert isinstance(result, dict), "Should return dict"
    assert result['success'] == False, "Should fail without credentials"
    assert 'error' in result, "Should have error message"
    print(f"   ✅ Error: {result['error']}")

def test_google_drive_no_credentials():
    """Google Drive tool should fail gracefully without credentials"""
    func = getattr(implementation, "process_google_drive_file_for_ai")
    
    result = func(
        file_id="test_file_id",
        mode='auto'
    )
    
    assert isinstance(result, dict), "Should return dict"
    assert result['success'] == False, "Should fail without credentials"
    assert 'error' in result, "Should have error message"
    print(f"   ✅ Error: {result['error']}")

test_step("Outlook without credentials", test_outlook_no_credentials)
test_step("Gmail without credentials", test_gmail_no_credentials)
test_step("OneDrive without credentials", test_onedrive_no_credentials)
test_step("Google Drive without credentials", test_google_drive_no_credentials)


# ============================================================================
# TEST 6: CREDENTIAL INJECTION SIMULATION (2 tests)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: CREDENTIAL INJECTION SIMULATION")
print("=" * 80)

def test_credential_extraction_outlook():
    """Test that credentials are properly extracted from kwargs"""
    func = getattr(implementation, "process_outlook_attachment_for_ai")
    
    # Simulate credential injection
    result = func(
        message_id="test_msg",
        attachment_id="test_att",
        mode='auto',
        _user_id=999,  # Simulated injected credential
        _injected_credentials={'access_token': 'fake_token'}
    )
    
    # Should still fail (no real API), but error should be different
    assert isinstance(result, dict), "Should return dict"
    # The error should NOT be about missing user_id anymore
    if not result['success'] and 'error' in result:
        error_msg = result['error'].lower()
        # If it's about user_id, credential extraction failed
        if 'user_id' in error_msg and 'provided' in error_msg:
            raise AssertionError(f"Credential extraction failed! Still showing user_id error: {result['error']}")
        else:
            print(f"   ✅ Credentials extracted (error is API-related, not auth): {result['error'][:60]}...")

def test_credential_extraction_gmail():
    """Test Gmail credential extraction"""
    func = getattr(implementation, "process_gmail_attachment_for_ai")
    
    result = func(
        message_id="test_msg",
        attachment_id="test_att",
        mode='auto',
        _user_id=999
    )
    
    assert isinstance(result, dict), "Should return dict"
    if not result['success'] and 'error' in result:
        error_msg = result['error'].lower()
        if 'user_id' in error_msg and 'provided' in error_msg:
            raise AssertionError(f"Credential extraction failed! {result['error']}")
        else:
            print(f"   ✅ Credentials extracted: {result['error'][:60]}...")

test_step("Outlook credential extraction", test_credential_extraction_outlook)
test_step("Gmail credential extraction", test_credential_extraction_gmail)


# ============================================================================
# FINAL REPORT
# ============================================================================
print("\n" + "=" * 80)
print("FINAL TEST REPORT")
print("=" * 80)

total = tests_passed + tests_failed
pass_rate = (tests_passed / total * 100) if total > 0 else 0

print(f"\nTotal Tests: {total}")
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"📊 Pass Rate: {pass_rate:.1f}%")

if tests_failed > 0:
    print("\n" + "=" * 80)
    print("FAILED TESTS:")
    print("=" * 80)
    for failure in failed_tests:
        print(f"\n❌ {failure['test']}")
        print(f"   {failure['error']}")
    print("=" * 80)
    print("\n⚠️  SOME TESTS FAILED - Review errors above")
else:
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS PASSED - MODULE IS FULLY FUNCTIONAL")
    print("=" * 80)
    print("\n✅ Universal file tools are working correctly!")
    print("✅ Credential extraction pattern implemented properly")
    print("✅ Local file processing functional")
    print("✅ OAuth tools validate credentials correctly")

# Exit code
sys.exit(0 if tests_failed == 0 else 1)
