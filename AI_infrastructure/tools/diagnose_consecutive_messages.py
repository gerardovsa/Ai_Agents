# Diagnostic Script: Find Corrupted Conversations with Consecutive Assistant Messages
# Created: January 19, 2026
# Purpose: Identify threads in database that have consecutive assistant messages

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
infrastructure_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(infrastructure_dir)

sys.path.insert(0, infrastructure_dir)
sys.path.insert(0, root_dir)

from AI_infrastructure.shared.database_utils import execute_query

def find_corrupted_threads():
    """Find all threads with consecutive assistant messages"""
    
    print("\n" + "="*80)
    print("🔍 SCANNING DATABASE FOR CONSECUTIVE ASSISTANT MESSAGES")
    print("="*80 + "\n")
    
    # Get all threads
    threads = execute_query(
        "SELECT id, thread_slug, name FROM sessions.threads ORDER BY updated_at DESC LIMIT 100",
        fetch_mode='all'
    )
    
    print(f"📊 Checking {len(threads)} most recent threads...\n")
    
    corrupted_threads = []
    
    for thread in threads:
        thread_id = thread['id']
        thread_slug = thread['thread_slug']
        thread_name = thread['name']
        
        # Get messages for this thread in chronological order
        messages = execute_query(
            """
            SELECT id, role, created_at 
            FROM sessions.messages 
            WHERE thread_id = %s 
            ORDER BY created_at ASC
            """,
            (thread_id,),
            fetch_mode='all'
        )
        
        if not messages or len(messages) < 2:
            continue
        
        # Check for consecutive assistant messages
        has_consecutive = False
        consecutive_pairs = []
        
        for i in range(len(messages) - 1):
            current_role = messages[i]['role']
            next_role = messages[i+1]['role']
            
            if current_role == 'assistant' and next_role == 'assistant':
                has_consecutive = True
                consecutive_pairs.append({
                    'index': i,
                    'current_id': messages[i]['id'],
                    'next_id': messages[i+1]['id'],
                    'current_created': messages[i]['created_at'],
                    'next_created': messages[i+1]['created_at']
                })
        
        if has_consecutive:
            corrupted_threads.append({
                'thread_id': thread_id,
                'thread_slug': thread_slug,
                'thread_name': thread_name,
                'total_messages': len(messages),
                'consecutive_pairs': consecutive_pairs
            })
            
            print(f"❌ FOUND CORRUPTION: {thread_name}")
            print(f"   Thread Slug: {thread_slug}")
            print(f"   Total Messages: {len(messages)}")
            print(f"   Consecutive Pairs: {len(consecutive_pairs)}")
            for pair in consecutive_pairs:
                print(f"      • Messages [{pair['index']}] → [{pair['index']+1}]: assistant → assistant")
                print(f"        IDs: {pair['current_id']} → {pair['next_id']}")
            print()
    
    print("="*80)
    print(f"📊 SUMMARY:")
    print(f"   Total threads scanned: {len(threads)}")
    print(f"   Corrupted threads found: {len(corrupted_threads)}")
    print("="*80 + "\n")
    
    if corrupted_threads:
        print("⚠️  RECOMMENDED ACTIONS:")
        print("1. Review the corrupted threads to understand the pattern")
        print("2. Determine if these are recent (after Jan 19 fix) or old corruption")
        print("3. Run cleanup script to remove duplicate assistant messages")
        print("\nTO FIX: Run fix_corrupted_conversations.py")
    else:
        print("✅ NO CORRUPTION FOUND - All conversations are valid!")
    
    return corrupted_threads

if __name__ == '__main__':
    try:
        corrupted = find_corrupted_threads()
        
        # Save results to file for analysis
        if corrupted:
            import json
            from datetime import datetime
            
            filename = f"corrupted_threads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(corrupted, f, indent=2, default=str)
            
            print(f"\n📄 Full report saved to: {filename}")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
