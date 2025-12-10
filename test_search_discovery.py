"""Test improved search discovery"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')

from tools.implementations.meta_tools import search_tools

# Test various search terms
test_terms = [
    'quote',
    'price', 
    'signs',
    'booklet',
    'business cards',
    'notepad',
    'flyers',
    'letterhead',
    'poster',
    'banner'
]

print("\n" + "="*80)
print("IMPROVED SEARCH DISCOVERY TEST")
print("="*80 + "\n")

for term in test_terms:
    result = search_tools(term)
    count = len(result.get("tools", []))
    print(f"'{term}': {count} tools found")

print("\n" + "="*80)
print("Test complete!")
print("="*80)
