"""
Check Thread Locations in Supabase - Export and Validate

Queries sessions.threads.location column to check for duplicates
Each non-prime agent should have only ONE thread assigned
"""

import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict

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
    
    return psycopg2.connect(db_url)

def check_thread_locations(user_id=1):
    """
    Query and analyze thread locations
    
    Returns:
        dict: {
            'threads': list of thread data,
            'duplicates': dict of locations with multiple threads,
            'has_duplicates': bool
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all threads with their locations
    cursor.execute("""
        SELECT id, thread_slug, name, location, updated_at, token_count
        FROM sessions.threads
        WHERE user_id = %s
        ORDER BY location, updated_at DESC
    """, [user_id])
    
    rows = cursor.fetchall()
    conn.close()
    
    # Organize by location
    location_counts = defaultdict(list)
    all_threads = []
    
    for row in rows:
        thread_id, slug, name, location, updated_at, token_count = row
        location = location or 'prime'
        
        thread_data = {
            'id': thread_id,
            'slug': slug,
            'name': name,
            'location': location,
            'updated_at': updated_at,
            'message_count': token_count or 0  # Using token_count as proxy for messages
        }
        
        all_threads.append(thread_data)
        location_counts[location].append(thread_data)
    
    # Find duplicates (non-prime locations with >1 thread)
    duplicates = {}
    for location, threads in location_counts.items():
        if location != 'prime' and len(threads) > 1:
            duplicates[location] = threads
    
    return {
        'threads': all_threads,
        'location_counts': dict(location_counts),
        'duplicates': duplicates,
        'has_duplicates': len(duplicates) > 0
    }

def print_report(data):
    """Print formatted report"""
    
    print('\n' + '='*100)
    print('THREAD LOCATIONS IN SUPABASE (sessions.threads.location)')
    print('='*100)
    print(f'{"ID":<5} {"Thread Slug":<20} {"Title":<35} {"Location":<12} {"Msgs":<5} {"Updated"}')
    print('-'*100)
    
    for thread in data['threads']:
        print(f"{thread['id']:<5} {thread['slug']:<20} {thread['name'][:33]:<35} "
              f"{thread['location']:<12} {thread['message_count']:<5} "
              f"{str(thread['updated_at'])[:19]}")
    
    print('\n' + '='*100)
    print('LOCATION SUMMARY (Checking for duplicates)')
    print('='*100)
    
    for location, threads in sorted(data['location_counts'].items()):
        count = len(threads)
        
        if location == 'prime':
            status = '✅'
            note = '(OK - Prime can have multiple threads)'
        elif count == 1:
            status = '✅'
            note = '(OK - Only 1 thread)'
        else:
            status = '🚨 DUPLICATE'
            note = f'(PROBLEM - {count} threads assigned to same agent!)'
        
        print(f'\n{status} {location:<12} : {count} threads {note}')
        
        if count > 1 and location != 'prime':
            print(f'     ⚠️  Only the MOST RECENT should stay, others should move to Prime:')
            for i, thread in enumerate(threads):
                action = '✅ KEEP' if i == 0 else '❌ MOVE TO PRIME'
                print(f'        {action} - ID {thread["id"]}: "{thread["name"][:45]}" '
                      f'(updated: {str(thread["updated_at"])[:19]})')
    
    print('\n' + '='*100)
    if data['has_duplicates']:
        print('❌ RESULT: DUPLICATES FOUND - Run cleanup script to fix!')
        print('   Command: python scripts\\maintenance\\cleanup_duplicate_thread_locations.py --apply')
    else:
        print('✅ RESULT: NO DUPLICATES - All agent locations have only 1 thread!')
    print('='*100 + '\n')
    
    return data['has_duplicates']

def export_to_csv(data, output_file='thread_locations_export.csv'):
    """Export data to CSV file"""
    import csv
    
    output_path = Path(__file__).parent.parent.parent / output_file
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'slug', 'name', 'location', 'updated_at', 'message_count'])
        writer.writeheader()
        
        for thread in data['threads']:
            writer.writerow(thread)
    
    print(f'📄 Data exported to: {output_path}')
    return output_path

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Check thread locations for duplicates')
    parser.add_argument('--user-id', type=int, default=1, help='User ID to check (default: 1)')
    parser.add_argument('--export', action='store_true', help='Export to CSV file')
    
    args = parser.parse_args()
    
    print(f'\n🔍 Checking thread locations for user_id={args.user_id}...\n')
    
    data = check_thread_locations(user_id=args.user_id)
    has_duplicates = print_report(data)
    
    if args.export:
        export_to_csv(data)
    
    # Exit with error code if duplicates found
    import sys
    sys.exit(1 if has_duplicates else 0)
