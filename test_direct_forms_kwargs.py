"""Direct test of google_forms_create_form with **kwargs"""

import sys
import importlib

# Force fresh import
if 'google_workspace.google_forms' in sys.modules:
    del sys.modules['google_workspace.google_forms']
if 'google_workspace' in sys.modules:
    del sys.modules['google_workspace']

# Import fresh
import google_workspace.google_forms as gf
import inspect

# Check signature
sig = inspect.signature(gf.google_forms_create_form)
print(f"Function signature: {sig}")
print(f"Has **kwargs: {'**kwargs' in str(sig)}")
print(f"Parameters: {list(sig.parameters.keys())}")

# Check source
source_lines = inspect.getsourcelines(gf.google_forms_create_form)[0][:5]
print("\nFirst 5 lines of source:")
for line in source_lines:
    print(f"  {line.rstrip()}")

# Try calling with kwargs
print("\n\nAttempting to call with kwargs:")
try:
    result = gf.google_forms_create_form(
        title="Test",
        description="Test desc",
        _user_id=1,
        _injected_credentials=True
    )
    print(f"✅ SUCCESS - No parameter error!")
    print(f"Result type: {type(result)}")
except TypeError as e:
    if "_user_id" in str(e):
        print(f"❌ FAIL - Still rejecting _user_id: {e}")
    else:
        print(f"⚠️  Different error: {e}")
except Exception as e:
    print(f"✅ Got past parameter check, hit runtime error: {type(e).__name__}")
    print(f"  Error: {str(e)[:100]}")
