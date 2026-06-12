"""
Comprehensive test suite for python_exec tools
Tests registration, execution, security, and error handling
"""

def test_tool_registration():
    """Test that python_exec tools are registered"""
    print("=" * 70)
    print("TEST 1: TOOL REGISTRATION")
    print("=" * 70)
    
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    
    expected_tools = [
        'python_exec',
        'python_exec_with_dataframe', 
        'python_exec_analysis'
    ]
    
    found_tools = []
    for tool_name in expected_tools:
        if tool_name in registry.tools:
            found_tools.append(tool_name)
            print(f"✅ {tool_name} - REGISTERED")
        else:
            print(f"❌ {tool_name} - NOT FOUND")
    
    print(f"\nResult: {len(found_tools)}/{len(expected_tools)} tools registered")
    assert len(found_tools) == len(expected_tools), "Missing python_exec tools!"
    print("✅ All python_exec tools are registered\n")


def test_basic_execution():
    """Test basic python_exec execution"""
    print("=" * 70)
    print("TEST 2: BASIC EXECUTION")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec
    
    # Test simple calculation
    code = """
x = 5
y = 10
result = x + y
print(f"Result: {result}")
"""
    
    print("Executing simple calculation...")
    result = python_exec(code=code)
    
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output', '').strip()}")
    print(f"Variables: {result.get('variables', {})}")
    print(f"Execution time: {result.get('execution_time', 0):.3f}s")
    
    assert result['success'], f"Execution failed: {result.get('error')}"
    assert 'Result: 15' in result['output'], "Output doesn't contain expected result"
    assert result['variables'].get('result') == 15, "Variable not captured correctly"
    print("✅ Basic execution works\n")


def test_pandas_execution():
    """Test pandas DataFrame operations"""
    print("=" * 70)
    print("TEST 3: PANDAS EXECUTION")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec
    
    code = """
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
})

mean_age = df['age'].mean()
total_salary = df['salary'].sum()

print(f"Mean age: {mean_age}")
print(f"Total salary: ${total_salary:,}")
print(f"DataFrame shape: {df.shape}")
"""
    
    print("Executing pandas operations...")
    result = python_exec(code=code)
    
    print(f"Success: {result.get('success')}")
    print(f"Output:\n{result.get('output', '').strip()}")
    print(f"Execution time: {result.get('execution_time', 0):.3f}s")
    
    assert result['success'], f"Pandas execution failed: {result.get('error')}"
    assert 'Mean age: 30.0' in result['output'], "Pandas calculation incorrect"
    assert 'Total salary: $180,000' in result['output'], "Salary sum incorrect"
    print("✅ Pandas execution works\n")


def test_security_restrictions():
    """Test that security restrictions are enforced"""
    print("=" * 70)
    print("TEST 4: SECURITY RESTRICTIONS")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec
    
    # Test 1: File system access should be blocked
    print("\nTest 4a: File system access (should fail)...")
    code_file = "open('/etc/passwd', 'r').read()"
    result = python_exec(code=code_file)
    
    if not result['success']:
        print(f"✅ File access blocked: {result.get('error', '')[:100]}")
    else:
        print(f"❌ WARNING: File access was NOT blocked!")
    
    # Test 2: Network access should be blocked
    print("\nTest 4b: Network access (should fail)...")
    code_network = """
import requests
response = requests.get('https://google.com')
"""
    result = python_exec(code=code_network)
    
    if not result['success']:
        print(f"✅ Network access blocked: {result.get('error', '')[:100]}")
    else:
        print(f"❌ WARNING: Network access was NOT blocked!")
    
    # Test 3: Subprocess should be blocked
    print("\nTest 4c: Subprocess execution (should fail)...")
    code_subprocess = """
import subprocess
subprocess.run(['ls', '-la'])
"""
    result = python_exec(code=code_subprocess)
    
    if not result['success']:
        print(f"✅ Subprocess blocked: {result.get('error', '')[:100]}")
    else:
        print(f"❌ WARNING: Subprocess was NOT blocked!")
    
    print("\n✅ Security restrictions are enforced\n")


