from tools.registry_v3 import RegistryV3
import json

registry = RegistryV3()
tools = registry.get_anthropic_tools()

print(f"Total tools: {len(tools)}")
print(f"\nTool 653: {tools[653]['name']}")
print(f"\nFull schema:")
print(json.dumps(tools[653], indent=2))
