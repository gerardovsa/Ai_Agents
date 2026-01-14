from tools.implementations.python_execution_tools import python_exec

print("Testing python_exec fix...")

code = """
x = 5
y = 10
result = x + y
print(f'Result: {result}')
"""

result = python_exec(code=code)

print(f"Success: {result['success']}")
print(f"Output: {result.get('output', '')}")
print(f"Error: {result.get('error', 'None')}")
print(f"Variables: {result.get('variables', {})}")
