"""Get actual tool names from schemas"""
import json
from pathlib import Path

schemas_dir = Path('tools/schemas')
test_cases = []

# Microsoft tools
for schema_file in sorted(schemas_dir.glob('microsoft_*.json')):
    with open(schema_file, encoding='utf-8') as f:
        data = json.load(f)
        platform = data.get('platform')
        tools = [t['name'] for t in data.get('tools', [])[:1]]  # First tool only
        for tool_name in tools:
            test_cases.append({
                "name": tool_name,
                "platform": platform
            })

# Google tools  
for schema_file in sorted(schemas_dir.glob('google_*.json')):
    with open(schema_file, encoding='utf-8') as f:
        data = json.load(f)
        platform = data.get('platform')
        tools = [t['name'] for t in data.get('tools', [])[:1]]  # First tool only
        for tool_name in tools:
            test_cases.append({
                "name": tool_name,
                "platform": platform
            })

# Gmail
for schema_file in sorted(schemas_dir.glob('gmail*.json')):
    with open(schema_file, encoding='utf-8') as f:
        data = json.load(f)
        platform = data.get('platform')
        tools = [t['name'] for t in data.get('tools', [])[:1]]  # First tool only
        for tool_name in tools:
            test_cases.append({
                "name": tool_name,
                "platform": platform
            })

print("ACTUAL TOOL NAMES FROM SCHEMAS:")
print("=" * 80)
for test in test_cases:
    platform = test.get('platform') or 'unknown'
    print(f"{platform:30s} → {test['name']}")
