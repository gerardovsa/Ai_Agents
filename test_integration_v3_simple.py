"""
INTEGRATION TEST V3 - Simplified end-to-end testing

Tests:
1. Registry loading (schemas + implementations)
2. Tool validation
3. Credential injection
4. Tool discovery and execution
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from tools.registry_v3 import RegistryV3
from AI_infrastructure.routes.agent_routes_v3 import ToolExecutor, ToolCallProcessor


def main():
    print("\n" + "="*80)
    print("INTEGRATION TEST V3 - SIMPLIFIED")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    # Test 1: Registry initialization
    try:
        registry = RegistryV3()
        assert len(registry.tools) > 500, f"Expected >500 tools, got {len(registry.tools)}"
        assert len(registry.implementations) > 30, f"Expected >30 implementations"
        print("✅ Test 1: Registry initialization")
        passed += 1
    except Exception as e:
        print(f"❌ Test 1: {e}")
        failed += 1
    
    # Test 2: Tool validation - valid tool
    try:
        executor = ToolExecutor(registry)
        is_valid, error = executor.validate_tool_call("gmail_send_email", {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body"
        })
        assert is_valid, f"Validation should pass: {error}"
        print("✅ Test 2: Tool validation - valid tool")
        passed += 1
    except Exception as e:
        print(f"❌ Test 2: {e}")
        failed += 1
    
    # Test 3: Tool validation - invalid (missing required)
    try:
        is_valid, error = executor.validate_tool_call("gmail_send_email", {
            "to": "test@example.com"
        })
        assert not is_valid, "Should reject missing params"
        assert "required" in error.lower(), f"Error should mention required: {error}"
        print("✅ Test 3: Tool validation - missing required params")
        passed += 1
    except Exception as e:
        print(f"❌ Test 3: {e}")
        failed += 1
    
    # Test 4: Credential injection - no credentials
    try:
        params = {"to": "test@example.com", "subject": "Test"}
        injected = executor.inject_credentials(params)
        assert "_user_id" not in injected
        assert "_injected_credentials" not in injected
        print("✅ Test 4: Credential injection - no credentials")
        passed += 1
    except Exception as e:
        print(f"❌ Test 4: {e}")
        failed += 1
    
    # Test 5: Credential injection - with user_id
    try:
        params = {"to": "test@example.com"}
        injected = executor.inject_credentials(params, user_id=123)
        assert "_user_id" in injected and injected["_user_id"] == 123
        print("✅ Test 5: Credential injection - with user_id")
        passed += 1
    except Exception as e:
        print(f"❌ Test 5: {e}")
        failed += 1
    
    # Test 6: Credential injection - with credentials
    try:
        params = {"to": "test@example.com"}
        creds = {"access_token": "abc123", "refresh_token": "xyz"}
        injected = executor.inject_credentials(params, credentials=creds)
        assert "_injected_credentials" in injected
        assert injected["_injected_credentials"] == creds
        print("✅ Test 6: Credential injection - with credentials")
        passed += 1
    except Exception as e:
        print(f"❌ Test 6: {e}")
        failed += 1
    
    # Test 7: Get tool function
    try:
        func = registry.get_tool_function("gmail_send_email")
        assert func is not None and callable(func)
        print("✅ Test 7: Get tool function - gmail_send_email")
        passed += 1
    except Exception as e:
        print(f"❌ Test 7: {e}")
        failed += 1
    
    # Test 8: Get tool function - Google Docs
    try:
        func = registry.get_tool_function("google_docs_create_document")
        assert func is not None and callable(func)
        print("✅ Test 8: Get tool function - google_docs_create_document")
        passed += 1
    except Exception as e:
        print(f"❌ Test 8: {e}")
        failed += 1
    
    # Test 9: Tool processor initialization
    try:
        processor = ToolCallProcessor(executor)
        assert processor.executor is not None
        assert len(processor.executor.registry.tools) > 500
        print("✅ Test 9: Tool processor initialization")
        passed += 1
    except Exception as e:
        print(f"❌ Test 9: {e}")
        failed += 1
    
    # Test 10: List tools by platform
    try:
        gmail_tools = executor.list_tools_for_platform("gmail")
        assert len(gmail_tools) > 20, f"Expected >20 Gmail tools, got {len(gmail_tools)}"
        
        docs_tools = executor.list_tools_for_platform("google_docs")
        assert len(docs_tools) > 15, f"Expected >15 Docs tools, got {len(docs_tools)}"
        
        slack_tools = executor.list_tools_for_platform("slack")
        assert len(slack_tools) > 10, f"Expected >10 Slack tools, got {len(slack_tools)}"
        
        print("✅ Test 10: List tools by platform (Gmail, Docs, Slack)")
        passed += 1
    except Exception as e:
        print(f"❌ Test 10: {e}")
        failed += 1
    
    # Test 11: Tool schemas have parameters
    try:
        tool = registry.get_tool("gmail_send_email")
        assert tool is not None
        
        params = tool.get("parameters", {})
        assert len(params) > 0, "Tool should have parameters"
        assert "to" in params, "Should have 'to' parameter"
        
        # Check required
        required = [n for n, p in params.items() if p.get("required")]
        assert "to" in required, "'to' should be required"
        assert "subject" in required, "'subject' should be required"
        
        print("✅ Test 11: Tool schemas with parameters and required fields")
        passed += 1
    except Exception as e:
        print(f"❌ Test 11: {e}")
        failed += 1
    
    # Test 12: Google Workspace implementations available
    try:
        gmail_impl = registry.get_implementation("gmail")
        assert gmail_impl is not None
        assert hasattr(gmail_impl, "gmail_send_email")
        assert hasattr(gmail_impl, "gmail_list_messages")
        
        docs_impl = registry.get_implementation("google_docs")
        assert docs_impl is not None
        assert hasattr(docs_impl, "google_docs_create_document")
        
        print("✅ Test 12: Google Workspace implementations available")
        passed += 1
    except Exception as e:
        print(f"❌ Test 12: {e}")
        failed += 1
    
    # Summary
    print("\n" + "="*80)
    print(f"RESULTS: {passed} PASSED, {failed} FAILED")
    print("="*80 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
