"""
Find all threads with messages in database
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
load_dotenv()

from AI_infrastructure.shared.database_utils import execute_query

print("\n🔍 FINDING ALL THREADS WITH MESSAGES IN DATABASE")
print("=" * 100)

query = """
    SELECT 
        thread_id,
        COUNT(*) as message_count,
        MIN(created_at) as first_message,
        MAX(created_at) as last_message
    FROM sessions.messages
    GROUP BY thread_id
    ORDER BY MAX(created_at) DESC
    LIMIT 20
"""

threads = execute_query(query, (), fetch_mode='all')

print(f"\n📊 FOUND {len(threads)} THREADS WITH MESSAGES:\n")
print("=" * 100)
print("| THREAD_ID        | MSG COUNT | FIRST MESSAGE       | LAST MESSAGE        |")
print("=" * 100)

for t in threads:
    thread_id = str(t['thread_id']).ljust(16)
    count = str(t['message_count']).rjust(9)
    first = str(t['first_message'])[:19]
    last = str(t['last_message'])[:19]
    print(f"| {thread_id} | {count} | {first} | {last} |")

print("=" * 100)

if threads:
    print(f"\n✅ Use one of these thread IDs to query messages")
    print(f"\nExample: python get_agent2_db_order.py {threads[0]['thread_id']}")
