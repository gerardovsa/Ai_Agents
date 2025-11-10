"""Simplest possible test - directly read and exec the function"""

# Read the function source directly from file
with open('google_workspace/google_forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function definition line
import re
match = re.search(r'^def google_forms_create_form\([^)]+\):', content, re.MULTILINE)
if match:
    func_def = match.group(0)
    print(f"Function definition in file:")
    print(f"  {func_def}")
    print(f"\nHas **kwargs: {'**kwargs' in func_def}")
else:
    print("Function not found!")

# Now actually import it
print("\n" + "="*60)
print("Now importing module...")

import sys
# Clear any cached imports
for mod in list(sys.modules.keys()):
    if 'google_workspace.google_forms' in mod:
        del sys.modules[mod]

import google_workspace.google_forms as gf
import inspect

sig = inspect.signature(gf.google_forms_create_form)
print(f"Function signature after import: {sig}")
print(f"Has **kwargs in signature: {'**kwargs' in str(sig)}")

# Check the actual parameters
params = sig.parameters
print(f"\nParameters:")
for name, param in params.items():
    print(f"  {name}: {param.kind.name}")
    if param.kind == inspect.Parameter.VAR_KEYWORD:
        print(f"    ✅ This is **kwargs!")
