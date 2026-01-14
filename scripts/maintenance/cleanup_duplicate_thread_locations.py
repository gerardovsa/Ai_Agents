"""
Cleanup Script: Fix Multiple Threads Assigned to Same Agent

PROBLEM:
- Multiple threads have location='agent-3', location='agent-4', etc.
- This violates the rule: ONE thread per agent at a time

SOLUTION:
- For each agent that has multiple threads, keep only the MOST RECENT one
- Move older threads to location='prime'

Author: AI Agent
Date: 2025-11-18
"""

import sys
import os
import psycopg2
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(__file__).parent.parent.parent
env_file = root_dir / '.env.master'
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

def get_db_connection():
    """Get connection to Supabase PostgreSQL"""
    db_url = os.getenv('SUPABASE_DB_URL')
    
    if not db_url:
        # Fallback for local testing
        db_url = "postgresql://postgres.xnpbpowppyugjvhnmnfk:Tswizzle132$@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    
    print(f'[DB] Connecting to Supabase PostgreSQL...')
    return psycopg2.connect(db_url)

def cleanup_duplicate_locations(user_id=1, dry_run=True):
    """
    Fix database: Ensure each agent has only ONE thread
    
    Args:
        user_id: User ID to fix (default: 1)
        dry_run: If True, only show what would be fixed (default: True)
    
    Returns:
        dict: Summary of changes
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all threads with agent locations
        cursor.execute("""
            SELECT id, name as title, location, updated_at as updated
            FROM sessions.threads
            WHERE user_id = %s 
              AND location IS NOT NULL 
              AND location != 'prime'
              AND location LIKE 'agent-%%'
            ORDER BY location, updated_at DESC
        """, [user_id])
        
        rows = cursor.fetchall()
        
        if not rows:
            print("✅ No agent-assigned threads found")
            return {'changed': 0, 'agents': {}}
        
        # Group threads by location
        location_threads = {}
        for row in rows:
            thread_id = row[0]
            title = row[1]
            location = row[2]
            updated = row[3]
            
            if location not in location_threads:
                location_threads[location] = []
            
            location_threads[location].append({
                'id': thread_id,
                'title': title,
                'updated': updated
            })
        
        # Find duplicates
        print("\n" + "="*60)
        print("DUPLICATE THREAD ANALYSIS")
        print("="*60)
        
        summary = {
            'changed': 0,
            'agents': {}
        }
        
        for location, threads in sorted(location_threads.items()):
            if len(threads) > 1:
                print(f"\n🚨 {location}: {len(threads)} threads (SHOULD BE 1)")
                print("-" * 60)
                
                # Keep most recent, move others to Prime
                keep_thread = threads[0]  # Already sorted by updated DESC
                move_threads = threads[1:]
                
                print(f"  ✅ KEEP: {keep_thread['id']} - '{keep_thread['title']}' (updated: {keep_thread['updated']})")
                
                for thread in move_threads:
                    print(f"  ❌ MOVE TO PRIME: {thread['id']} - '{thread['title']}' (updated: {thread['updated']})")
                    
                    if not dry_run:
                        cursor.execute("""
                            UPDATE sessions.threads 
                            SET location = 'prime', updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s AND user_id = %s
                        """, [thread['id'], user_id])
                        conn.commit()
                        print(f"     → Database updated")
                    
                    summary['changed'] += 1
                
                summary['agents'][location] = {
                    'kept': keep_thread['id'],
                    'moved': [t['id'] for t in move_threads]
                }
            else:
                print(f"\n✅ {location}: 1 thread (OK)")
                thread = threads[0]
                print(f"   {thread['id']} - '{thread['title']}'")
        
        if dry_run:
            print("\n" + "="*60)
            print("DRY RUN MODE - NO CHANGES MADE")
            print("="*60)
            print(f"\nWould move {summary['changed']} threads to Prime")
            print("\nTo apply changes, run:")
            print("  python cleanup_duplicate_thread_locations.py --apply")
        else:
            print("\n" + "="*60)
            print("CLEANUP COMPLETE")
            print("="*60)
            print(f"\nMoved {summary['changed']} threads to Prime")
        
        return summary
        
    finally:
        if conn:
            conn.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix duplicate thread locations')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry run)')
    parser.add_argument('--user-id', type=int, default=1, help='User ID to fix (default: 1)')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("THREAD LOCATION CLEANUP SCRIPT")
    print("="*60)
    print(f"User ID: {args.user_id}")
    print(f"Mode: {'APPLY CHANGES' if args.apply else 'DRY RUN (preview only)'}")
    print("="*60 + "\n")
    
    summary = cleanup_duplicate_locations(
        user_id=args.user_id,
        dry_run=not args.apply
    )
    
    if not args.apply and summary['changed'] > 0:
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Review the changes above")
        print("2. If correct, run with --apply flag:")
        print(f"   python {os.path.basename(__file__)} --apply")
        print("3. Refresh browser (Ctrl+Shift+R) to see changes")
        print("="*60 + "\n")


if __name__ == '__main__':
    main()
