"""
FILE: scripts/testing/test_microsoft_google_execution.py
PURPOSE: Test actual tool execution with registry.execute_tool() wrapper

DEPENDENCIES:
- tools.registry_v3 (RegistryV3 class)
- requests (HTTP client)

EXPORTS:
- None (testing script)

USED BY:
- Manual execution for tool testing

RELATED FILES:
- tools/registry_v3.py (execute_tool method)
- tools/implementations/microsoft_*.py (Microsoft tools)
- google_workspace/*.py (Google tools)

NOTES:
- Tests with mock data (no real API calls needed initially)
- Tests parameter passing via **kwargs
- Tests error handling

LAST MODIFIED: 2025-01-14 - Created for tool execution testing
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from tools.registry_v3 import RegistryV3

print("=" * 100)
print("TOOL EXECUTION TEST - MICROSOFT & GOOGLE TOOLS")
print("=" * 100)

# Initialize registry
print("\n[1/3] Initializing Registry...")
try:
    registry = RegistryV3()
    print(f"✅ Registry loaded: {len(registry.tools)} total tools")
except Exception as e:
    print(f"❌ Failed to load registry: {e}")
    sys.exit(1)

# Get sample tools to test
print("\n[2/3] Preparing test tools...")

test_cases = [
    # Microsoft Tools
    {
        "name": "microsoft_outlook_list_messages",
        "category": "Microsoft Outlook",
        "params": {
            "folder": "inbox",
            "limit": 5,
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_teams_list_teams",
        "category": "Microsoft Teams",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_word_list_documents",
        "category": "Microsoft Word",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_excel_list_workbooks",
        "category": "Microsoft Excel",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_onedrive_list_files",
        "category": "Microsoft OneDrive",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_calendar_list_events",
        "category": "Microsoft Calendar",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_forms_list_forms",
        "category": "Microsoft Forms",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_onenote_list_notebooks",
        "category": "Microsoft OneNote",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_sharepoint_list_sites",
        "category": "Microsoft SharePoint",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "microsoft_todo_list_tasks",
        "category": "Microsoft Todo",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    # Google Tools
    {
        "name": "gmail_list_messages",
        "category": "Gmail",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "limit": 5
        }
    },
    {
        "name": "google_docs_create_document",
        "category": "Google Docs",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "title": "Test Document"
        }
    },
    {
        "name": "google_sheets_create_spreadsheet",
        "category": "Google Sheets",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing",
            "title": "Test Spreadsheet"
        }
    },
]

print(f"✅ Prepared {len(test_cases)} test cases")

# Test execution
print("\n[3/3] Testing tool execution...")
print("=" * 100)

passed = 0
failed = 0
errors_by_type = {}

for i, test_case in enumerate(test_cases, 1):
    tool_name = test_case["name"]
    category = test_case["category"]
    params = test_case["params"]
    
    # Check if tool exists
    if tool_name not in registry.tools:
        print(f"\n[{i}/{len(test_cases)}] ❌ TOOL NOT FOUND: {tool_name}")
        print(f"      Category: {category}")
        failed += 1
        errors_by_type.setdefault("NOT_FOUND", []).append(tool_name)
        continue
    
    print(f"\n[{i}/{len(test_cases)}] Testing: {tool_name}")
    print(f"      Category: {category}")
    print(f"      Params: {list(params.keys())}")
    
    try:
        # Execute tool via registry (tool_name must be in kwargs!)
        result = registry.execute_tool(tool_name=tool_name, **params)
        
        # Check result
        if isinstance(result, dict) and result.get("success") is False:
            # Tool executed but returned error (expected with mock token)
            error_msg = result.get("error", "Unknown error")
            if "401" in str(error_msg) or "Unauthorized" in str(error_msg) or "mock_token" in str(error_msg):
                print(f"      ✅ PASSED (expected auth error with mock token)")
                print(f"         Error: {error_msg[:80]}")
                passed += 1
            else:
                print(f"      ⚠️  PARTIAL (executed but API error)")
                print(f"         Error: {error_msg[:80]}")
                passed += 1
        elif isinstance(result, list):
            print(f"      ✅ PASSED (returned list with {len(result)} items)")
            passed += 1
        elif isinstance(result, dict) and "success" in result:
            print(f"      ✅ PASSED (returned dict with success={result['success']})")
            passed += 1
        else:
            print(f"      ✅ PASSED (returned {type(result).__name__})")
            passed += 1
            
    except TypeError as e:
        error_msg = str(e)
        print(f"      ❌ FAILED: {error_msg[:100]}")
        failed += 1
        errors_by_type.setdefault("PARAMETER_ERROR", []).append((tool_name, error_msg))
    except Exception as e:
        error_msg = str(e)
        print(f"      ❌ FAILED: {error_msg[:100]}")
        failed += 1
        error_type = type(e).__name__
        errors_by_type.setdefault(error_type, []).append((tool_name, error_msg))

# Summary
print("\n" + "=" * 100)
print("TEST SUMMARY")
print("=" * 100)
print(f"Total Tests: {len(test_cases)}")
print(f"Passed:      {passed} ✅")
print(f"Failed:      {failed} ❌")
print(f"Success Rate: {(passed / len(test_cases) * 100):.1f}%")

if errors_by_type:
    print("\n" + "=" * 100)
    print("ERROR ANALYSIS")
    print("=" * 100)
    for error_type, errors in sorted(errors_by_type.items()):
        print(f"\n{error_type}: {len(errors)} occurrences")
        for item in errors[:3]:  # Show first 3
            if isinstance(item, tuple):
                tool, msg = item
                print(f"  - {tool}: {msg[:70]}")
            else:
                print(f"  - {item}")

print("\n" + "=" * 100)
print("INTERPRETATION")
print("=" * 100)

if failed == 0:
    print("✅ ALL TOOLS EXECUTING SUCCESSFULLY!")
    print("   (Returns indicate tools are properly registered and accepting parameters)")
    print("   (Actual API errors are expected with mock tokens)")
elif failed <= 3:
    print("⚠️  MOST TOOLS WORKING - Check specific failures")
    print("   Likely issues:")
    print("   - Parameter naming mismatch")
    print("   - execute_tool() not stripping internal parameters before spreading")
else:
    print("❌ SIGNIFICANT FAILURES - Investigate error types")
    print("   Most common error types:")
    for error_type in sorted(errors_by_type.keys(), key=lambda x: -len(errors_by_type[x]))[:3]:
        print(f"   - {error_type}: {len(errors_by_type[error_type])} tools")

print("\n" + "=" * 100)
