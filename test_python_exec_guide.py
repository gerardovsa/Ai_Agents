"""Test python_exec_get_guide registration and execution."""
from tools.registry_v3 import RegistryV3
from tools.implementations.python_execution_guide_wrapper import python_exec_get_guide

print("Initializing registry...")
r = RegistryV3()

print(f"\nTool registered: {'python_exec_get_guide' in r.tools}")

if 'python_exec_get_guide' in r.tools:
    print("\nExecuting python_exec_get_guide...")
    result = python_exec_get_guide()
    
    print(f"Success: {result.get('success')}")
    print(f"Guide version: {result.get('guide_version')}")
    print(f"Last updated: {result.get('last_updated')}")
    print(f"Total tools: {result.get('overview', {}).get('total_tools')}")
    print(f"\nKey sections:")
    for key in result.keys():
        if key not in ['success', 'guide_version', 'last_updated']:
            print(f"  - {key}")
else:
    print("ERROR: Tool not registered!")
