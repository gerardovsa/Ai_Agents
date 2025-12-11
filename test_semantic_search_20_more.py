"""
Test 20 MORE user queries to identify additional tool description issues
"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
search = SemanticToolSearch(registry)

test_queries = [
    'send invoice to customer',
    'update my calendar settings',
    'export data to CSV',
    'create a presentation slide',
    'add a task to my todo list',
    'share a document with my team',
    'search for contacts',
    'run a SQL query',
    'get analytics report',
    'compress a PDF file',
    'merge two documents',
    'create a backup',
    'list all my files',
    'convert image to PDF',
    'translate this text',
    'summarize this document',
    'check spelling',
    'create a chart',
    'set a reminder',
    'archive old emails'
]

print("="*100)
print("SEMANTIC TOOL SEARCH TEST - 20 MORE User Queries")
print("="*100)

for idx, query in enumerate(test_queries, 1):
    print(f'\n{"="*100}')
    print(f'TEST {idx}/20: "{query}"')
    print('='*100)
    
    results = search.search(query, top_k=5)
    
    if results:
        for i, tool in enumerate(results, 1):
            name = tool['tool_name']
            platform = tool.get('platform', 'unknown')
            similarity = tool.get('similarity', 0)
            desc = tool.get('short_description', 'No description')[:100]
            print(f'{i}. {name} [{platform}] - {similarity:.1%}')
            print(f'   {desc}')
    else:
        print('❌ No matches found')

print(f'\n{"="*100}')
print("TEST COMPLETE")
print("="*100)
