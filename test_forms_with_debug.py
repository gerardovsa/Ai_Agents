"""Test with debug logging to see what parameters are being passed"""

import sys
sys.path.insert(0, 'google_workspace')

import google_forms as gf

# Monkey-patch _get_forms_service to add logging
original_get_forms_service = gf._get_forms_service

def debug_get_forms_service(_user_id=None, _injected_credentials=None, **kwargs):
    print(f"\n[DEBUG] _get_forms_service called:")
    print(f"  _user_id: {_user_id} (type: {type(_user_id)})")
    print(f"  _injected_credentials: {_injected_credentials} (type: {type(_injected_credentials)})")
    print(f"  Other kwargs: {list(kwargs.keys())}")
    print(f"  Condition check: _user_id={bool(_user_id)}, _injected_credentials={bool(_injected_credentials)}")
    print(f"  Will use OAuth: {bool(_user_id and _injected_credentials)}")
    return original_get_forms_service(_user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs)

gf._get_forms_service = debug_get_forms_service

print("="*80)
print("DEBUGGING CREDENTIAL INJECTION")
print("="*80)

print("\nCalling google_forms_create_form with user 12 credentials...")
try:
    result = gf.google_forms_create_form(
        title="Debug Test",
        description="Test description",
        _user_id=12,
        _injected_credentials=True
    )
    print(f"\n✅ SUCCESS: {result}")
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)[:150]}")
