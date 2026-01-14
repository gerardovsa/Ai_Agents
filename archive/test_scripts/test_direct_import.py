"""Direct test of google_forms.py fixes"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'google_workspace'))

# Import function
from google_forms import google_forms_create_form

# Check source code
import inspect
source = inspect.getsource(google_forms_create_form)

print("="*70)
print("DIRECT IMPORT TEST - google_forms_create_form")
print("="*70)

# Check for fix markers
has_step1 = "STEP 1" in source
has_step2 = "STEP 2" in source
has_api_comment = "# Google Forms API only accepts" in source
has_title_only = "form_info = {\n            'title': title\n        }" in source
has_batchupdate = "batchUpdate" in source

print(f"\nFix Markers Found:")
print(f"  STEP 1 comment: {has_step1}")
print(f"  STEP 2 comment: {has_step2}")
print(f"  API restriction comment: {has_api_comment}")
print(f"  Title-only form_info: {has_title_only}")
print(f"  batchUpdate logic: {has_batchupdate}")

if all([has_step1, has_step2, has_api_comment, has_batchupdate]):
    print("\n✅ ALL FIXES PRESENT IN LOADED FUNCTION")
else:
    print("\n❌ FIXES MISSING - Function loaded from wrong source")
    print("\nFunction source (first 500 chars):")
    print(source[:500])

print("="*70)
