import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

client = create_client(url, key)

# Count total threads
result = client.table('saved_threads').select('id', count='exact').execute()
print(f'Total threads in Supabase: {result.count}')

# Count by user if possible
try:
    user_threads = client.table('saved_threads').select('user_id', count='exact').execute()
    print(f'\nThread breakdown:')
    all_threads = client.table('saved_threads').select('user_id, id').execute()
    if all_threads.data:
        user_counts = {}
        for thread in all_threads.data:
            uid = thread.get('user_id', 'unknown')
            user_counts[uid] = user_counts.get(uid, 0) + 1
        for uid, count in user_counts.items():
            print(f'  User {uid}: {count} threads')
except Exception as e:
    print(f'Could not get user breakdown: {e}')
