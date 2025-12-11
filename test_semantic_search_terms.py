"""
Test 20 common user queries to identify tool description issues
"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
search = SemanticToolSearch(registry)

test_queries = [
    'schedule a meeting with John tomorrow at 2pm',
    'book an appointment for next Friday',
    'when am I free this week',
    'cancel my 3pm meeting',
    'reschedule my dentist appointment',
    'send an email to the team',
    'create a spreadsheet with sales data',
    'make a quote for customer',
    'generate an invoice',
    'track project progress',
    'create a document with meeting notes',
    'upload files to cloud storage',
    'analyze website traffic',
    'schedule a video call',
    'find available meeting rooms',
    'create a form for feedback',
    'send a text message',
    'process a payment',
    'backup my database',
    'deploy to production'
]

print("="*100)
print("SEMANTIC TOOL SEARCH TEST - 20 Common User Queries")
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
