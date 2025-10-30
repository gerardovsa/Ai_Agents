"""Test multi-directory tool loading"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from tools.registry import ToolRegistry

print("="*80)
print("TESTING MULTI-DIRECTORY TOOL REGISTRY")
print("="*80)

registry = ToolRegistry()

print(f"\n RESULTS:")
print(f"   Schemas loaded: {len(registry.tools)}")
print(f"   Implementations loaded: {len(registry.implementations)}")
print(f"   Platforms: {len(registry.get_all_platforms())}")

print(f"\n LOADED IMPLEMENTATIONS:")
for name in sorted(registry.implementations.keys())[:20]:
    print(f"   ✅ {name}")
if len(registry.implementations) > 20:
    print(f"   ... and {len(registry.implementations) - 20} more")

print(f"\n PLATFORMS DETECTED:")
for platform in sorted(registry.get_all_platforms()):
    tools = registry.get_platform_tools(platform)
    print(f"   {platform}: {len(tools)} tools")

print(f"\n TEST EXECUTION:")
# Test a Google tool
if 'ai_check_pending_work' in registry.tools:
    result = registry.execute_tool('ai_check_pending_work', user_id=1)
    print(f"   ai_check_pending_work: {'✅' if result.get('success') else '❌'}")

# Test a Microsoft tool
if 'microsoft_outlook_send_email' in registry.tools:
    result = registry.execute_tool('microsoft_outlook_send_email', 
                                   user_id=1, 
                                   to="test@example.com",
                                   subject="Test",
                                   body="Test")
    print(f"   microsoft_outlook_send_email: {'✅' if result.get('success') else '❌'}")

print("\n" + "="*80)