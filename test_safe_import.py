"""Test RestrictedPython's safe import."""
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, safe_globals, guarded_iter_unpack_sequence
try:
    from RestrictedPython.Guards import safer_getattr
except ImportError:
    safer_getattr = getattr

print("=== Available in safe_builtins ===")
print(f"__import__ available: {'__import__' in safe_builtins}")
print(f"Keys: {sorted([k for k in safe_builtins.keys() if 'import' in k.lower()])}")

print("\n=== Available in safe_globals ===")
print(f"Keys: {sorted([k for k in safe_globals.keys()])}")

print("\n=== Test import ===")
code = "import pandas as pd"
try:
    byte_code = compile_restricted(code, '<string>', 'exec')
    
    test_globals = {
        '__builtins__': safe_builtins,
        '__name__': '__main__',
        '__metaclass__': type,
        '_getattr_': safer_getattr,
    }
    
    exec(byte_code, test_globals, {})
    print("SUCCESS: Import worked")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
