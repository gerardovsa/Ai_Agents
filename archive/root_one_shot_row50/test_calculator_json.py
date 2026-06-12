"""Test calculator_tools.json is valid"""
import json

print("Testing calculator_tools.json validity...")

try:
    with open('UI/modules_external/quote-calculator/schema/calculator_tools.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'tools' in data:
        tools = data['tools']
        print(f"\n✅ Valid JSON!")
        print(f"   Tools defined: {len(tools)}")
        print(f"   Platform: {data.get('platform', 'N/A')}")
        print(f"\n✅ No JSON syntax errors")
    else:
        print("❌ Invalid structure - not a dict with 'tools' array")
except json.JSONDecodeError as e:
    print(f"\n❌ JSON Error: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
