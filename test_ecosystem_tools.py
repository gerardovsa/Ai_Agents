"""
Test Google Workspace and Microsoft 365 specific queries
"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
search = SemanticToolSearch(registry)

test_queries = [
    # Google Workspace queries
    'read my Gmail inbox',
    'create a Google Doc',
    'share a Google Sheet with my team',
    'add event to Google Calendar',
    'upload file to Google Drive',
    'create Google Slides presentation',
    'make a Google Form survey',
    'add task to Google Tasks',
    'search my Drive for documents',
    'get Google Analytics data',
    
    # Microsoft 365 queries
    'read my Outlook emails',
    'create a Word document',
    'share an Excel spreadsheet',
    'schedule Outlook meeting',
    'upload to OneDrive',
    'create PowerPoint presentation',
    'make Microsoft Form',
    'add to Microsoft To Do',
    'search OneDrive for files',
    'schedule Teams video call'
]

print("="*100)
print("ECOSYSTEM TOOLS TEST - Google Workspace & Microsoft 365")
print("="*100)

for idx, query in enumerate(test_queries, 1):
    ecosystem = "Google" if idx <= 10 else "Microsoft"
    print(f'\n{"="*100}')
    print(f'TEST {idx}/20 [{ecosystem}]: "{query}"')
    print('='*100)
    
    results = search.search(query, top_k=5)
    
    if results:
        for i, tool in enumerate(results, 1):
            name = tool['tool_name']
            platform = tool.get('platform', 'unknown')
            similarity = tool.get('similarity', 0)
            desc = tool.get('short_description', 'No description')[:100]
            
            # Highlight if wrong ecosystem
            wrong_ecosystem = False
            if idx <= 10:  # Google query
                if 'microsoft' in platform.lower() or 'outlook' in platform.lower():
                    wrong_ecosystem = True
            else:  # Microsoft query
                if 'google' in platform.lower() or 'gmail' in platform.lower():
                    wrong_ecosystem = True
            
            marker = ' ⚠️ WRONG ECOSYSTEM!' if wrong_ecosystem else ''
            print(f'{i}. {name} [{platform}] - {similarity:.1%}{marker}')
            print(f'   {desc}')
    else:
        print('❌ No matches found')

print(f'\n{"="*100}')
print("TEST COMPLETE")
print("="*100)
