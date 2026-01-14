import json

try:
    with open('tools/schemas/synergy_tools.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tool_count = len(data['tools'])
    print(f"Valid JSON: {tool_count} tools")
    
    # List last 10 tool names
    print("\nLast 10 tools:")
    for tool in data['tools'][-10:]:
        print(f"  - {tool['name']}")
    
    print("\nValidation successful!")
    
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
except Exception as e:
    print(f"Error: {e}")
