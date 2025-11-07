#!/usr/bin/env python3
"""
DEEP REGISTRY AUDIT - Test actual tool execution

This audit will:
1. Load all 606 tools from registry
2. Try to execute each one
3. Identify which ones work vs fail
4. Categorize failures
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

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
    "timeout": [],
}

# Test each tool with mock parameters
mock_params = {
    "title": "Test",
    "name": "Test",
    "message": "Test",
    "content": "Test",
    "text": "Test",
    "query": "Test",
    "to": "test@test.com",
    "email": "test@test.com",
    "subject": "Test",
    "body": "Test",
    "summary": "Test",
    "description": "Test",
    "start_time": "2025-11-05T10:00:00Z",
    "end_time": "2025-11-05T11:00:00Z",
    "start_date": "2025-11-05",
    "end_date": "2025-11-06",
    "spreadsheet_id": "test",
    "sheet_name": "Sheet1",
    "data": [[1, 2, 3]],
    "updates": {"status": "test"},
    "session_id": "sess_test",
    "_user_id": 1,
    "_injected_credentials": True,
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

print("=" * 80)
print("TESTING HIGH-PRIORITY TOOLS FIRST")
print("=" * 80)

for tool_name in high_priority_tools:
    if tool_name not in registry.tools:
        print(f"\n❌ {tool_name}: NOT FOUND in registry")
        results["not_found"].append(tool_name)
        continue
    
    print(f"\nTesting: {tool_name}")
    
    try:
        # Get tool schema to see what params it needs
        tool_schema = registry.tools[tool_name]
        params = tool_schema.get("parameters", {})
        
        print(f"  Schema parameters: {list(params.keys())}")
        
        # Build minimal params from mock
        test_params = {}
        for param_name in params.keys():
            if param_name in mock_params:
                test_params[param_name] = mock_params[param_name]
        
        # Add auth params
        if "_user_id" not in test_params:
            test_params["_user_id"] = 1
        if "_injected_credentials" not in test_params:
            test_params["_injected_credentials"] = True
        
        print(f"  Test params: {list(test_params.keys())}")
        
        # Try to execute
        result = registry.execute_tool(tool_name, **test_params)
        
        if isinstance(result, dict) and result.get("error"):
            error = result["error"]
            if "requires _user_id" in str(error):
                print(f"  ⚠️  AUTH ERROR: {error}")
                results["auth_required"].append((tool_name, str(error)))
            else:
                print(f"  ❌ ERROR: {error}")
                results["execution_error"].append((tool_name, str(error)))
        else:
            print(f"  ✅ SUCCESS (returned: {type(result).__name__})")
            results["working"].append(tool_name)
    
    except Exception as e:
        error_str = str(e)
        print(f"  ❌ EXCEPTION: {error_str}")
        
        if "_user_id" in error_str or "authenticate" in error_str.lower():
            results["auth_required"].append((tool_name, error_str))
        elif "missing" in error_str.lower() or "required" in error_str.lower():
            results["param_error"].append((tool_name, error_str))
        else:
            results["execution_error"].append((tool_name, error_str))

# Print summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"\n✅ WORKING: {len(results['working'])}")
for tool in results['working']:
    print(f"  - {tool}")

print(f"\n⚠️  AUTH REQUIRED: {len(results['auth_required'])}")
for tool, error in results['auth_required'][:5]:
    print(f"  - {tool}: {error[:50]}...")

print(f"\n❌ PARAM ERROR: {len(results['param_error'])}")
for tool, error in results['param_error'][:5]:
    print(f"  - {tool}: {error[:50]}...")

print(f"\n❌ EXECUTION ERROR: {len(results['execution_error'])}")
for tool, error in results['execution_error'][:5]:
    print(f"  - {tool}: {error[:50]}...")

print(f"\n❌ NOT FOUND: {len(results['not_found'])}")
for tool in results['not_found']:
    print(f"  - {tool}")

# Calculate stats
total = len(results['working']) + len(results['auth_required']) + len(results['param_error']) + len(results['execution_error']) + len(results['not_found'])

print("\n" + "=" * 80)
print("STATISTICS")
print("=" * 80)
print(f"""
Tools Tested:           {len(high_priority_tools)}
Working:                {len(results['working'])} ({100*len(results['working'])/len(high_priority_tools):.0f}%)
Auth Issues:            {len(results['auth_required'])} ({100*len(results['auth_required'])/len(high_priority_tools):.0f}%)
Param Issues:           {len(results['param_error'])} ({100*len(results['param_error'])/len(high_priority_tools):.0f}%)
Execution Errors:       {len(results['execution_error'])} ({100*len(results['execution_error'])/len(high_priority_tools):.0f}%)
Not Found:              {len(results['not_found'])} ({100*len(results['not_found'])/len(high_priority_tools):.0f}%)

KEY FINDING:
  Only {len(results['working'])} out of {len(high_priority_tools)} high-priority tools work!
  
ISSUES:
  - Auth problems: {len(results['auth_required'])}
  - Parameter problems: {len(results['param_error'])}
  - Execution errors: {len(results['execution_error'])}
  - Missing: {len(results['not_found'])}
""")

# Show actual errors
print("=" * 80)
print("DETAILED ERROR ANALYSIS")
print("=" * 80)

if results['auth_required']:
    print("\nAUTHENTICATION ERRORS:")
    for tool, error in results['auth_required']:
        print(f"\n{tool}:")
        print(f"  {error[:200]}")

if results['param_error']:
    print("\nPARAMETER ERRORS:")
    for tool, error in results['param_error']:
        print(f"\n{tool}:")
        print(f"  {error[:200]}")

if results['execution_error']:
    print("\nEXECUTION ERRORS:")
    for tool, error in results['execution_error']:
        print(f"\n{tool}:")
        print(f"  {error[:200]}")
