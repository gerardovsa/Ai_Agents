"""
Third Round Ecosystem Test - 20 More Varied Queries
Focus on natural language variations and edge cases
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

# Initialize semantic search
registry = RegistryV3()
searcher = SemanticToolSearch(registry)

# 20 new test queries with natural language variations
test_queries = [
    # Google Workspace - Natural variations (10 queries)
    'send message via Gmail',
    'new spreadsheet in Google Sheets',
    'set up a meeting in Google Calendar',
    'save file to Google Drive',
    'make a survey with Google Forms',
    'presentation in Google Slides',
    'find files in my Google Drive',
    'Google Calendar event',
    'write a Google Doc',
    'Gmail inbox management',
    
    # Microsoft 365 - Natural variations (10 queries)
    'send message via Outlook',
    'new spreadsheet in Excel',
    'set up a meeting in Outlook Calendar',
    'save file to OneDrive',
    'make a survey with Microsoft Forms',
    'presentation in PowerPoint',
    'find files in my OneDrive',
    'Outlook Calendar event',
    'write a Word document',
    'Outlook inbox management',
]

print("="*100)
print("THIRD ROUND ECOSYSTEM TEST - 20 MORE QUERIES")
print("="*100)

results = {
    'google_correct': 0,
    'microsoft_correct': 0,
    'wrong_ecosystem': 0,
    'no_matches': 0,
    'cross_contamination': []
}

for idx, query in enumerate(test_queries, 1):
    # Determine expected ecosystem
    is_google_query = idx <= 10
    expected_ecosystem = "google" if is_google_query else "microsoft"
    
    print(f"\n{'='*100}")
    print(f"TEST {idx}/20 [{'Google' if is_google_query else 'Microsoft'}]: \"{query}\"")
    print("="*100)
    
    # Run semantic search
    suggestions = searcher.search(query, top_k=5)
    
    if not suggestions:
        print("❌ NO MATCHES FOUND")
        results['no_matches'] += 1
        continue
    
    # Check top match
    top_tool = suggestions[0]
    tool_name = top_tool['tool_name']
    platform = top_tool.get('platform', 'unknown')
    similarity = top_tool.get('similarity', 0.0)
    
    # Detect wrong ecosystem
    wrong_ecosystem = False
    if is_google_query:
        # Google query should match Google tools
        if any(x in platform.lower() for x in ['microsoft', 'outlook', 'onedrive', 'excel', 'word', 'teams']):
            wrong_ecosystem = True
            results['wrong_ecosystem'] += 1
            results['cross_contamination'].append({
                'query': query,
                'expected': 'google',
                'got_platform': platform,
                'tool': tool_name,
                'rank': 1
            })
    else:  # Microsoft query
        # Microsoft query should match Microsoft tools
        if any(x in platform.lower() for x in ['google', 'gmail', 'drive', 'sheets', 'docs']):
            wrong_ecosystem = True
            results['wrong_ecosystem'] += 1
            results['cross_contamination'].append({
                'query': query,
                'expected': 'microsoft',
                'got_platform': platform,
                'tool': tool_name,
                'rank': 1
            })
    
    # Display top 5 results
    for rank, tool_result in enumerate(suggestions, 1):
        tool_name = tool_result['tool_name']
        similarity = tool_result.get('similarity', 0.0)
        platform = tool_result.get('platform', 'unknown')
        description = tool_result.get('short_description', '')
        
        # Check if wrong ecosystem in top 5
        wrong_in_top5 = False
        if is_google_query and rank > 1:
            if any(x in platform.lower() for x in ['microsoft', 'outlook', 'onedrive', 'excel', 'word']):
                wrong_in_top5 = True
                results['cross_contamination'].append({
                    'query': query,
                    'expected': 'google',
                    'got_platform': platform,
                    'tool': tool_name,
                    'rank': rank
                })
        elif not is_google_query and rank > 1:
            if any(x in platform.lower() for x in ['google', 'gmail', 'drive', 'sheets', 'docs']):
                wrong_in_top5 = True
                results['cross_contamination'].append({
                    'query': query,
                    'expected': 'microsoft',
                    'got_platform': platform,
                    'tool': tool_name,
                    'rank': rank
                })
        
        marker = ''
        if rank == 1 and wrong_ecosystem:
            marker = ' ⚠️ WRONG ECOSYSTEM!'
        elif wrong_in_top5:
            marker = ' ⚠️ WRONG ECOSYSTEM!'
        
        print(f"{rank}. {tool_name} [{platform}] - {similarity:.1%}{marker}")
        if rank == 1:
            print(f"   {description[:100]}")
    
    # Count success
    if not wrong_ecosystem:
        if is_google_query:
            results['google_correct'] += 1
        else:
            results['microsoft_correct'] += 1

print("\n" + "="*100)
print("FINAL RESULTS")
print("="*100)
print(f"\n✅ Google Queries Correct: {results['google_correct']}/10 ({results['google_correct']/10*100:.1f}%)")
print(f"✅ Microsoft Queries Correct: {results['microsoft_correct']}/10 ({results['microsoft_correct']/10*100:.1f}%)")
print(f"⚠️  Wrong Ecosystem Matches: {results['wrong_ecosystem']}")
print(f"❌ No Matches Found: {results['no_matches']}")
print(f"\n📊 Overall Success Rate: {(results['google_correct'] + results['microsoft_correct'])/20*100:.1f}%")

if results['cross_contamination']:
    print(f"\n{'='*100}")
    print(f"CROSS-ECOSYSTEM CONTAMINATION DETAILS ({len(results['cross_contamination'])} issues)")
    print("="*100)
    
    # Group by rank
    rank1_issues = [x for x in results['cross_contamination'] if x['rank'] == 1]
    other_issues = [x for x in results['cross_contamination'] if x['rank'] > 1]
    
    if rank1_issues:
        print(f"\n🔴 CRITICAL - Wrong #1 Match ({len(rank1_issues)} issues):")
        for issue in rank1_issues:
            print(f"\n   Query: \"{issue['query']}\"")
            print(f"   Expected: {issue['expected']} ecosystem")
            print(f"   Got: {issue['tool']} [{issue['got_platform']}]")
    
    if other_issues:
        print(f"\n⚠️  Lower Rank Contamination ({len(other_issues)} issues in top 5):")
        for issue in other_issues[:5]:  # Show first 5
            print(f"   \"{issue['query']}\" → {issue['tool']} at rank #{issue['rank']}")

print("\n" + "="*100)
print("TEST COMPLETE")
print("="*100)
