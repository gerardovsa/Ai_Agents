"""
Test Google Forms Critical Fixes - November 9, 2025

Tests the 3 critical bugs that were fixed:
1. Basic form creation with description (HTTP 400 fix)
2. Complete form with questions (uses basic creation)
3. AI form generation (BadRequestError fix)
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

def test_basic_form_creation():
    """Test Bug 1 Fix: Form creation with description"""
    print("\n" + "="*70)
    print("TEST 1: Basic Form Creation with Description")
    print("="*70)
    print("Testing: google_forms_create_form")
    print("Expected: Success (was HTTP 400 before fix)")
    print("-"*70)
    
    try:
        registry = RegistryV3()
        
        result = registry.execute_tool(
            tool_name='google_forms_create_form',
            title='Test Form - Description Fix Verification',
            description='This form tests the two-step creation process fix. If you see this description, the fix worked!',
            shareable=True,
            _user_id=12,
            _injected_credentials=True
        )
        
        print("RESULT: SUCCESS")
        print(f"  Form ID: {result.get('form_id', 'N/A')}")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Description Set: {result.get('has_description', 'N/A')}")
        print(f"  Responder URL: {result.get('responder_uri', 'N/A')[:60]}...")
        print(f"  Edit URL: {result.get('edit_uri', 'N/A')[:60]}...")
        
        return True, result
        
    except Exception as e:
        print(f"RESULT: FAILED")
        print(f"  Error: {str(e)[:200]}")
        return False, None


def test_complete_form_creation():
    """Test Bug 1 Fix Extended: Complete form with questions"""
    print("\n" + "="*70)
    print("TEST 2: Complete Form with Questions")
    print("="*70)
    print("Testing: google_forms_create_complete_form")
    print("Expected: Success (depends on Bug 1 fix)")
    print("-"*70)
    
    try:
        registry = RegistryV3()
        
        result = registry.execute_tool(
            tool_name='google_forms_create_complete_form',
            title='Customer Satisfaction Survey - Test',
            description='Please help us improve our service by completing this survey',
            questions=[
                {
                    'type': 'text',
                    'text': 'What is your name?',
                    'required': True
                },
                {
                    'type': 'multiple_choice',
                    'text': 'How satisfied are you with our service?',
                    'options': ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied'],
                    'required': True
                },
                {
                    'type': 'paragraph',
                    'text': 'Please provide any additional comments or suggestions:',
                    'required': False
                }
            ],
            shareable=True,
            _user_id=12,
            _injected_credentials=True
        )
        
        print("RESULT: SUCCESS")
        print(f"  Form ID: {result.get('form_id', 'N/A')}")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Questions Created: {len(result.get('questions', []))}")
        print(f"  Responder URL: {result.get('responder_uri', 'N/A')[:60]}...")
        
        # Show question details
        for i, q in enumerate(result.get('questions', []), 1):
            print(f"  Question {i}: {q.get('text', 'N/A')[:40]}... ({q.get('type', 'N/A')})")
        
        return True, result
        
    except Exception as e:
        print(f"RESULT: FAILED")
        print(f"  Error: {str(e)[:200]}")
        return False, None


def test_ai_form_generation():
    """Test Bug 2 Fix: AI form generation without response_format"""
    print("\n" + "="*70)
    print("TEST 3: AI Form Generation (OpenAI Compatibility)")
    print("="*70)
    print("Testing: google_forms_ai_generate_form")
    print("Expected: Success (was BadRequestError before fix)")
    print("-"*70)
    
    try:
        registry = RegistryV3()
        
        result = registry.execute_tool(
            tool_name='google_forms_ai_generate_form',
            prompt='Create a restaurant feedback survey with 5 questions about food quality, service speed, atmosphere, cleanliness, and likelihood to recommend',
            form_type='survey',
            shareable=True,
            ai_model='gpt-4',
            _user_id=12,
            _injected_credentials=True
        )
        
        print("RESULT: SUCCESS")
        print(f"  Form ID: {result.get('form_id', 'N/A')}")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Questions Created: {result.get('questions_count', 'N/A')}")
        print(f"  AI Model Used: {result.get('ai_model', 'N/A')}")
        print(f"  Responder URL: {result.get('responder_uri', 'N/A')[:60]}...")
        
        # Show generated questions
        for i, q in enumerate(result.get('questions', [])[:5], 1):
            print(f"  Question {i}: {q.get('text', 'N/A')[:50]}...")
        
        return True, result
        
    except Exception as e:
        print(f"RESULT: FAILED")
        print(f"  Error: {str(e)[:200]}")
        
        # Check if it's the specific OpenAI error we fixed
        if 'response_format' in str(e) or 'json_object' in str(e):
            print("  NOTE: This is the exact error we tried to fix!")
            print("  The response_format parameter may still be present")
        
        return False, None


def run_all_tests():
    """Run all Google Forms tests"""
    print("\n")
    print("#"*70)
    print("# GOOGLE FORMS CRITICAL FIXES - VERIFICATION TESTS")
    print("# Date: November 9, 2025")
    print("# Bugs Fixed: 3 (HTTP 400, BadRequestError, HTTP 500)")
    print("#"*70)
    
    results = []
    
    # Test 1: Basic creation
    success1, result1 = test_basic_form_creation()
    results.append(('Basic Form Creation', success1, result1))
    
    # Test 2: Complete form
    success2, result2 = test_complete_form_creation()
    results.append(('Complete Form', success2, result2))
    
    # Test 3: AI generation
    success3, result3 = test_ai_form_generation()
    results.append(('AI Form Generation', success3, result3))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, result in results:
        status = "PASS" if success else "FAIL"
        icon = "+" if success else "-"
        print(f"  {icon} {test_name}: {status}")
        
        if success and result:
            form_id = result.get('form_id', 'N/A')
            url = result.get('responder_uri', 'N/A')
            print(f"    Form: {form_id}")
            print(f"    URL: {url[:60]}...")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\nSTATUS: ALL TESTS PASSED!")
        print("Result: All Google Forms bugs are fixed and verified")
    else:
        print(f"\nSTATUS: {total - passed} TEST(S) FAILED")
        print("Action: Review error messages above for debugging")
    
    print("="*70)
    
    return passed == total


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
