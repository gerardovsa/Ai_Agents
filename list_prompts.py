"""List all prompts in database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
from shared.database_utils import execute_query

result = execute_query(
    'SELECT name, category, type FROM ai_infrastructure.prompt_library ORDER BY category, name',
    fetch_mode='all'
)

print(f'Total prompts: {len(result)}\n')

categories = {}
for r in result:
    categories.setdefault(r['category'], []).append(f"{r['name']} ({r['type']})")

for cat, prompts in sorted(categories.items()):
    print(f'\n{cat.upper()}: {len(prompts)} prompts')
    for p in prompts:
        print(f'  - {p}')
