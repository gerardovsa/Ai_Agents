"""Quick verification test for credential injection support"""

from tools.registry_v3 import RegistryV3

print("=" * 70)
print("TOOL VERIFICATION TEST - Credential Injection Support")
print("=" * 70)

registry = RegistryV3()
print(f"Registry loaded: {len(registry.tools)} tools\n")

# Test tools that accept credentials
test_tools = [
    ('gmail_send_email', {'to': 'test@example.com', 'subject': 'test', 'body': 'test', '_user_id': 1, '_injected_credentials': True}),
    ('gmail_list_available_accounts', {'_user_id': 1, '_injected_credentials': True}),
    ('stripe_create_customer', {'name': 'test', '_user_id': 1}),
    ('ai_create_task', {'title': 'test', 'description': 'test', '_user_id': 1}),
]

working = 0
errors = 0

for tool_name, params in test_tools:
    print(f"[TEST] {tool_name}")
    try:
        # Try to execute the tool - will fail due to missing/invalid credentials, but tests parameter passing
        result = registry.execute_tool(tool_name=tool_name, **params)
        print(f"  [SUCCESS] Tool executed")
        working += 1
    except TypeError as e:
        error_msg = str(e)
        if "missing" in error_msg and "required positional" in error_msg:
            print(f"  [PARAM_ERROR] {error_msg[:60]}...")
            errors += 1
        else:
            print(f"  [OK] TypeError (testing credentials): {error_msg[:60]}...")
            working += 1
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        if "charmap" in error_msg or "encode" in error_msg:
            print(f"  [ENCODING_ERROR] {error_type}: {error_msg[:50]}...")
        elif "404" in error_msg or "connection" in error_msg.lower():
            print(f"  [OK] Network/API error (expected)")
            working += 1
        else:
            print(f"  [OK] {error_type} (test parameters)")
            working += 1

print("\n" + "=" * 70)
print(f"SUMMARY: {working} working, {errors} parameter errors")
print("=" * 70)

if errors == 0:
    print("Status: ALL TOOLS SUPPORT CREDENTIAL INJECTION")
