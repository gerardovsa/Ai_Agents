"""
Test Script: Enhanced /api/agent/start Endpoint (Option 2)

Tests the new metadata + multimodal content support added to /api/agent/start
for Communication Hub email workflow compatibility.

Run this BEFORE updating Communication Hub to verify backend changes work.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
THREAD_SLUG = f"test-email-workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def test_1_simple_text_message():
    """Test 1: Simple text message (existing functionality - should still work)"""
    print("\n" + "="*80)
    print("TEST 1: Simple Text Message (Backward Compatibility)")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/api/agent/Alpha/start",
        json={
            "thread_slug": THREAD_SLUG,
            "message": "Hello, this is a simple text message"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Simple text message failed"
    assert response.json()['success'], "Response not successful"
    print("✅ TEST 1 PASSED: Simple text messages still work")


def test_2_multimodal_content_array():
    """Test 2: Multimodal content array (new functionality)"""
    print("\n" + "="*80)
    print("TEST 2: Multimodal Content Array (NEW)")
    print("="*80)
    
    # Simulate email with text + image attachment
    multimodal_content = [
        {
            "type": "text",
            "text": "Please review this invoice document"
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/agent/Alpha/start",
        json={
            "thread_slug": THREAD_SLUG,
            "message": multimodal_content  # Array instead of string
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Multimodal content failed"
    assert response.json()['success'], "Response not successful"
    print("✅ TEST 2 PASSED: Multimodal content arrays work")


def test_3_email_metadata():
    """Test 3: Email metadata from Communication Hub (new functionality)"""
    print("\n" + "="*80)
    print("TEST 3: Email Metadata (NEW - Communication Hub Format)")
    print("="*80)
    
    # Simulate Communication Hub email assignment
    email_content = [
        {
            "type": "text",
            "text": "Subject: Q4 Budget Proposal\n\nPlease find attached the budget proposal..."
        },
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": "JVBERi0xLjQKJeLjz9MK"  # Minimal PDF header
            }
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/agent/Alpha/start",
        json={
            "thread_slug": THREAD_SLUG,
            "message": email_content,
            "metadata": {
                "message_type": "email",
                "email_id": "AAMkAGI2TnZmAAA=",
                "has_attachments": True,
                "email_subject": "Q4 Budget Proposal",
                "email_from": "john.doe@example.com",
                "email_date": "2026-01-13T10:30:00Z"
            }
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Email metadata failed"
    assert response.json()['success'], "Response not successful"
    print("✅ TEST 3 PASSED: Email metadata preserved")


def test_4_verify_database_storage():
    """Test 4: Verify metadata saved to database"""
    print("\n" + "="*80)
    print("TEST 4: Database Storage Verification")
    print("="*80)
    
    # Query database to verify metadata was saved
    from AI_infrastructure.shared.database_utils import execute_query
    
    messages = execute_query(
        """
        SELECT role, content, metadata, created_at
        FROM sessions.messages m
        JOIN sessions.threads t ON m.thread_id = t.id
        WHERE t.thread_slug = %s
        ORDER BY m.created_at DESC
        LIMIT 3
        """,
        (THREAD_SLUG,),
        fetch_mode='all'
    )
    
    print(f"\nFound {len(messages)} messages in database:")
    for idx, msg in enumerate(messages):
        print(f"\n--- Message {idx+1} ---")
        print(f"Role: {msg['role']}")
        print(f"Content: {str(msg['content'])[:200]}...")
        print(f"Metadata: {msg['metadata']}")
        
        # Check if email metadata was preserved
        if msg['metadata'] and msg['metadata'].get('message_type') == 'email':
            print("✅ Email metadata found in database!")
            assert 'email_id' in msg['metadata'], "email_id missing"
            assert 'has_attachments' in msg['metadata'], "has_attachments missing"
    
    print("\n✅ TEST 4 PASSED: Metadata stored correctly in database")


def test_5_communication_hub_simulation():
    """Test 5: Full Communication Hub email workflow simulation"""
    print("\n" + "="*80)
    print("TEST 5: Communication Hub Email Workflow Simulation")
    print("="*80)
    
    # This simulates EXACTLY what Communication Hub line 3210 would send
    # after being updated to use /api/agent/start instead of /api/threads/messages/save
    
    email_thread_slug = f"email-workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Step 1: Create thread (Communication Hub does this first)
    print("\nStep 1: Creating thread...")
    create_response = requests.post(
        f"{BASE_URL}/api/threads/create",
        json={
            "thread_slug": email_thread_slug,
            "agent_id": "Alpha",
            "user_id": 1
        }
    )
    print(f"Thread created: {create_response.status_code}")
    
    # Step 2: Save email as document with metadata (NEW: using /api/agent/start)
    print("\nStep 2: Saving email with /api/agent/start...")
    
    email_content_blocks = [
        {
            "type": "text",
            "text": "From: customer@example.com\nSubject: Quote Request - Business Cards\n\nHi, I need a quote for 500 business cards..."
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": "/9j/4AAQSkZJRg=="  # Mock JPEG
            }
        }
    ]
    
    email_response = requests.post(
        f"{BASE_URL}/api/agent/Alpha/start",
        json={
            "thread_slug": email_thread_slug,
            "message": email_content_blocks,
            "metadata": {
                "message_type": "email",
                "email_id": "AAMkAGI2TESTID",
                "has_attachments": True,
                "source": "outlook"
            }
        }
    )
    
    print(f"Email saved: {email_response.status_code}")
    print(f"Response: {json.dumps(email_response.json(), indent=2)}")
    
    assert email_response.status_code == 200, "Email save failed"
    
    # Step 3: Verify email appears in thread with metadata
    print("\nStep 3: Verifying email in database...")
    from AI_infrastructure.shared.database_utils import execute_query
    
    thread_messages = execute_query(
        """
        SELECT role, content, metadata
        FROM sessions.messages m
        JOIN sessions.threads t ON m.thread_id = t.id
        WHERE t.thread_slug = %s
        ORDER BY m.created_at ASC
        """,
        (email_thread_slug,),
        fetch_mode='all'
    )
    
    print(f"\nThread has {len(thread_messages)} messages:")
    for msg in thread_messages:
        print(f"- {msg['role']}: {msg['metadata']}")
    
    # Verify email metadata preserved
    email_msg = thread_messages[0]
    assert email_msg['metadata']['message_type'] == 'email', "Email type not preserved"
    assert email_msg['metadata']['email_id'] == 'AAMkAGI2TESTID', "Email ID not preserved"
    assert email_msg['metadata']['has_attachments'] == True, "Attachment flag not preserved"
    
    print("\n✅ TEST 5 PASSED: Communication Hub workflow works with /api/agent/start!")


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*80)
    print("ENHANCED /api/agent/start ENDPOINT TEST SUITE")
    print("Testing Option 2: Metadata + Multimodal Support")
    print("="*80)
    
    try:
        test_1_simple_text_message()
        test_2_multimodal_content_array()
        test_3_email_metadata()
        test_4_verify_database_storage()
        test_5_communication_hub_simulation()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\n🎉 Backend is ready for Communication Hub update!")
        print("\nNext steps:")
        print("1. Deploy these backend changes to production")
        print("2. Update Communication Hub line 3210 to use /api/agent/start")
        print("3. Test email assignment workflow in production")
        print("4. Monitor for any issues")
        
    except AssertionError as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"Error: {e}")
        print("\n⚠️ DO NOT update Communication Hub until this is fixed!")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ UNEXPECTED ERROR")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if Flask server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✅ Flask server detected at {BASE_URL}")
    except:
        print(f"❌ Flask server not running at {BASE_URL}")
        print("Start the server first: cd AI_infrastructure && python flask_app.py")
        exit(1)
    
    run_all_tests()
