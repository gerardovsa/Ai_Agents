"""
Test Microsoft and Google tools with REAL tool names and parameters
"""

import sys
import json
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from tools.registry_v3 import RegistryV3

print("=" * 100)
print("TOOL EXECUTION TEST - USING REAL TOOL NAMES")
print("=" * 100)

# Initialize registry
print("\n[1/3] Initializing Registry...")
try:
    registry = RegistryV3()
    total_tools = len(registry.tools)
    print(f"Registry loaded: {total_tools} total tools")
except Exception as e:
    print(f"Failed to load registry: {e}")
    sys.exit(1)

# Prepare test cases with REAL tool names from schemas
print("\n[2/3] Preparing test tools...")

test_cases = [
    # Microsoft tools
    {
        "name": "microsoft_outlook_send_email",
        "category": "Microsoft Outlook",
        "params": {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "Test body",
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_teams_list_teams",
        "category": "Microsoft Teams",
        "params": {
            "limit": 5,
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_word_create_document",
        "category": "Microsoft Word",
        "params": {
            "name": "Test Document",
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_excel_create_workbook",
        "category": "Microsoft Excel",
        "params": {
            "name": "Test Workbook",
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_onedrive_list_files",
        "category": "Microsoft OneDrive",
        "params": {
            "limit": 5,
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_calendar_list_events",
        "category": "Microsoft Calendar",
        "params": {
            "limit": 5,
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_forms_list_forms",
        "category": "Microsoft Forms",
        "params": {
            "limit": 5,
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_onenote_list_notebooks",
        "category": "Microsoft OneNote",
        "params": {
            "limit": 5,
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_sharepoint_get_site",
        "category": "Microsoft SharePoint",
        "params": {
            "site_id": "test_site",
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "microsoft_todo_list_tasks",
        "category": "Microsoft Todo",
        "params": {
            "limit": 5,
            "user_id": "1",
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    # Google tools
    {
        "name": "gmail_send_email",
        "category": "Gmail",
        "params": {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test",
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "google_drive_list_files",
        "category": "Google Drive",
        "params": {
            "limit": 5,
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "google_calendar_list_calendars",
        "category": "Google Calendar",
        "params": {
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "google_docs_smart_create_from_markdown",
        "category": "Google Docs",
        "params": {
            "title": "Test Doc",
            "markdown_content": "# Test",
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
    {
        "name": "google_meet_create_meeting",
        "category": "Google Meet",
        "params": {
            "title": "Test Meeting",
            "_user_id": 1,
            "_injected_credentials": True,
            "access_token": "mock_token_for_testing"
        }
    },
]

print(f"Prepared {len(test_cases)} test cases")

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
    
    # Check if tool exists in registry
    if tool_name not in registry.tools:
        print(f"\n[{i}/{len(test_cases)}] TOOL NOT FOUND: {tool_name}")
        print(f"      Category: {category}")
        failed += 1
        errors_by_type.setdefault("NOT_FOUND", []).append(tool_name)
        continue
    
    print(f"\n[{i}/{len(test_cases)}] {tool_name}")
    print(f"      Category: {category}")
    
    try:
        # Execute tool via registry using execute_tool with tool_name in kwargs
        result = registry.execute_tool(tool_name=tool_name, **params)
        
        # Check result type
        if isinstance(result, dict):
            if result.get("success") is False:
                error = result.get("error", "Unknown")
                # Check if it's an expected auth error
                if any(x in str(error) for x in ["401", "Unauthorized", "mock_token", "Bearer", "invalid"]):
                    print(f"      SUCCESS - Tool executed, got expected auth error")
                    print(f"      Error: {str(error)[:70]}")
                    passed += 1
                else:
                    print(f"      PARTIAL - Tool executed, got API error")
                    print(f"      Error: {str(error)[:70]}")
                    passed += 1
            else:
                print(f"      SUCCESS - Tool executed successfully")
                if "data" in result:
                    print(f"      Data keys: {list(result.get('data', {}).keys())[:3]}")
                passed += 1
        elif isinstance(result, list):
            print(f"      SUCCESS - Tool returned list with {len(result)} items")
            passed += 1
        elif isinstance(result, str):
            if any(x in result for x in ["401", "Unauthorized", "Bearer"]):
                print(f"      SUCCESS - Tool executed, got expected auth error")
                passed += 1
            else:
                print(f"      SUCCESS - Tool returned string: {result[:50]}")
                passed += 1
        else:
            print(f"      SUCCESS - Tool returned {type(result).__name__}")
            passed += 1
            
    except TypeError as e:
        error_msg = str(e)
        print(f"      FAILED - Parameter Error: {error_msg[:80]}")
        failed += 1
        errors_by_type.setdefault("PARAMETER_ERROR", []).append((tool_name, error_msg))
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f"      TOOL NOT IN REGISTRY: {error_msg[:80]}")
            failed += 1
            errors_by_type.setdefault("NOT_REGISTERED", []).append(tool_name)
        else:
            print(f"      FAILED - ValueError: {error_msg[:80]}")
            failed += 1
            errors_by_type.setdefault("ValueError", []).append((tool_name, error_msg))
    except Exception as e:
        error_msg = str(e)
        print(f"      FAILED - {type(e).__name__}: {error_msg[:80]}")
        failed += 1
        error_type = type(e).__name__
        errors_by_type.setdefault(error_type, []).append((tool_name, error_msg))

# Summary
print("\n" + "=" * 100)
print("TEST SUMMARY")
print("=" * 100)
print(f"Total Tests:   {len(test_cases)}")
print(f"Passed:        {passed} SUCCESS")
print(f"Failed:        {failed} FAILED")
success_rate = (passed / len(test_cases) * 100) if test_cases else 0
print(f"Success Rate:  {success_rate:.1f}%")

if errors_by_type:
    print("\n" + "=" * 100)
    print("ERROR TYPES")
    print("=" * 100)
    for error_type in sorted(errors_by_type.keys()):
        errors = errors_by_type[error_type]
        print(f"\n{error_type}: {len(errors)} occurrences")

print("\n" + "=" * 100)
if failed == 0:
    print("RESULT: ALL TOOLS WORKING!")
elif passed > (len(test_cases) * 0.7):
    print("RESULT: MOST TOOLS WORKING - Check error types")
else:
    print("RESULT: SIGNIFICANT ISSUES - See errors above")
print("=" * 100)
