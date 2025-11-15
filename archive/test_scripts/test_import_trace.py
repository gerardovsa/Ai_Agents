"""Trace where google_forms_create_form is being loaded from"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'google_workspace'))

# Import function
from google_forms import google_forms_create_form

# Check WHERE it came from
import inspect

print("="*70)
print("IMPORT TRACE - google_forms_create_form")
print("="*70)

# Get module info
module = inspect.getmodule(google_forms_create_form)
print(f"\nModule: {module}")
print(f"Module file: {module.__file__ if hasattr(module, '__file__') else 'N/A'}")

# Get function info
print(f"\nFunction: {google_forms_create_form}")
print(f"Function name: {google_forms_create_form.__name__}")
print(f"Function module: {google_forms_create_form.__module__}")

# Check if it's wrapped
print(f"\nIs wrapped: {hasattr(google_forms_create_form, '__wrapped__')}")
if hasattr(google_forms_create_form, '__wrapped__'):
    print(f"Wrapped function: {google_forms_create_form.__wrapped__}")
    
# Check for closure
print(f"\nHas closure: {google_forms_create_form.__closure__ is not None}")
if google_forms_create_form.__closure__:
    print(f"Closure vars: {[cell.cell_contents for cell in google_forms_create_form.__closure__]}")

# Get signature
sig = inspect.signature(google_forms_create_form)
print(f"\nSignature: {sig}")
print(f"Parameters: {list(sig.parameters.keys())}")

# Check source file
try:
    source_file = inspect.getsourcefile(google_forms_create_form)
    print(f"\nSource file: {source_file}")
    
    # Read first 10 lines of actual source
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[68:78], 69):  # Lines around function definition
            print(f"Line {i}: {line.rstrip()}")
except Exception as e:
    print(f"\nCould not read source: {e}")

print("="*70)
