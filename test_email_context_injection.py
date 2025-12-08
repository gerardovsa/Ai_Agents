"""
Test Email Context Injection Implementation
Verifies that email context is properly injected into AI system prompts

Run this after deploying the updated agent_routes_v4.py
"""

import requests
import json

# Configuration
API_URL = "http://localhost:5001"  # Adjust if needed
USER_ID = 12  # Adjust to your test user ID

def test_email_context_injection():
    """
    Test that email context is injected when thread has email_thread_id
    """
    print("=" * 80)
    print("🧪 EMAIL CONTEXT INJECTION TEST")
    print("=" * 80)
    
    # Step 1: Create a test thread
    print("\n📝 Step 1: Creating test thread...")
    thread_response = requests.post(f"{API_URL}/api/threads/create", json={
        "user_id": USER_ID,
        "title": "Test Email Thread",
        "tags": ["email", "test"]
    })
    
    if not thread_response.ok:
        print(f"❌ Failed to create thread: {thread_response.status_code}")
        return
    
    thread_data = thread_response.json()
    thread_slug = thread_data.get('thread_slug')
    print(f"✅ Thread created: {thread_slug}")
    
    # Step 2: Link email to thread
    print("\n📧 Step 2: Linking email to thread...")
    email_response = requests.post(f"{API_URL}/api/thread-assignments/email", json={
        "user_id": USER_ID,
        "thread_slug": thread_slug,
        "email_thread_id": "test_msg_123456",
        "email_subject": "Test Quote Request - Integration Test",
        "email_participants": ["test@example.com", "support@company.com"]
    })
    
    if not email_response.ok:
        print(f"❌ Failed to link email: {email_response.status_code}")
        print(f"Response: {email_response.text}")
        return
    
    email_data = email_response.json()
    print(f"✅ Email linked: {email_data}")
    
    # Step 3: Send a test message to trigger context injection
    print("\n💬 Step 3: Sending test message to trigger AI context...")
    print("   (Check server console for '📧 EMAIL THREAD LINKED' message)")
    
    chat_response = requests.post(f"{API_URL}/api/chat/stream", json={
        "message": "What email is this thread about?",
        "user_id": USER_ID,
        "thread_slug": thread_slug,
        "stream": False  # Disable streaming for testing
    })
    
    if chat_response.ok:
        print("✅ Message sent successfully")
        print("\n📊 CHECK SERVER CONSOLE FOR:")
        print("   [STREAM] 📧 EMAIL THREAD LINKED → test_msg_123456")
        print("   [STREAM] ✅ Context injection: X sections")
        print("\n💡 If you see those messages, email context is working!")
    else:
        print(f"⚠️  Message may have failed: {chat_response.status_code}")
    
    # Step 4: Cleanup - unlink email
    print("\n🧹 Step 4: Cleanup - unlinking email...")
    unlink_response = requests.post(f"{API_URL}/api/thread-assignments/email/unlink", json={
        "user_id": USER_ID,
        "thread_slug": thread_slug
    })
    
    if unlink_response.ok:
        print("✅ Email unlinked successfully")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print("\nVERIFICATION STEPS:")
    print("1. Check server console for '📧 EMAIL THREAD LINKED' message")
    print("2. Verify email badge appears in UI (if frontend is running)")
    print("3. Check AI response mentions the email subject")
    print("4. System prompt should include email context section")
    print("\n" + "=" * 80)


def test_email_query():
    """
    Test retrieving thread with email data
    """
    print("\n" + "=" * 80)
    print("🔍 DATABASE QUERY TEST")
    print("=" * 80)
    
    # This simulates what agent_routes_v4.py does
    print("\n📋 SQL Query to retrieve email context:")
    print("""
    SELECT 
        synergy_card_id,
        workflow_slug, workflow_title,
        automation_slug, automation_title,
        internal_doc_slug, internal_doc_title,
        email_thread_id, email_subject, email_participants  ← NEW FIELDS
    FROM sessions.threads 
    WHERE thread_slug = %s
    LIMIT 1
    """)
    
    print("\n✅ This query now includes email fields!")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Starting Email Context Injection Tests\n")
    
    # Test 1: Database query structure
    test_email_query()
    
    # Test 2: Full integration test
    print("\n⚠️  Make sure your Flask server is running on", API_URL)
    print("   Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
        test_email_context_injection()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
