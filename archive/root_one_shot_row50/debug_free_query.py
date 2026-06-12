import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
search = SemanticToolSearch(registry)

query = 'when am I free this week'
results = search.search(query, top_k=10, similarity_threshold=0.0)  # Show ALL matches

print(f'Query: "{query}"')
print(f'Found {len(results)} results\n')

if results:
    for i, r in enumerate(results, 1):
        print(f'{i}. {r["tool_name"]} - {r.get("similarity", 0):.1%}')
        print(f'   {r.get("short_description", "")[:80]}')
else:
    print('NO MATCHES - Threshold too high?')
