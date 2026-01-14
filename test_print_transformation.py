"""See how RestrictedPython transforms print statements."""
from RestrictedPython import compile_restricted_exec
import dis

code = """
result = 5 + 10
print('Result:', result)
"""

print("=== Original Code ===")
print(code)

print("\n=== Compiled Bytecode ===")
byte_code = compile_restricted_exec(code)
if byte_code.errors:
    print(f"Errors: {byte_code.errors}")
else:
    print("Compilation successful")
    print("\n=== Disassembly ===")
    dis.dis(byte_code.code)
    
    print("\n=== Code Object Details ===")
    print(f"Names: {byte_code.code.co_names}")
    print(f"Varnames: {byte_code.code.co_varnames}")
