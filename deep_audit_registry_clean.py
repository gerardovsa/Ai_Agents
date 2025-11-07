#!/usr/bin/env python3
"""
DEEP REGISTRY AUDIT - Test actual tool execution
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 80)
print("DEEP REGISTRY AUDIT - Testing Tool Execution")
print("=" * 80)

# Load registry
from tools.registry_v3 import RegistryV3

print("\nLoading registry...")
registry = RegistryV3()
print(f"[OK] Registry loaded: {len(registry.tools)} tools")

# Get all tool names
all_tools = sorted(registry.tools.keys())

print(f"\nTesting {len(all_tools)} tools...")
print("(This will attempt to call each tool with minimal/mock parameters)\n")

# Categorize results
results = {
    "working": [],
    "auth_required": [],
    "param_error": [],
    "not_found": [],
    "execution_error": [],
}

# Test specific high-value tools
high_priority_tools = [
    "gsheets_create",
    "gsheets_write",
    "gsheets_read",
    "gmail_send_email",
    "gmail_list_available_accounts",
    "google_calendar_create_event",
    "google_forms_create_form",
    "google_docs_create",
    "synergy_update_session",
    "synergy_get_session",
]

# Mock parameters
mock_params = {
    "title": "Test",
    "name": "Test",
    "message": "Test",
    "content": "Test",
    "to": "test@test.com",
    "subject": "Test",
    "body": "Test",
    "summary": "Test",
    "start_time": "2025-11-05T10:00:00Z",
    "end_time": "2025-11-05T11:00:00Z",
    "spreadsheet_id": "test",
    "sheet_name": "Sheet1",
    "data": [[1, 2, 3]],
    "updates": {"status": "test"},
    "session_id": "sess_test",
    "_user_id": 1,
    "_injected_credentials": True,
}

print("=" * 80)
print("TESTING HIGH-PRIORITY TOOLS")
print("=" * 80)

for tool_name in high_priority_tools:
    if tool_name not in registry.tools:
        print(f"\n[NOTFOUND] {tool_name}")
        results["not_found"].append(tool_name)
        continue
    
    print(f"\n[TEST] {tool_name}")
    
    try:
        # Get tool schema
        tool_schema = registry.tools[tool_name]
        params = tool_schema.get("parameters", {})
        
        # Build minimal params
        test_params = {}
        for param_name in params.keys():
            if param_name in mock_params:
                test_params[param_name] = mock_params[param_name]
        
        # Add auth params
        test_params["_user_id"] = 1
        test_params["_injected_credentials"] = True
        
        # Try to execute
        result = registry.execute_tool(tool_name, **test_params)
        
        if isinstance(result, dict) and result.get("error"):
            error = result["error"]
            if "requires _user_id" in str(error):
                print(f"  [AUTH_ERROR] {error}")
                results["auth_required"].append((tool_name, str(error)))
            else:
                print(f"  [ERROR] {error}")
                results["execution_error"].append((tool_name, str(error)))
        else:
            print(f"  [SUCCESS] Type: {type(result).__name__}")
            results["working"].append(tool_name)
    
    except Exception as e:
        error_str = str(e)
        print(f"  [EXCEPTION] {error_str[:100]}")
        
        if "_user_id" in error_str or "authenticate" in error_str.lower():
            results["auth_required"].append((tool_name, error_str))
        elif "missing" in error_str.lower() or "required" in error_str.lower():
            results["param_error"].append((tool_name, error_str))
        else:
            results["execution_error"].append((tool_name, error_str))

# Print summary
print("\n" + "=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

print(f"\n[WORKING] {len(results['working'])} tools")
for tool in results['working']:
    print(f"  - {tool}")

print(f"\n[AUTH_REQUIRED] {len(results['auth_required'])} tools")
for tool, error in results['auth_required'][:5]:
    print(f"  - {tool}")
    print(f"    Error: {error[:60]}...")

print(f"\n[PARAM_ERROR] {len(results['param_error'])} tools")
for tool, error in results['param_error'][:5]:
    print(f"  - {tool}")
    print(f"    Error: {error[:60]}...")

print(f"\n[EXECUTION_ERROR] {len(results['execution_error'])} tools")
for tool, error in results['execution_error'][:5]:
    print(f"  - {tool}")
    print(f"    Error: {error[:60]}...")

print(f"\n[NOT_FOUND] {len(results['not_found'])} tools")
for tool in results['not_found']:
    print(f"  - {tool}")

# Statistics
print("\n" + "=" * 80)
print("STATISTICS")
print("=" * 80)

total = len(results['working']) + len(results['auth_required']) + len(results['param_error']) + len(results['execution_error']) + len(results['not_found'])

working_pct = 100 * len(results['working']) / total if total > 0 else 0
auth_pct = 100 * len(results['auth_required']) / total if total > 0 else 0
param_pct = 100 * len(results['param_error']) / total if total > 0 else 0
exec_pct = 100 * len(results['execution_error']) / total if total > 0 else 0
notfound_pct = 100 * len(results['not_found']) / total if total > 0 else 0

print(f"""
Tools Tested:           {total}
Working:                {len(results['working'])} ({working_pct:.0f}%)
Auth Issues:            {len(results['auth_required'])} ({auth_pct:.0f}%)
Param Issues:           {len(results['param_error'])} ({param_pct:.0f}%)
Execution Errors:       {len(results['execution_error'])} ({exec_pct:.0f}%)
Not Found:              {len(results['not_found'])} ({notfound_pct:.0f}%)

KEY FINDING:
  {len(results['working'])} out of {total} high-priority tools work!
  Failure rate: {100 - working_pct:.0f}%
""")

# Final status
print("=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
