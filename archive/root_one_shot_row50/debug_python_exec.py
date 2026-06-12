import traceback
from tools.implementations.python_execution_tools import python_exec

print("Testing python_exec with detailed error tracking...")

code = """
x = 5
y = 10
result = x + y
print(f'Result: {result}')
"""

try:
    result = python_exec(code=code)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Output: '{result.get('output', '')}'")
    print(f"Error: {result.get('error', 'None')}")
    
    if 'traceback' in result:
        print(f"\nFull traceback:")
        print(result['traceback'])
        
except Exception as e:
    print(f"Exception during test: {e}")
    traceback.print_exc()
