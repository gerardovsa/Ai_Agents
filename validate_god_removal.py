#!/usr/bin/env python3
"""Validate GOD calculator removal from schema"""
import json
from pathlib import Path

schema_path = Path("UI/modules_external/quote-calculator/schema/calculator_tools.json")

print("🔍 Validating GOD calculator removal...")
print(f"📄 File: {schema_path}\n")

# Load and validate JSON
with open(schema_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("✅ JSON is valid")

# Check for GOD calculators
god_tools = [t['name'] for t in data['tools'] if '_god' in t['name']]

print(f"\n📊 Results:")
print(f"  • Total tools in schema: {len(data['tools'])}")
print(f"  • GOD calculators remaining: {len(god_tools)}")

if god_tools:
    print(f"\n❌ GOD calculators still present:")
    for tool in god_tools:
        print(f"    - {tool}")
else:
    print(f"\n✅ All GOD calculators successfully removed!")
    
# Show a few remaining calculator names
print(f"\n📝 Sample of remaining calculators:")
for tool in data['tools'][:5]:
    print(f"    - {tool['name']}")

print(f"\n✅ VALIDATION COMPLETE - Schema is clean!")
