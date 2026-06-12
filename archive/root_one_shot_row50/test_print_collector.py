from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
from RestrictedPython.PrintCollector import PrintCollector

code = "print('Hello', 'World')"

byte_code = compile_restricted(code, filename='<test>', mode='exec')

# Try different ways to use PrintCollector
_print = PrintCollector()

safe_globals = {
    '__builtins__': safe_builtins,
    '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
    '_print_': _print,
    '_getattr_': getattr,
}

safe_locals = {}

print("Executing code...")
try:
    exec(byte_code, safe_globals, safe_locals)
    print(f"PrintCollector txt: {_print.txt if hasattr(_print, 'txt') else 'no txt'}")
    print(f"PrintCollector result: {_print()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
