"""
Send test message with Team ID routing
Tests both Central HQ and Local Ops modes
"""

import requests
import json
import time

API_BASE = "http://localhost:5001"
TEST_AGENT = "3"

def send_test_message(mode="central"):
    """Send a test message in specified privacy mode"""
    
    thread_slug = f"test_{mode}_{int(time.time())}"
    
    if mode == "central":
        print("\n" + "="*80)
        print("  Testing CENTRAL HQ Mode (Broadcast)")
        print("="*80)
        
        payload = {
            "thread_slug": thread_slug,
            "thread_id": thread_slug,
            "message": f"[CENTRAL HQ TEST] This message should be visible to all team members",
            "sender_team_id": "alice_test",
            "recipient_team_id": None,  # ✅ Broadcast
            "message_type": "direct",
            "privacy_mode": "central"
        }
        
        print("\n📤 Sending message...")
        print(f"   Mode: Central HQ (Collaborative)")
        print(f"   Sender: alice_test")
        print(f"   Recipient: NULL (broadcast to all)")
        
    else:  # local
        print("\n" + "="*80)
        print("  Testing LOCAL OPS Mode (Private)")
        print("="*80)
        
        payload = {
            "thread_slug": thread_slug,
            "thread_id": thread_slug,
            "message": f"[LOCAL OPS TEST] This message should be private to Bob only",
            "sender_team_id": "bob_test",
            "recipient_team_id": "bob_test",  # ✅ Private to Bob
            "message_type": "direct",
            "privacy_mode": "local"
        }
        
        print("\n🔒 Sending message...")
        print(f"   Mode: Local Ops (Private)")
        print(f"   Sender: bob_test")
        print(f"   Recipient: bob_test (private)")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/agent/agent/{TEST_AGENT}/start",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"\n✅ Message sent successfully!")
            data = response.json()
            print(f"   Thread: {data.get('data', {}).get('thread_slug', 'N/A')}")
            print(f"   Status: {data.get('data', {}).get('status', 'N/A')}")
            return thread_slug
        else:
            print(f"\n❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n🧪 Team ID Routing - Live Test")
    print("="*80)
    
    # Test Central HQ mode
    central_thread = send_test_message("central")
    
    if central_thread:
        print("\n⏳ Waiting 3 seconds for AI response...")
        time.sleep(3)
    
    # Test Local Ops mode
    local_thread = send_test_message("local")
    
    if local_thread:
        print("\n⏳ Waiting 3 seconds for AI response...")
        time.sleep(3)
    
    print("\n" + "="*80)
    print("  Next Steps:")
    print("="*80)
    print("\n   Run: python verify_database_team_id.py")
    print("   → Verify sender_team_id and recipient_team_id are populated")
    print("\n   Check database:")
    print(f"      Central HQ thread: {central_thread}")
    print(f"      Local Ops thread: {local_thread}")
