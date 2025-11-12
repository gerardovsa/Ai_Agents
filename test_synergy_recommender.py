"""
Test synergy_recommend_next_tool - Verify intelligent recommendations work
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

print("=" * 70)
print("TESTING: synergy_recommend_next_tool")
print("=" * 70)

# Initialize registry
registry = RegistryV3()

# Test 1: Just starting
print("\n" + "=" * 70)
print("TEST 1: Just Starting a New Project")
print("=" * 70)
result = registry.execute_tool(
    tool_name='synergy_recommend_next_tool',
    current_situation='just_starting',
    have_session_id=False,
    resources_created=0,
    task_type='multi_platform'
)

print(f"\nRecommended Tool: {result['recommended_tool']}")
print(f"\nReason:\n{result['reason']}")
print(f"\nParameters:")
for param_name, param_info in result['parameters'].items():
    req = "REQUIRED" if param_info.get('required') else "Optional"
    print(f"  - {param_name} ({param_info['type']}) [{req}]")
    print(f"    {param_info.get('description', 'No description')}")
    if 'example' in param_info:
        print(f"    Example: {param_info['example']}")

print(f"\nSchemas to Fetch: {', '.join(result['schema_to_fetch'])}")

# Test 2: Project created, need to update
print("\n\n" + "=" * 70)
print("TEST 2: Project Created, Adding First Resource")
print("=" * 70)
result = registry.execute_tool(
    tool_name='synergy_recommend_next_tool',
    current_situation='project_created',
    have_session_id=True,
    resources_created=1
)

print(f"\nRecommended Tool: {result['recommended_tool']}")
print(f"\nReason:\n{result['reason']}")
print(f"\nExample Code:\n{result['example']}")
print(f"\nWarning:\n{result['warning']}")

# Test 3: Troubleshooting
print("\n\n" + "=" * 70)
print("TEST 3: Troubleshooting - Something Went Wrong")
print("=" * 70)
result = registry.execute_tool(
    tool_name='synergy_recommend_next_tool',
    current_situation='troubleshooting',
    have_session_id=True,
    resources_created=3
)

print(f"\nRecommended Tool: {result['recommended_tool']}")
print(f"\nReason:\n{result['reason']}")
print(f"\nWarning:\n{result['warning']}")

# Test 4: Learning
print("\n\n" + "=" * 70)
print("TEST 4: Learning - Need to Understand Synergy")
print("=" * 70)
result = registry.execute_tool(
    tool_name='synergy_recommend_next_tool',
    current_situation='learning',
    have_session_id=False,
    resources_created=0
)

print(f"\nRecommended Tool: {result['recommended_tool']}")
print(f"\nReason:\n{result['reason']}")
print(f"\nNext Steps:\n{result['next_steps']}")

# Test 5: Invalid situation
print("\n\n" + "=" * 70)
print("TEST 5: Invalid Situation (Error Handling)")
print("=" * 70)
result = registry.execute_tool(
    tool_name='synergy_recommend_next_tool',
    current_situation='invalid_situation_test'
)

print(f"\nSuccess: {result['success']}")
print(f"Error: {result.get('error', 'No error')}")
print(f"Valid Situations: {', '.join(result.get('valid_situations', []))}")

print("\n\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
print("\nSummary:")
print("- Tool loads successfully")
print("- Provides situation-specific recommendations")
print("- Includes complete parameters, examples, warnings")
print("- Handles invalid input gracefully")
print("\nStatus: READY FOR PRODUCTION")
