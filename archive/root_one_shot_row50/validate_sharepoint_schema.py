import json

try:
    with open('tools/schemas/microsoft_sharepoint_tools.json', 'r', encoding='utf-8') as f:
        schema = json.load(f)
    print(f"✅ Valid JSON")
    print(f"📊 Tools: {len(schema.get('tools', []))}")
    print(f"📦 Platform: {schema.get('platform', 'N/A')}")
except json.JSONDecodeError as e:
    print(f"❌ JSON Error: {e}")
    print(f"   Line {e.lineno}, Column {e.colno}")
    print(f"   Position {e.pos}")
