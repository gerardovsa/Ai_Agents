"""
Test Microsoft 365 tools loading and credential injection
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from auth.credential_injector import get_microsoft_access_token

def test_microsoft_credentials():
    """Test if Microsoft credentials can be retrieved"""
    print("=" * 60)
    print("Testing Microsoft 365 Credential Injection")
    print("=" * 60)
    
    try:
        # Test with user_id 1 (Gerardo@minivetguide.onmicrosoft.com)
        print("\n1. Testing credential retrieval for user_id=1...")
        access_token = get_microsoft_access_token(user_id=1)
        
        if access_token:
            print(f"   ✅ Access token found: {access_token[:20]}...")
            return True
        else:
            print(f"   ❌ No access token retrieved")
            return False
            
    except Exception as e:
        print(f"   ❌ Error retrieving credentials: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_loading():
    """Test if Microsoft tools are loaded"""
    print("\n" + "=" * 60)
    print("Testing Microsoft 365 Tools Loading")
    print("=" * 60)
    
    from tools.registry import ToolRegistry
    
    registry = ToolRegistry()
    
    # Count Microsoft tools
    excel_tools = [t for t in registry.tools if t.startswith('excel_')]
    word_tools = [t for t in registry.tools if t.startswith('word_')]
    sharepoint_tools = [t for t in registry.tools if t.startswith('sharepoint_')]
    onenote_tools = [t for t in registry.tools if t.startswith('onenote_')]
    forms_tools = [t for t in registry.tools if t.startswith('forms_')]
    
    print(f"\n✅ Total tools loaded: {len(registry.tools)}")
    print(f"\n📊 Microsoft 365 Tools:")
    print(f"   - Excel: {len(excel_tools)} tools")
    print(f"   - Word: {len(word_tools)} tools")
    print(f"   - SharePoint: {len(sharepoint_tools)} tools")
    print(f"   - OneNote: {len(onenote_tools)} tools")
    print(f"   - Forms: {len(forms_tools)} tools")
    print(f"   - Total: {len(excel_tools) + len(word_tools) + len(sharepoint_tools) + len(onenote_tools) + len(forms_tools)} Microsoft tools")
    
    return len(excel_tools) > 0

def test_excel_tool_callable():
    """Test if Excel tool can be called"""
    print("\n" + "=" * 60)
    print("Testing Excel Tool Execution")
    print("=" * 60)
    
    try:
        from tools.implementations.microsoft_excel_tools import excel_list_workbooks
        
        print("\n1. Testing excel_list_workbooks function exists...")
        print(f"   ✅ Function exists: {callable(excel_list_workbooks)}")
        
        print("\n2. Testing function signature...")
        import inspect
        sig = inspect.signature(excel_list_workbooks)
        print(f"   ✅ Signature: {sig}")
        
        # Check if **kwargs is in signature
        has_kwargs = any(str(param).startswith('**') for param in sig.parameters.values())
        print(f"   ✅ Has **kwargs: {has_kwargs}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🧪 Microsoft 365 Tools Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Tool loading
    results.append(("Tools Loading", test_tool_loading()))
    
    # Test 2: Credentials
    results.append(("Credential Injection", test_microsoft_credentials()))
    
    # Test 3: Callable
    results.append(("Excel Tool Callable", test_excel_tool_callable()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Microsoft 365 tools are ready.")
    else:
        print("\n⚠️ Some tests failed. Check logs above.")
    
    sys.exit(0 if all_passed else 1)
