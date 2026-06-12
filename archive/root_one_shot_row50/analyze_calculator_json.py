import json

file_path = r"c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\schema\calculator_tools.json"

print("="*80)
print("CALCULATOR_TOOLS.JSON ANALYSIS")
print("="*80)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("✅ Valid JSON\n")
    
    # Basic stats
    total_tools = len(data.get("tools", []))
    print(f"📊 Total tools: {total_tools}")
    
    # Find GOD calculators
    god_tools = [t['name'] for t in data['tools'] if '_god' in t['name'].lower()]
    print(f"\n🔍 GOD calculators found: {len(god_tools)}")
    if god_tools:
        print("   ❌ GOD tools still present:")
        for tool in god_tools:
            print(f"      - {tool}")
    else:
        print("   ✅ No GOD calculators found")
    
    # Check for GOD in descriptions
    god_descriptions = []
    for tool in data['tools']:
        desc = tool.get('description', '') + tool.get('short_description', '')
        if 'GOD' in desc.upper():
            god_descriptions.append(tool['name'])
    
    if god_descriptions:
        print(f"\n⚠️  GOD mentioned in descriptions ({len(god_descriptions)} tools):")
        for tool in god_descriptions[:5]:
            print(f"      - {tool}")
    
    # List all tool names
    print(f"\n📋 All tool names:")
    for i, tool in enumerate(data['tools'], 1):
        print(f"   {i:2d}. {tool['name']}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    
except json.JSONDecodeError as e:
    print(f"❌ JSON DECODE ERROR: {e}")
    print(f"   Line: {e.lineno}, Column: {e.colno}")
    print(f"   Position: {e.pos}")
except Exception as e:
    print(f"❌ ERROR: {e}")
