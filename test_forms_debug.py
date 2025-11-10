"""Debug Google Forms function to see what's actually executing"""

import sys
import importlib

# Force fresh import
for mod in list(sys.modules.keys()):
    if 'google_workspace' in mod or 'google' in mod:
        del sys.modules[mod]

# Import fresh
import google_workspace.google_forms as gf

# Patch the function to see what's being sent
original_get_forms_service = gf._get_forms_service

def debug_get_forms_service(**kwargs):
    print(f"\n[DEBUG] _get_forms_service called with kwargs: {list(kwargs.keys())}")
    return original_get_forms_service(**kwargs)

gf._get_forms_service = debug_get_forms_service

# Now test
print("Testing google_forms_create_form with description...")
print("="*60)

try:
    # Add detailed tracing
    import google_workspace.google_forms
    func_code = google_workspace.google_forms.google_forms_create_form
    
    print(f"\nFunction object: {func_code}")
    print(f"Function __code__.co_varnames: {func_code.__code__.co_varnames[:10]}")
    print(f"Function __defaults__: {func_code.__defaults__}")
    
    # Try to call it
    print("\n\nCalling function...")
    result = gf.google_forms_create_form(
        title="Debug Test Form",
        description="This is a test description",
        _user_id=1,
        _injected_credentials=True
    )
    
    print(f"\n✅ Function completed!")
    print(f"Result keys: {result.keys() if isinstance(result, dict) else type(result)}")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}")
    print(f"Message: {str(e)[:200]}")
    
    # Check if it's the HTTP 400 error
    if "Only info.title can be set" in str(e):
        print("\n⚠️  GOT THE OLD BUG - two-step process NOT being used!")
        print("This means the code being executed is NOT the fixed version.")
    elif "500" in str(e):
        print("\n✅ Two-step process IS working (different error)")
