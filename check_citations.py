"""
Quick check to see if citations are stored in the database
"""

import sys
from pathlib import Path
import json

# Add paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def check_for_citations():
    """Check if citations exist in recent assistant messages"""
    print("\n" + "="*80)
    print("CHECKING FOR CITATIONS IN DATABASE")
    print("="*80 + "\n")
    
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    # Get recent assistant messages
    cursor.execute("""
        SELECT id, thread_id, content, created_at 
        FROM sessions.messages 
        WHERE role = 'assistant'
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    messages = cursor.fetchall()
    
    if not messages:
        print("No assistant messages found in database")
        conn.close()
        return
    
    print(f"Checking last {len(messages)} assistant messages...\n")
    
    found_citations = False
    
    for idx, row in enumerate(messages, 1):
        # Handle both tuple and dict results
        if isinstance(row, dict):
            msg_id = row['id']
            thread_id = row['thread_id']
            content = row['content']
            created_at = row['created_at']
        else:
            msg_id = row[0]
            thread_id = row[1]
            content = row[2]
            created_at = row[3]
        
        # Check if content has citations
        has_citations = False
        citation_count = 0
        
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if 'citations' in block:
                        has_citations = True
                        citation_count += len(block['citations'])
        
        status = "✅ HAS CITATIONS" if has_citations else "❌ NO CITATIONS"
        
        print(f"Message {idx}:")
        print(f"  ID: {msg_id}")
        print(f"  Thread: {thread_id}")
        print(f"  Created: {created_at}")
        print(f"  Status: {status}")
        
        if has_citations:
            found_citations = True
            print(f"  Citations found: {citation_count}")
            
            # Show first citation
            for block in content:
                if isinstance(block, dict) and 'citations' in block:
                    first_citation = block['citations'][0]
                    print(f"  First citation:")
                    print(f"    URL: {first_citation.get('url', 'N/A')}")
                    print(f"    Title: {first_citation.get('title', 'N/A')[:60]}...")
                    print(f"    Text: {first_citation.get('cited_text', 'N/A')[:100]}...")
                    break
        
        print()
    
    conn.close()
    
    print("="*80)
    if found_citations:
        print("✅ RESULT: Citations ARE being stored in the database!")
    else:
        print("❌ RESULT: NO citations found in recent messages")
        print("\nPossible reasons:")
        print("  1. No web searches have been performed recently")
        print("  2. Citations are being stripped before saving")
        print("  3. Web fetch tool doesn't have citations enabled")
    print("="*80 + "\n")

if __name__ == "__main__":
    check_for_citations()
