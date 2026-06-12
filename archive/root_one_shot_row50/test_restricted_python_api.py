from RestrictedPython import compile_restricted

# Test what compile_restricted actually returns
code = "x = 5\nprint(x)"

result = compile_restricted(code, filename='<test>', mode='exec')

print(f"Result type: {type(result)}")
print(f"Result: {result}")
print(f"Dir: {[x for x in dir(result) if not x.startswith('_')]}")

if hasattr(result, 'errors'):
    print(f"Has errors attribute: {result.errors}")
if hasattr(result, 'code'):
    print(f"Has code attribute: {type(result.code)}")
