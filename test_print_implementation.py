"""Test different print guard implementations for RestrictedPython."""
from RestrictedPython import compile_restricted
import sys
from io import StringIO

# Test 1: Simple function
print("=== Test 1: Simple function ===")
code1 = """
result = 5 + 10
print('Result:', result)
"""

print_output = []

class PrintCollector:
    """Custom print collector that implements _call_print."""
    def __init__(self):
        self.output = []
    
    def _call_print(self, *args, **kwargs):
        """Method called by RestrictedPython for print statements."""
        text = ' '.join(str(arg) for arg in args)
        self.output.append(text)
        print(text)
        return text
    
    def __call__(self, *args, **kwargs):
        """Allow direct calls."""
        return self._call_print(*args, **kwargs)

try:
    byte_code = compile_restricted(code1, '<string>', 'exec')
    
    _print = PrintCollector()
    safe_globals = {
        '__builtins__': {
            '_print_': _print,
            '_getattr_': getattr,
        }
    }
    
    safe_locals = {}
    
    stdout_capture = StringIO()
    sys.stdout = stdout_capture
    
    exec(byte_code, safe_globals, safe_locals)
    
    sys.stdout = sys.__stdout__
    
    print(f"Success!")
    print(f"Output: {_print.output}")
    print(f"Stdout: {stdout_capture.getvalue()}")
    
except Exception as e:
    sys.stdout = sys.__stdout__
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
