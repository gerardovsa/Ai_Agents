from tools.registry_v3 import RegistryV3

registry = RegistryV3()

print("Test: Calling through registry.execute_tool")

print("\nTest 1: execute_tool via registry")
try:
    result = registry.execute_tool('execute_tool', tool_name='gmail_list_available_accounts')
    print(f"  Success: {result.get('success')}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:80]}")

print("\nTest 2: get_tool_schema via registry")
try:
    result = registry.execute_tool('get_tool_schema', tool_name='gmail_send_email')
    print(f"  Success: {result.get('success')}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:80]}")
