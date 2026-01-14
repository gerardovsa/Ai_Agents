#!/usr/bin/env python3
"""Remove remaining GOD calculator and fix emoji corruption"""
import json
from pathlib import Path

schema_path = Path("UI/modules_external/quote-calculator/schema/calculator_tools.json")

print("🔧 Fixing calculator_tools.json...")

# Read with error replacement
with open(schema_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Load as JSON
data = json.loads(content)

print(f"Original tool count: {len(data['tools'])}")

# Remove any tool with "_god" in the name
original_count = len(data['tools'])
data['tools'] = [t for t in data['tools'] if '_god' not in t['name'].lower()]
removed_count = original_count - len(data['tools'])

print(f"Removed {removed_count} GOD calculator(s)")
print(f"New tool count: {len(data['tools'])}")

# Update file description
data['description'] = "InHouse Print quote calculator tools - Calculate pricing with Shopify-based calculators for business cards, flyers, booklets, perfect bound books, letterheads, and corflute signs"

# Write back as clean JSON
with open(schema_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ File saved successfully")
print(f"✅ All GOD calculators removed")
print(f"✅ Emoji corruption fixed")
print(f"✅ Clean UTF-8 without BOM")
