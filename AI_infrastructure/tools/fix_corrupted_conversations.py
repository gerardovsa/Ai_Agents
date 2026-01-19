# Cleanup Script: Fix Corrupted Conversations with Consecutive Assistant Messages
# Created: January 19, 2026
# Purpose: Remove duplicate consecutive assistant messages from database

import sys
import os
import json
from datetime import datetime

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
infrastructure_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(infrastructure_dir)

sys.path.insert(0, infrastructure_dir)
sys.path.insert(0, root_dir)

from AI_infrastructure.shared.database_utils import execute_query

def fix_corrupted_conversations(dry_run=True):
    """
    Fix conversations with consecutive assistant messages by removing duplicates.
    
    Strategy:
    - When two consecutive assistant messages are found:
      - Keep the FIRST assistant message (it likely has the tool_use)
      - DELETE the SECOND assistant message (it's likely the duplicate)
    
    Args:
        dry_run: If True, only shows what would be fixed without making changes
    """
    
    print("\n" + "="*80)
    print("🔧 FIXING CORRUPTED CONVERSATIONS")
    print(f"   Mode: {'DRY RUN (no changes)' if dry_run else '⚠️  LIVE MODE (will modify database)'}")
    print("="*80 + "\n")
    
    # Load the diagnostic results
    import glob
    diagnostic_files = sorted(glob.glob("corrupted_threads_*.json"), reverse=True)
    
    if not diagnostic_files:
        print("❌ ERROR: No diagnostic results found!")
        print("   Please run diagnose_consecutive_messages.py first")
        return []
    
    latest_diagnostic = diagnostic_files[0]
    print(f"📄 Loading diagnostic results from: {latest_diagnostic}\n")
    
    with open(latest_diagnostic, 'r') as f:
        corrupted_threads = json.load(f)
    
    if not corrupted_threads:
        print("✅ No corrupted threads to fix!")
        return []
    
    print(f"📊 Found {len(corrupted_threads)} corrupted threads\n")
    
    fixed_threads = []
    total_messages_deleted = 0
    
    for thread_data in corrupted_threads:
        thread_slug = thread_data['thread_slug']
        thread_name = thread_data['thread_name']
        consecutive_pairs = thread_data['consecutive_pairs']
        
        print(f"🔨 Processing: {thread_name}")
        print(f"   Thread: {thread_slug}")
        print(f"   Consecutive pairs: {len(consecutive_pairs)}")
        
        messages_deleted_in_thread = 0
        
        for pair in consecutive_pairs:
            current_id = pair['current_id']
            next_id = pair['next_id']
            
            print(f"   • Pair [{pair['index']}→{pair['index']+1}]: {current_id} → {next_id}")
            
            # Get the content of both messages to decide which to keep
            current_msg = execute_query(
                "SELECT content FROM sessions.messages WHERE id = %s",
                (current_id,),
                fetch_mode='one'
            )
            
            next_msg = execute_query(
                "SELECT content FROM sessions.messages WHERE id = %s",
                (next_id,),
                fetch_mode='one'
            )
            
            # Determine which message to delete (usually the second one)
            # But check if first has tool_use to be safe
            delete_id = next_id  # Default: delete the second message
            keep_id = current_id
            
            if current_msg and next_msg:
                current_content = current_msg.get('content', [])
                next_content = next_msg.get('content', [])
                
                # Check if first message has tool_use
                current_has_tool = any(
                    block.get('type') == 'tool_use' 
                    for block in current_content 
                    if isinstance(block, dict)
                )
                
                # Check if second message has tool_use
                next_has_tool = any(
                    block.get('type') == 'tool_use' 
                    for block in next_content 
                    if isinstance(block, dict)
                )
                
                # If only second has tool_use, keep it instead
                if next_has_tool and not current_has_tool:
                    delete_id = current_id
                    keep_id = next_id
                    print(f"      → Keeping SECOND message (has tool_use), deleting FIRST")
                else:
                    print(f"      → Keeping FIRST message, deleting SECOND")
            
            if not dry_run:
                # DELETE the duplicate message
                execute_query(
                    "DELETE FROM sessions.messages WHERE id = %s",
                    (delete_id,)
                )
                print(f"      ✅ DELETED message {delete_id}")
                messages_deleted_in_thread += 1
                total_messages_deleted += 1
            else:
                print(f"      🔍 Would DELETE message {delete_id} (dry run)")
                messages_deleted_in_thread += 1
        
        fixed_threads.append({
            'thread_slug': thread_slug,
            'thread_name': thread_name,
            'messages_deleted': messages_deleted_in_thread
        })
        
        print(f"   ✅ Fixed {messages_deleted_in_thread} message(s) in this thread\n")
    
    print("="*80)
    print(f"📊 CLEANUP SUMMARY:")
    print(f"   Threads processed: {len(fixed_threads)}")
    print(f"   Messages deleted: {total_messages_deleted}")
    
    if dry_run:
        print(f"\n⚠️  THIS WAS A DRY RUN - No changes were made")
        print(f"   To apply changes, run with: --live")
    else:
        print(f"\n✅ CLEANUP COMPLETE - Database has been updated")
        
        # Save cleanup report
        report_filename = f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'threads_fixed': fixed_threads,
                'total_messages_deleted': total_messages_deleted
            }, f, indent=2)
        
        print(f"   Report saved to: {report_filename}")
    
    print("="*80 + "\n")
    
    return fixed_threads

if __name__ == '__main__':
    try:
        # Check if --live flag is provided
        is_live = '--live' in sys.argv
        
        if is_live:
            print("\n⚠️  WARNING: You are about to modify the database!")
            print("   This will DELETE duplicate assistant messages permanently.")
            response = input("\n   Type 'YES' to continue: ")
            
            if response.strip().upper() != 'YES':
                print("\n❌ Operation cancelled by user")
                sys.exit(0)
        
        fixed = fix_corrupted_conversations(dry_run=not is_live)
        
        if is_live:
            print("\n✅ NEXT STEPS:")
            print("1. Verify the cleanup worked correctly")
            print("2. Test the affected conversations")
            print("3. Monitor for new consecutive assistant messages")
            print("\nRun diagnose_consecutive_messages.py to verify all issues are fixed")
        else:
            print("\n📋 NEXT STEPS:")
            print("1. Review the dry run results above")
            print("2. If everything looks good, run with --live flag:")
            print("   python AI_infrastructure/tools/fix_corrupted_conversations.py --live")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
