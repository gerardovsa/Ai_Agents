"""
Extended Ecosystem Test - More Google vs Microsoft Queries
Tests cross-platform contamination with edge cases
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

# Initialize semantic search
registry = RegistryV3()
searcher = SemanticToolSearch(registry)

# 30 additional test queries (15 Google, 15 Microsoft)
test_queries = [
    # Google Workspace - Edge Cases
    'compose email in Gmail',
    'make a new Google spreadsheet',
    'schedule recurring meeting in Google Calendar',
    'upload file to Google Drive folder',
    'create Google Form survey',
    'share Google Slides with edit access',
    'search Google Drive by file type',
    'add event to my Google Calendar',
    'create blank Google Doc',
    'organize my Gmail with labels',
    'export Google Sheet to CSV',
    'duplicate Google Doc',
    'add collaborators to Google Drive file',
    'create Google Meet link',
    'check my Google Calendar availability',
    
    # Microsoft 365 - Edge Cases
    'draft email in Outlook',
    'make a new Excel workbook',
    'schedule recurring appointment in Outlook',
    'upload file to OneDrive folder',
    'create Microsoft Forms survey',
    'share PowerPoint with edit permissions',
    'search OneDrive by file name',
    'add appointment to Outlook Calendar',
    'create blank Word file',
    'organize Outlook with folders',
    'export Excel to PDF',
    'copy Word document',
    'share OneDrive file with team',
    'start Teams meeting',
    'check Outlook Calendar free time',
]

print("="*100)
print("EXTENDED ECOSYSTEM TEST - 30 MORE QUERIES")
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
    is_google_query = idx <= 15
    expected_ecosystem = "google" if is_google_query else "microsoft"
    
    print(f"\n{'='*100}")
    print(f"TEST {idx}/30 [{'Google' if is_google_query else 'Microsoft'}]: \"{query}\"")
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
        if 'microsoft' in platform.lower() or 'outlook' in platform.lower() or 'onedrive' in platform.lower():
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
        if 'google' in platform.lower() or 'gmail' in platform.lower() or 'drive' in platform.lower():
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
            if 'microsoft' in platform.lower() or 'outlook' in platform.lower():
                wrong_in_top5 = True
                results['cross_contamination'].append({
                    'query': query,
                    'expected': 'google',
                    'got_platform': platform,
                    'tool': tool_name,
                    'rank': rank
                })
        elif not is_google_query and rank > 1:
            if 'google' in platform.lower() or 'gmail' in platform.lower():
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
print(f"\n✅ Google Queries Correct: {results['google_correct']}/15 ({results['google_correct']/15*100:.1f}%)")
print(f"✅ Microsoft Queries Correct: {results['microsoft_correct']}/15 ({results['microsoft_correct']/15*100:.1f}%)")
print(f"⚠️  Wrong Ecosystem Matches: {results['wrong_ecosystem']}")
print(f"❌ No Matches Found: {results['no_matches']}")
print(f"\n📊 Overall Success Rate: {(results['google_correct'] + results['microsoft_correct'])/30*100:.1f}%")

if results['cross_contamination']:
    print(f"\n{'='*100}")
    print(f"CROSS-ECOSYSTEM CONTAMINATION DETAILS ({len(results['cross_contamination'])} issues)")
    print("="*100)
    for issue in results['cross_contamination']:
        print(f"\n⚠️  Query: \"{issue['query']}\"")
        print(f"   Expected: {issue['expected']} ecosystem")
        print(f"   Got: {issue['tool']} [{issue['got_platform']}] at rank #{issue['rank']}")

print("\n" + "="*100)
print("TEST COMPLETE")
print("="*100)
