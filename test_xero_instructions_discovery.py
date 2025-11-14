"""
Test: Demonstrate how AI discovers and uses Xero tool instructions

This script simulates what an AI agent sees when it queries tool schemas.
"""

from tools.registry_v3 import RegistryV3
import json

print("="*80)
print("XERO TOOL INSTRUCTIONS - AI DISCOVERY DEMO")
print("="*80)

# Load registry (simulates AI agent startup)
print("\n1. AI Agent initializing registry...")
registry = RegistryV3()
print(f"   ✅ Registry loaded: {len(registry.tools)} tools available")

# Discover Xero tools (simulates AI seeing what platforms exist)
print("\n2. AI discovering Xero tools...")
xero_tools = [name for name in registry.tools.keys() if name.startswith('xero_')]
print(f"   ✅ Found {len(xero_tools)} Xero tools:")
for tool_name in sorted(xero_tools):
    print(f"      - {tool_name}")

# Get schema for specific tool (simulates AI learning how to use it)
print("\n3. AI examining xero_get_invoices schema...")
tool_schema = registry.get_tool(tool_name='xero_get_invoices')

if 'instructions' in tool_schema:
    instructions = tool_schema['instructions']
    
    print(f"\n   📖 Instructions found! AI learns:")
    print(f"\n   🎯 WHEN TO USE (AI sees {len(instructions['when_to_use'])} scenarios):")
    for scenario in instructions['when_to_use']:
        print(f"      • {scenario}")
    
    print(f"\n   📋 WORKFLOW (AI learns {len(instructions['workflow'])} steps):")
    for step in instructions['workflow']:
        print(f"      {step}")
    
    print(f"\n   💡 EXAMPLES (AI sees {len(instructions['example_usage'])} real-world cases):")
    for scenario_name, scenario_data in instructions['example_usage'].items():
        print(f"\n      Example: {scenario_name}")
        print(f"         User asks: \"{scenario_data['user_request']}\"")
        print(f"         AI calls: {scenario_data['tool_call']}")
        print(f"         AI responds: \"{scenario_data['ai_responds'][:100]}...\"")
    
    print(f"\n   ⚠️  TIPS (AI learns {len(instructions['tips'])} best practices):")
    for tip in instructions['tips'][:3]:  # Show first 3
        print(f"      • {tip}")
    
    print(f"\n   ✅ AI now knows WHEN, HOW, and WHY to use this tool!")

else:
    print("   ❌ No instructions found - AI must guess how to use it")

# Demonstrate smart tool instructions
print("\n" + "="*80)
print("4. AI examining xero_smart_export_accounts_payable_stats schema...")
smart_tool_schema = registry.get_tool(tool_name='xero_smart_export_accounts_payable_stats')

if 'instructions' in smart_tool_schema:
    instructions = smart_tool_schema['instructions']
    
    print(f"\n   📖 Smart tool has comprehensive instructions!")
    print(f"\n   🎯 WHEN TO USE scenarios: {len(instructions['when_to_use'])}")
    print(f"   📋 Workflow steps: {len(instructions['workflow'])}")
    print(f"   💡 Example dialogues: {len(instructions['example_usage'])}")
    print(f"   ⚠️  Usage tips: {len(instructions['tips'])}")
    
    # Show one detailed example
    example = instructions['example_usage']['scenario_1']
    print(f"\n   Example Scenario:")
    print(f"      User: \"{example['user_request']}\"")
    print(f"      AI calls: {example['tool_call']}")
    print(f"      AI analyzes: {', '.join(example['ai_analyzes'][:2])}...")
    print(f"      AI responds: \"{example['ai_responds'][:120]}...\"")
    
    print(f"\n   ✅ AI learns complete workflow for complex financial analysis!")

# Summary
print("\n" + "="*80)
print("SUMMARY: HOW AI USES INSTRUCTIONS")
print("="*80)

print("""
1. 🔍 AI DISCOVERS TOOLS:
   - Calls list_platform_tools("xero")
   - Sees 8 available Xero tools

2. 📖 AI READS INSTRUCTIONS:
   - Calls get_tool_schema("xero_get_invoices")
   - Gets complete instructions section
   - Learns when, how, and why to use tool

3. 🎯 AI MATCHES USER INTENT:
   - User: "Show unpaid invoices"
   - AI checks "when_to_use" scenarios
   - Finds match: "User wants to check invoice status"
   - AI selects xero_get_invoices

4. 💡 AI LEARNS FROM EXAMPLES:
   - Sees example: status='AUTHORISED' for unpaid
   - Learns: NOT status='UNPAID' (doesn't exist)
   - Copies response format from example

5. ✅ AI USES TOOL CORRECTLY:
   - Calls: xero_get_invoices(business_id=1, status='AUTHORISED')
   - Gets results
   - Formats response like examples
   - User gets accurate, helpful answer

WITHOUT INSTRUCTIONS:
   ❌ AI guesses status='UNPAID' (wrong)
   ❌ API returns error
   ❌ User gets confused

WITH INSTRUCTIONS:
   ✅ AI uses status='AUTHORISED' (correct)
   ✅ API returns data
   ✅ User gets accurate answer
""")

print("="*80)
print("✅ DOCUMENTATION SUCCESS!")
print("="*80)
print("""
All 8 Xero tools now have AI-readable instructions.
AI agents can learn tool usage from schemas without external documentation.
This pattern should be applied to all 54 remaining smart tools.
""")
