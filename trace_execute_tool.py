"""Detailed trace of the parameter conflict"""

from tools.implementations.meta_tools import execute_tool
import inspect

print("execute_tool signature:", inspect.signature(execute_tool))
print()

# Test 1: Direct call with tool_name as kwarg
print("[TEST 1] Direct call to execute_tool")
try:
    result = execute_tool(tool_name='gmail_send_email', to='test@example.com')
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
except TypeError as e:
    print(f"TypeError: {e}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print()

# Test 2: Direct call with tool_name positional
print("[TEST 2] Direct call with tool_name positional")
try:
    result = execute_tool('gmail_send_email', to='test@example.com')
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
except TypeError as e:
    print(f"TypeError: {e}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
