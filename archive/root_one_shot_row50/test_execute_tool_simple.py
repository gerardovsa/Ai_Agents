"""
Simple direct test of execute_tool parameter unwrapping
Tests calling execute_tool the way the AI agent calls it
"""

import sys
import os

# Add paths
ai_infra = os.path.abspath(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
sys.path.insert(0, ai_infra)
tools_path = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_path)

from tools.implementations.meta_tools import execute_tool

print("=" * 100)
print("DIRECT TEST: execute_tool with nested parameters dict")
print("=" * 100)

# Simulate how the AI agent is calling it (INCORRECT format, but we fix it)
print("\nCalling execute_tool the way the AI agent does:")
print("  execute_tool(")
print("    tool_name='inhouse_execute_sql',")
print("    _user_id=14,")
print("    _injected_credentials={},")
print("    parameters={'query': 'SELECT TOP 5...'}  # <- NESTED, should be unwrapped")
print("  )")

result = execute_tool(
    tool_name='inhouse_execute_sql',
    _user_id=14,
    _injected_credentials={},
    parameters={
        'query': 'SELECT TOP 5 OrderID, ClientName FROM Orders ORDER BY OrderDate DESC'
    }
)

print("\n" + "=" * 100)
print("RESULT:")
print("=" * 100)
print(f"Success: {result.get('success')}")

if result.get('success'):
    print("\n✅ FIX WORKS! Parameters were unwrapped correctly!")
    inner_result = result.get('result', {})
    print(f"\nTool executed: {result.get('tool')}")
    print(f"Inner success: {inner_result.get('success')}")
    
    if isinstance(inner_result, list):
        print(f"Rows returned: {len(inner_result)}")
        if len(inner_result) > 0:
            print(f"\nSample row:")
            for key, value in inner_result[0].items():
                print(f"  {key}: {value}")
else:
    print("\n❌ FIX FAILED!")
    print(f"Error: {result.get('error')}")
    if 'traceback' in result:
        print(f"\nTraceback:\n{result['traceback']}")

print("\n" + "=" * 100)
