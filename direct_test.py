from tools.implementations.meta_tools import get_tool_schema, execute_tool

print("Test 1: get_tool_schema direct")
result = get_tool_schema(tool_name='gmail_send_email')
print(f"  Success: {result.get('success')}")

print("\nTest 2: execute_tool direct")  
result = execute_tool(tool_name='gmail_list_available_accounts')
print(f"  Success: {result.get('success')}")
