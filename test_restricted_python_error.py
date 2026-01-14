from RestrictedPython import compile_restricted, CompileResult

# Test with syntax error
bad_code = "x = 5 +"

result = compile_restricted(bad_code, filename='<test>', mode='exec')

print(f"Result type: {type(result)}")
print(f"Result: {result}")

if isinstance(result, CompileResult):
    print("It's a CompileResult!")
    print(f"Errors: {result.errors}")
    print(f"Code: {result.code}")
else:
    print("It's NOT a CompileResult")
    print(f"It's a: {type(result)}")
