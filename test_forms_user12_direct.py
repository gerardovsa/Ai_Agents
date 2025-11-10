"""Direct test of Google Forms with user 12 (no registry)"""

import sys
sys.path.insert(0, 'google_workspace')

import google_forms as gf

print("="*80)
print("DIRECT GOOGLE FORMS TEST - USER 12")
print("="*80)

print("\nTest 1: Simple form with description")
print("-"*80)

try:
    result = gf.google_forms_create_form(
        title="Direct Test Form from User 12",
        description="This form tests the two-step creation process",
        document_title="Test Document Title",
        shareable=True,
        _user_id=12,
        _injected_credentials=True
    )
    
    print(f"✅ SUCCESS!")
    print(f"   Form ID: {result.get('form_id')}")
    print(f"   Responder URI: {result.get('responder_uri')}")
    print(f"   Edit URI: {result.get('edit_uri')}")
    print(f"   Shareable: {result.get('shareable')}")
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ FAILED: {type(e).__name__}")
    print(f"   Error: {error_msg[:150]}")
    
    if "Only info.title can be set" in error_msg:
        print("\n⚠️  OLD BUG - Two-step process NOT working")
    elif "500" in error_msg or "Internal error" in error_msg:
        print("\n⚠️  HTTP 500 - Service account doesn't work with Forms API")
        print("   Need OAuth credentials")
    elif "403" in error_msg or "permission" in error_msg.lower():
        print("\n⚠️  HTTP 403 - Permission denied")
    else:
        print("\n✅ Two-step process working (got past HTTP 400)")

print("\n" + "="*80)
