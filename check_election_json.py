"""Extract JSON specification for Election Signs"""
import json
from pathlib import Path

json_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'tools' / 'election_signs_shopify.json'

with open(json_path) as f:
    tool = json.load(f)

params = tool['parameters']['properties']

print("ELECTION SIGNS JSON SPECIFICATION")
print("=" * 80)

for param_name, param_info in params.items():
    if param_name == 'quantity':
        continue
    print(f"\n{param_name}:")
    if 'enum' in param_info:
        print(f"  Enum values ({len(param_info['enum'])}): {param_info['enum']}")
    if 'default' in param_info:
        print(f"  Default: {param_info['default']}")
    print(f"  Type: {param_info['type']}")
    print(f"  Description: {param_info.get('description', 'N/A')}")
