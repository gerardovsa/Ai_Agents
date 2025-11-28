import json
from collections import defaultdict

# Load all 4 Synergy schema files (synergy_reference_tools.json removed - deprecated)
files = [
    'tools/schemas/synergy_instruction_tools.json',
    'tools/schemas/synergy_recommender_tools.json',
    'tools/schemas/synergy_smart_internal_doc_tool.json',
    'tools/schemas/synergy_tools.json'
]

all_tools = defaultdict(list)

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            file_name = file_path.split('/')[-1]
            
            for tool in data.get('tools', []):
                tool_name = tool.get('name')
                all_tools[tool_name].append(file_name)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# Find duplicates
duplicates = {name: files for name, files in all_tools.items() if len(files) > 1}

print("=" * 80)
print("SYNERGY TOOL DUPLICATION ANALYSIS")
print("=" * 80)

if duplicates:
    print(f"\n❌ FOUND {len(duplicates)} DUPLICATE TOOLS:\n")
    for tool_name, file_list in sorted(duplicates.items()):
        print(f"  🔴 {tool_name}")
        for file in file_list:
            print(f"     - {file}")
        print()
else:
    print("\n✅ NO DUPLICATES FOUND - All tool names are unique!\n")

# Summary per file
print("-" * 80)
print("TOOL COUNT PER FILE:")
print("-" * 80)

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            file_name = file_path.split('/')[-1]
            tool_count = len(data.get('tools', []))
            print(f"{tool_count:2d} tools - {file_name}")
    except Exception as e:
        print(f" ? tools - {file_path.split('/')[-1]} (error: {e})")

# Total unique tools
print(f"\n{'=' * 80}")
print(f"TOTAL UNIQUE TOOLS: {len(all_tools)}")
print(f"TOTAL DEFINITIONS: {sum(len(files) for files in all_tools.values())}")
print(f"{'=' * 80}")
