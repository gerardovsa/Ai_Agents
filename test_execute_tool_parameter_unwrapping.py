"""
Test execute_tool meta-tool parameter unwrapping fix
Tests that nested 'parameters' dicts are properly unwrapped

ISSUE: AI agent was calling:
  execute_tool(tool_name='inhouse_execute_sql', parameters={'query': 'SELECT...'})

But inhouse_execute_sql expects:
  inhouse_execute_sql(query='SELECT...')

FIX: Added parameter unwrapping logic to execute_tool that detects nested
'parameters' dict and merges it into main params.

Created: Dec 24, 2025
"""

import sys
import os
from pathlib import Path

# Add AI_infrastructure to path
ai_infra = os.path.abspath(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
sys.path.insert(0, ai_infra)

# Add tools to path
tools_path = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_path)

from tools.registry_v3 import RegistryV3

def test_parameter_unwrapping():
    """Test that nested parameters dict is unwrapped correctly"""
    
    print("=" * 100)
    print("TEST: execute_tool parameter unwrapping")
    print("=" * 100)
    
    registry = RegistryV3()
    
    # Test Case 1: Nested parameters dict (AI agent format - INCORRECT but we fix it)
    print("\n[TEST 1] Nested parameters dict (AI agent wrapping - should auto-unwrap)")
    print("-" * 80)
    print("Calling: execute_tool(tool_name='inhouse_execute_sql', parameters={'query': '...'})")
    print("Expected: Should unwrap to execute_tool(tool_name='inhouse_execute_sql', query='...')")
    
    result = registry.execute_tool(
        tool_name='execute_tool',
        _user_id=14,  # Simulated user
        _injected_credentials={},
        tool_name_inner='inhouse_execute_sql',  # Target tool name
        parameters={
            # This nested dict should be unwrapped automatically
            'query': 'SELECT TOP 5 OrderID, ClientName FROM Orders ORDER BY OrderDate DESC'
        }
    )
    
    print(f"\nResult success: {result.get('success')}")
    if result.get('success'):
        print(f"✅ TEST 1 PASSED - Nested parameters unwrapped successfully!")
        inner_result = result.get('result', {})
        print(f"   Tool executed: {result.get('tool')}")
        print(f"   Inner success: {inner_result.get('success')}")
        if isinstance(inner_result, list) and len(inner_result) > 0:
            print(f"   Rows returned: {len(inner_result)}")
            print(f"   Sample row: {inner_result[0]}")
    else:
        print(f"❌ TEST 1 FAILED")
        print(f"   Error: {result.get('error')}")
        if 'traceback' in result:
            print(f"   Traceback: {result['traceback']}")
    
    # Test Case 2: Flat parameters (correct format)
    print("\n" + "=" * 100)
    print("[TEST 2] Flat parameters (already correct format)")
    print("-" * 80)
    print("Calling: execute_tool(tool_name='inhouse_execute_sql', query='...')")
    
    result2 = registry.execute_tool(
        tool_name='execute_tool',
        _user_id=14,
        _injected_credentials={},
        tool_name_inner='inhouse_execute_sql',  # Target tool name
        query='SELECT TOP 3 OrderID, ClientName FROM Orders ORDER BY OrderDate DESC'
    )
    
    print(f"\nResult success: {result2.get('success')}")
    if result2.get('success'):
        print(f"✅ TEST 2 PASSED - Flat parameters work correctly!")
        inner_result2 = result2.get('result', {})
        print(f"   Tool executed: {result2.get('tool')}")
        print(f"   Inner success: {inner_result2.get('success')}")
        if isinstance(inner_result2, list) and len(inner_result2) > 0:
            print(f"   Rows returned: {len(inner_result2)}")
            print(f"   Sample row: {inner_result2[0]}")
    else:
        print(f"❌ TEST 2 FAILED")
        print(f"   Error: {result2.get('error')}")
        if 'traceback' in result2:
            print(f"   Traceback: {result2['traceback']}")
    
    # Summary
    print("\n" + "=" * 100)
    print("TEST SUMMARY")
    print("=" * 100)
    
    test1_pass = result.get('success', False)
    test2_pass = result2.get('success', False)
    
    if test1_pass and test2_pass:
        print("✅ ALL TESTS PASSED")
        print("\n🎉 FIX CONFIRMED: execute_tool now properly unwraps nested 'parameters' dicts")
        print("   - AI agent can call with nested format: parameters={'query': '...'}")
        print("   - AI agent can call with flat format: query='...'")
        print("   - Both formats now work correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Test 1 (nested): {'PASS' if test1_pass else 'FAIL'}")
        print(f"   Test 2 (flat): {'PASS' if test2_pass else 'FAIL'}")
        return False

if __name__ == '__main__':
    try:
        success = test_parameter_unwrapping()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
