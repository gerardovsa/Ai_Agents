import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
from shared.database_utils import execute_query

# Check if UI/UX prompt exists
result = execute_query(
    "SELECT id, name, category, type FROM ai_infrastructure.prompt_library WHERE id = 92",
    fetch_mode='all'
)
print(f"ID 92 check: {len(result)} found")
if result:
    for r in result:
        print(f"  {r['name']} ({r['category']}, {r['type']})")

# Check for any Consistency or UX related
result2 = execute_query(
    "SELECT id, name, category FROM ai_infrastructure.prompt_library WHERE name LIKE '%Consist%' OR name LIKE '%UX%' OR name LIKE '%UI%'",
    fetch_mode='all'
)
print(f"\nConsistency/UX/UI search: {len(result2)} found")
for r in result2:
    print(f"  ID {r['id']}: {r['name']} ({r['category']})")
