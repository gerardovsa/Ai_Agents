"""Check specific platform coverage"""
import json
from pathlib import Path

# Check the three platforms we fixed
platforms_to_check = {
    'microsoft_todo_tools.json': 'microsoft_todo',
    'universal_file_tools.json': 'universal_file', 
    'pinecone_tools.json': 'pinecone'
}

print("\n" + "=" * 80)
print("VERIFICATION: Fixed Platforms Coverage")
print("=" * 80)

for schema_file, platform_name in platforms_to_check.items():
    file_path = Path("tools/schemas") / schema_file
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'tools' in data:
                total = len(data['tools'])
                with_short = sum(1 for t in data['tools'] if 'short_description' in t and t['short_description'])
                coverage = (with_short / total * 100) if total > 0 else 0
                
                status = "PASS" if coverage == 100 else "FAIL"
                print(f"\n{status} {platform_name}:")
                print(f"  Total tools: {total}")
                print(f"  With short_description: {with_short}")
                print(f"  Coverage: {coverage:.1f}%")
                
                if coverage < 100:
                    print(f"  Missing: {total - with_short} tools")
                    # Show which tools are missing
                    missing = [t['name'] for t in data['tools'] if 'short_description' not in t or not t['short_description']]
                    for tool in missing[:5]:
                        print(f"    - {tool}")
                    if len(missing) > 5:
                        print(f"    ... and {len(missing) - 5} more")
    except Exception as e:
        print(f"\nERROR {platform_name}: {e}")

print("\n" + "=" * 80)
