"""Test Google Forms tools with user 12 (who has OAuth credentials)"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from tools.registry_v3 import RegistryV3

print("="*80)
print("GOOGLE FORMS TEST - USER 12 (HAS OAUTH CREDENTIALS)")
print("="*80)

# Initialize registry
print("\n[1/2] Initializing Registry...")
registry = RegistryV3()
print(f"Registry loaded: {len(registry.tools)} total tools")

# Test cases with user 12
test_cases = [
    {
        "name": "google_forms_create_form",
        "description": "Create simple form with description",
        "params": {
            "title": "Test Form from AI Agent",
            "description": "This form was created by an AI agent to test the Google Forms API",
            "document_title": "AI Agent Test Form",
            "shareable": True,
            "_user_id": 12,
            "_injected_credentials": True
        }
    },
    {
        "name": "google_forms_create_complete_form",
        "description": "Create complete form with questions",
        "params": {
            "title": "Complete Test Form",
            "description": "Form with multiple questions",
            "questions": [
                {"question": "What is your name?", "type": "TEXT"},
                {"question": "What is your email?", "type": "TEXT"},
                {"question": "How would you rate this test?", "type": "MULTIPLE_CHOICE", 
                 "options": ["Excellent", "Good", "Fair", "Poor"]}
            ],
            "shareable": True,
            "_user_id": 12,
            "_injected_credentials": True
        }
    },
    {
        "name": "google_forms_ai_generate_form",
        "description": "AI-generated customer feedback form",
        "params": {
            "prompt": "Create a customer feedback survey with 5 questions about product satisfaction",
            "form_type": "survey",
            "shareable": True,
            "_user_id": 12,
            "_injected_credentials": True
        }
    }
]

print(f"\n[2/2] Testing {len(test_cases)} Google Forms tools...")
print("="*80)

passed = 0
failed = 0
created_forms = []

for i, test_case in enumerate(test_cases, 1):
    tool_name = test_case["name"]
    description = test_case["description"]
    params = test_case["params"]
    
    print(f"\n[{i}/{len(test_cases)}] {tool_name}")
    print(f"      Description: {description}")
    print(f"      Using user_id: {params.get('_user_id')}")
    
    try:
        result = registry.execute_tool(tool_name=tool_name, **params)
        
        # Check result
        if isinstance(result, dict):
            if result.get("success") or result.get("form_id"):
                print(f"      ✅ SUCCESS - Form created!")
                if result.get("form_id"):
                    print(f"         Form ID: {result['form_id']}")
                if result.get("responder_uri"):
                    print(f"         Respond: {result['responder_uri']}")
                if result.get("edit_uri"):
                    print(f"         Edit: {result['edit_uri']}")
                created_forms.append({
                    'tool': tool_name,
                    'form_id': result.get('form_id'),
                    'responder_uri': result.get('responder_uri'),
                    'edit_uri': result.get('edit_uri')
                })
                passed += 1
            elif result.get("success") is False:
                error = result.get("error", "Unknown")
                print(f"      ❌ FAILED - {str(error)[:100]}")
                failed += 1
            else:
                print(f"      ✅ SUCCESS - Returned: {type(result).__name__}")
                passed += 1
        else:
            print(f"      ✅ SUCCESS - Returned: {type(result).__name__}")
            passed += 1
            
    except Exception as e:
        error_msg = str(e)
        print(f"      ❌ FAILED - {type(e).__name__}: {error_msg[:100]}")
        failed += 1

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Total Tests:   {len(test_cases)}")
print(f"Passed:        {passed} ✅")
print(f"Failed:        {failed} ❌")
success_rate = (passed / len(test_cases) * 100) if test_cases else 0
print(f"Success Rate:  {success_rate:.1f}%")

if created_forms:
    print("\n" + "="*80)
    print("CREATED FORMS")
    print("="*80)
    for form in created_forms:
        print(f"\n{form['tool']}:")
        print(f"  Form ID: {form['form_id']}")
        print(f"  Respond: {form['responder_uri']}")
        print(f"  Edit:    {form['edit_uri']}")

print("\n" + "="*80)
if failed == 0:
    print("RESULT: ✅ ALL TESTS PASSED!")
    print("Google Forms tools are working correctly with OAuth credentials!")
elif passed > 0:
    print(f"RESULT: ⚠️  PARTIAL SUCCESS - {passed}/{len(test_cases)} tests passed")
else:
    print("RESULT: ❌ ALL TESTS FAILED")
print("="*80)
