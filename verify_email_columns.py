"""
Quick script to verify email columns are populated in sessions.threads
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

# Check the two threads that were created
thread_ids = ['1766038193066', '1766038196373']

print("\n" + "="*80)
print("Verifying Email Column Population in sessions.threads")
print("="*80)

for thread_id in thread_ids:
    print(f"\n🔍 Checking thread: {thread_id}")
    print("-" * 80)
    
    result = execute_query(
        """
        SELECT 
            thread_slug,
            name,
            location,
            email_thread_id,
            email_subject,
            email_participants,
            created_at
        FROM sessions.threads 
        WHERE thread_slug = %s
        """,
        (thread_id,),
        fetch_mode='one'
    )
    
    if result:
        print(f"📧 Thread Slug: {result[0]}")
        print(f"📝 Name: {result[1]}")
        print(f"📍 Location: {result[2]}")
        print(f"🆔 Email Thread ID: {result[3]}")
        print(f"✉️  Email Subject: {result[4]}")
        print(f"👥 Email Participants: {result[5]}")
        print(f"📅 Created: {result[6]}")
        
        if result[3]:  # email_thread_id
            print("\n✅ SUCCESS: Email data IS populated!")
        else:
            print("\n❌ FAILURE: Email data is NULL!")
    else:
        print(f"❌ Thread {thread_id} not found in database")

print("\n" + "="*80)
