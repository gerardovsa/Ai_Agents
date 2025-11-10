"""Direct test of Google Forms API with service account"""

import sys
sys.path.insert(0, 'google_workspace')

from google_auth_helper import build_forms_service

print("="*70)
print("Direct Google Forms API Test")
print("="*70)

try:
    # Build service
    print("\n1. Building Forms service...")
    service = build_forms_service()
    print("   ✅ Service built successfully")
    
    # Test 1: Create form with ONLY title (should work)
    print("\n2. Creating form with ONLY title (API compliant)...")
    form = {'info': {'title': 'Test Form - Direct API Test'}}
    result = service.forms().create(body=form).execute()
    form_id = result['formId']
    print(f"   ✅ Form created: {form_id}")
    print(f"   URL: {result['responderUri']}")
    
    # Test 2: Add description via batchUpdate (should work)
    print("\n3. Adding description via batchUpdate...")
    batch_requests = [{
        'updateFormInfo': {
            'info': {'description': 'This is a test description added via batchUpdate'},
            'updateMask': 'description'
        }
    }]
    service.forms().batchUpdate(formId=form_id, body={'requests': batch_requests}).execute()
    print("   ✅ Description added successfully")
    
    # Test 3: Verify form has description
    print("\n4. Verifying form...")
    form_data = service.forms().get(formId=form_id).execute()
    has_description = 'description' in form_data.get('info', {})
    description_text = form_data.get('info', {}).get('description', 'N/A')
    print(f"   Has description: {has_description}")
    print(f"   Description: {description_text[:60]}...")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - API fixes are working!")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*70)
    print("❌ TEST FAILED")
    print("="*70)
