"""
Verify that the description fixes improved semantic matching
"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

registry = RegistryV3()
search = SemanticToolSearch(registry)

# Test the 5 problematic queries
tests = [
    ('when am I free this week', 'google_calendar_check_availability'),
    ('reschedule my dentist appointment', 'google_calendar_update_event'),
    ('create a document with meeting notes', 'google_docs'),
    ('schedule a video call', 'google_meet_create_meeting'),
    ('create a form for feedback', 'google_forms')
]

print('='*100)
print('VERIFICATION TEST - Did the fixes work?')
print('='*100)

for query, expected in tests:
    print(f'\n{"="*100}')
    print(f'Query: "{query}"')
    print(f'Expected tool: {expected}')
    print('='*100)
    
    results = search.search(query, top_k=5)
    
    if results:
        found_expected = False
        for i, tool in enumerate(results, 1):
            name = tool['tool_name']
            platform = tool.get('platform', 'unknown')
            similarity = tool.get('similarity', 0)
            desc = tool.get('short_description', '')[:80]
            
            is_match = expected in name
            status = '✅ CORRECT!' if is_match else ''
            
            print(f'{i}. {name} [{platform}] - {similarity:.1%} {status}')
            print(f'   {desc}')
            
            if is_match and i == 1:
                found_expected = True
        
        if not found_expected:
            print('\n⚠️  Expected tool NOT in top position!')
    else:
        print('❌ No matches found')

print(f'\n{"="*100}')
print('VERIFICATION COMPLETE')
print('='*100)