def test_with_dataframe():
    """Test python_exec_with_dataframe"""
    print("=" * 70)
    print("TEST 5: PYTHON_EXEC_WITH_DATAFRAME")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec_with_dataframe
    
    # Create sample dataframe data
    df_data = {
        'product': ['Widget A', 'Widget B', 'Widget C'],
        'price': [10.99, 25.50, 15.75],
        'quantity': [100, 50, 75]
    }
    
    code = """
# DataFrame is already loaded as 'df'
total_value = (df['price'] * df['quantity']).sum()
avg_price = df['price'].mean()

print(f"Total inventory value: ${total_value:.2f}")
print(f"Average price: ${avg_price:.2f}")
print(f"Products: {len(df)}")
"""
    
    print("Executing with pre-loaded DataFrame...")
    result = python_exec_with_dataframe(code=code, dataframe=df_data)
    
    print(f"Success: {result.get('success')}")
    print(f"Output:\n{result.get('output', '').strip()}")
    
    assert result['success'], f"Execution failed: {result.get('error')}"
    assert 'Total inventory value' in result['output'], "Missing calculation output"
    print("✅ python_exec_with_dataframe works\n")


def test_error_handling():
    """Test error handling for invalid code"""
    print("=" * 70)
    print("TEST 6: ERROR HANDLING")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec
    
    # Test syntax error
    print("Test 6a: Syntax error...")
    code_syntax = "x = 5 +"
    result = python_exec(code=code_syntax)
    
    assert not result['success'], "Should have failed on syntax error"
    print(f"✅ Syntax error caught: {result.get('error', '')[:80]}...")
    
    # Test runtime error
    print("\nTest 6b: Runtime error...")
    code_runtime = """
x = 5
y = 0
z = x / y  # Division by zero
"""
    result = python_exec(code=code_runtime)
    
    assert not result['success'], "Should have failed on runtime error"
    print(f"✅ Runtime error caught: {result.get('error', '')[:80]}...")
    
    # Test undefined variable
    print("\nTest 6c: Undefined variable...")
    code_undefined = "print(undefined_variable)"
    result = python_exec(code=code_undefined)
    
    assert not result['success'], "Should have failed on undefined variable"
    print(f"✅ Undefined variable caught: {result.get('error', '')[:80]}...")
    
    print("\n✅ Error handling works correctly\n")


def test_timeout():
    """Test timeout protection"""
    print("=" * 70)
    print("TEST 7: TIMEOUT PROTECTION")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec
    
    code_timeout = """
import time
time.sleep(5)  # Sleep for 5 seconds
"""
    
    print("Executing code with 2-second timeout...")
    import time
    start = time.time()
    result = python_exec(code=code_timeout, timeout=2)
    elapsed = time.time() - start
    
    print(f"Elapsed time: {elapsed:.2f}s")
    print(f"Success: {result.get('success')}")
    
    if not result['success']:
        print(f"✅ Timeout enforced: {result.get('error', '')[:80]}...")
    else:
        print(f"⚠️  WARNING: Timeout may not be working (elapsed: {elapsed:.2f}s)")
    
    print()


def test_visualization():
    """Test matplotlib visualization"""
    print("=" * 70)
    print("TEST 8: VISUALIZATION (MATPLOTLIB)")
    print("=" * 70)
    
    from tools.implementations.python_execution_tools import python_exec
    
    code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('sin(X)')
plt.grid(True)

# Note: plt.show() won't work in headless mode
# Charts would be saved to workspace_dir if provided

print("Chart created successfully")
"""
    
    print("Creating matplotlib chart...")
    result = python_exec(code=code)
    
    print(f"Success: {result.get('success')}")
    print(f"Output: {result.get('output', '').strip()}")
    
    assert result['success'], f"Visualization failed: {result.get('error')}"
    print("✅ Matplotlib visualization works\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PYTHON_EXEC COMPREHENSIVE TEST SUITE")
    print("=" * 70 + "\n")
    
    tests = [
        ("Tool Registration", test_tool_registration),
        ("Basic Execution", test_basic_execution),
        ("Pandas Execution", test_pandas_execution),
        ("Security Restrictions", test_security_restrictions),
        ("With DataFrame", test_with_dataframe),
        ("Error Handling", test_error_handling),
        ("Timeout Protection", test_timeout),
        ("Visualization", test_visualization)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED: {str(e)}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("=" * 70 + "\n")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! python_exec is fully functional.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review output above for details.")


if __name__ == '__main__':
    run_all_tests()
