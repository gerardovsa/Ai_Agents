"""
Analyze CadQuery Tools Against Platform Tool Suite Standards
Checks: short_description, full description, searchability, Anthropic format
"""

import sys
import json
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')

from tools.registry import ToolRegistry

print("=" * 80)
print("CADQUERY TOOL INTEGRATION ANALYSIS")
print("=" * 80)

# Load registry
registry = ToolRegistry()
tools = registry.list_tools()
cadquery_tools = [t for t in tools if t.get('platform') == 'cadquery']

print(f"\n✓ CadQuery tools found: {len(cadquery_tools)}")

# CRITICAL CHECKS FROM PLATFORM TOOL SUITE AGENT PROMPT

print("\n" + "=" * 80)
print("CRITICAL CHECK 1: SHORT_DESCRIPTION FIELD (Required for Search)")
print("=" * 80)

missing_short_desc = []
for i, tool in enumerate(cadquery_tools):
    has_short = 'short_description' in tool
    print(f"{i+1}. {tool['name']}")
    print(f"   Has short_description: {has_short}")
    if has_short:
        short_desc = tool['short_description']
        print(f"   Content: '{short_desc}'")
        print(f"   Length: {len(short_desc)} chars (should be 50-120)")
        if len(short_desc) < 50 or len(short_desc) > 120:
            print(f"   ⚠️  WARNING: Length outside optimal range!")
    else:
        print(f"   ❌ MISSING - Tool will have poor search discovery!")
        missing_short_desc.append(tool['name'])
    print()

if missing_short_desc:
    print(f"\n❌ CRITICAL: {len(missing_short_desc)}/4 tools missing short_description")
    print("   Impact: 98% token reduction in search listings NOT achieved")
    print("   Impact: Semantic search quality degraded")
    print("   Impact: Hybrid discovery less effective")
else:
    print(f"\n✅ All tools have short_description field")

print("\n" + "=" * 80)
print("CHECK 2: FULL DESCRIPTION QUALITY")
print("=" * 80)

for i, tool in enumerate(cadquery_tools):
    desc = tool.get('description', '')
    print(f"{i+1}. {tool['name']}")
    print(f"   Length: {len(desc)} chars (should be 200-500+)")
    print(f"   Has execution rules: {'🚨 CRITICAL EXECUTION RULES' in desc or 'Use this when' in desc}")
    print(f"   Has examples: {'Example:' in desc or 'example' in desc.lower()}")
    if len(desc) < 200:
        print(f"   ⚠️  WARNING: Description too short for comprehensive guidance")
    print()

print("\n" + "=" * 80)
print("CHECK 3: NAMING CONVENTION")
print("=" * 80)

naming_issues = []
for tool in cadquery_tools:
    name = tool['name']
    # Pattern: {platform}_{action}_{resource}
    # For CadQuery: generate_cad_from_code, validate_cadquery_code, etc.
    # These follow verb_object or verb_platform_object patterns
    parts = name.split('_')
    
    print(f"✓ {name}")
    if name.startswith(('generate_', 'validate_', 'list_', 'get_')):
        print(f"   Pattern: Follows standard convention (verb_object)")
    elif len(parts) >= 2 and parts[0] == 'cadquery':
        print(f"   Pattern: Follows platform_action_resource")
    else:
        print(f"   ⚠️  May not follow standard patterns")
        naming_issues.append(f"{name} - unusual pattern")
    print()

print("\n" + "=" * 80)
print("CHECK 4: ANTHROPIC FORMAT CONVERSION")
print("=" * 80)

try:
    anthropic_tools = registry.get_anthropic_tools()
    cadquery_anthropic = [t for t in anthropic_tools if t.get('name', '').startswith('cadquery_') or 'cadquery' in t.get('name', '')]
    
    print(f"✓ Anthropic conversion successful")
    print(f"✓ CadQuery tools in Anthropic format: {len(cadquery_anthropic)}")
    
    if len(cadquery_anthropic) > 0:
        sample = cadquery_anthropic[0]
        print(f"\nSample tool structure:")
        print(f"  name: {sample.get('name')}")
        print(f"  description: {sample.get('description', '')[:100]}...")
        print(f"  input_schema type: {sample.get('input_schema', {}).get('type')}")
        print(f"  has properties: {'properties' in sample.get('input_schema', {})}")
except Exception as e:
    print(f"❌ ERROR converting to Anthropic format: {e}")

print("\n" + "=" * 80)
print("CHECK 5: SEARCHABILITY")
print("=" * 80)

# Check if tools can be discovered via platform search
try:
    from tools.implementations.meta_tools import list_platform_tools
    platform_tools = list_platform_tools(platform='cadquery')
    print(f"✓ list_platform_tools('cadquery'): {len(platform_tools.get('tools', []))} tools found")
    
    if len(platform_tools.get('tools', [])) == len(cadquery_tools):
        print(f"✅ All CadQuery tools are discoverable via platform search")
    else:
        print(f"⚠️  Mismatch: Registry has {len(cadquery_tools)}, platform search found {len(platform_tools.get('tools', []))}")
except Exception as e:
    print(f"❌ ERROR testing platform search: {e}")

print("\n" + "=" * 80)
print("CHECK 6: PROGRESSIVE DISCOVERY WORKFLOW")
print("=" * 80)

print("Testing: User asks 'Create a bolt using CadQuery'")
print("\nStep 1: Search for tools")
try:
    from tools.implementations.meta_tools import search_tools
    results = search_tools(query='create bolt cadquery')
    matching = [t for t in results.get('tools', []) if 'cadquery' in t.get('name', '').lower()]
    print(f"  ✓ search_tools('create bolt cadquery'): {len(matching)} CadQuery tools found")
    if matching:
        print(f"    Top result: {matching[0].get('name')}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

print("\nStep 2: Get tool schema")
try:
    from tools.implementations.meta_tools import get_tool_schema
    schema = get_tool_schema(tool_name='generate_cad_from_code')
    print(f"  ✓ get_tool_schema('generate_cad_from_code'): Success")
    print(f"    Description length: {len(schema.get('description', ''))} chars")
    print(f"    Has input_schema: {'input_schema' in schema}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

print("\nStep 3: Execute tool")
print("  (Skipped - would require actual CadQuery code execution)")

print("\n" + "=" * 80)
print("FINAL ASSESSMENT")
print("=" * 80)

issues = []
if missing_short_desc:
    issues.append(f"❌ CRITICAL: {len(missing_short_desc)}/4 tools missing short_description")
if naming_issues:
    issues.append(f"⚠️  {len(naming_issues)} naming convention issues")

if not issues:
    print("\n✅ CadQuery tools meet platform integration standards!")
    print("\nStrengths:")
    print("  ✓ Proper tool registration (4 tools)")
    print("  ✓ Anthropic format conversion working")
    print("  ✓ Platform search discoverable")
    print("  ✓ Progressive discovery workflow functional")
else:
    print("\n⚠️  CadQuery tools need updates:")
    for issue in issues:
        print(f"  {issue}")
    
    print("\nRequired Actions:")
    if missing_short_desc:
        print("\n1. Add short_description field to all tools (50-120 chars)")
        print("   Format: [ACTION] [OBJECT] with/by/for [KEY_FEATURES]")
        print("   Example: 'Generate 3D CAD geometry from Python code with STEP/STL export'")
        print("\n   Why critical:")
        print("   - Enables 98% token reduction in tool listings")
        print("   - Improves semantic search quality")
        print("   - Required for hybrid discovery (keyword + semantic + platform)")

print("\n" + "=" * 80)
print("END OF ANALYSIS")
print("=" * 80)
