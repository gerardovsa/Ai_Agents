"""
Test Stream Response - Verify NameError fix works
Created: November 19, 2025 11:50 PM

Purpose: Test that AI responses now include text (not just thinking blocks)
         after fixing the NameError: session_id not defined bug.

Expected Result: Should receive text response from AI
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def create_test_thread():
    """Create a new thread for testing"""
    print("📝 Creating test thread...")
    
    response = requests.post(
        f"{BASE_URL}/api/threads/create",
        json={
            "title": f"NameError Fix Test - {datetime.now().strftime('%H:%M:%S')}",
            "location": "prime",
            "user_id": 14
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        # API returns thread in data.thread with id field as thread_slug
        thread_slug = data.get('data', {}).get('thread', {}).get('id')
        print(f"✅ Thread created: {thread_slug}")
        return thread_slug
    else:
        print(f"❌ Failed to create thread: {response.status_code}")
        print(response.text)
        return None

def send_message_to_agent(thread_slug, agent_id="1"):
    """Send a test message to an agent"""
    print(f"\n💬 Sending message to Agent {agent_id}...")
    
    response = requests.post(
        f"{BASE_URL}/api/agent/agent/{agent_id}/start",
        json={
            "message": "Say hello and tell me what 2+2 equals. Keep it brief.",
            "session_id": thread_slug,
            "thread_slug": thread_slug
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Message sent successfully")
        print(f"   Session ID: {data.get('session_id')}")
        return True
    else:
        print(f"❌ Failed to send message: {response.status_code}")
        print(response.text)
        return False

def stream_agent_response(thread_slug, agent_id="1"):
    """Stream the agent's response and check for text content"""
    print(f"\n🔄 Streaming response from Agent {agent_id}...\n")
    
    url = f"{BASE_URL}/api/agent/stream/{agent_id}?thread_slug={thread_slug}"
    
    thinking_blocks = []
    text_blocks = []
    tool_blocks = []
    errors = []
    
    try:
        response = requests.get(url, stream=True, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Stream failed with status {response.status_code}")
            print(response.text)
            return False
        
        print("📡 Stream started, receiving events...\n")
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            
            # Parse SSE events
            if line.startswith('event:'):
                event_type = line.split(':', 1)[1].strip()
            elif line.startswith('data:'):
                data_json = line.split(':', 1)[1].strip()
                try:
                    data = json.loads(data_json)
                    
                    # Track different block types
                    if event_type == 'thinking':
                        thinking_blocks.append(data.get('content', ''))
                        print(f"🤔 [Thinking] {data.get('content', '')[:60]}...")
                    
                    elif event_type == 'text':
                        text_blocks.append(data.get('content', ''))
                        print(f"💬 [Text] {data.get('content', '')}")
                    
                    elif event_type == 'tool_use':
                        tool_name = data.get('tool_name', 'unknown')
                        tool_blocks.append(tool_name)
                        print(f"🔧 [Tool] {tool_name}")
                    
                    elif event_type == 'error':
                        error_msg = data.get('error', 'Unknown error')
                        errors.append(error_msg)
                        print(f"❌ [Error] {error_msg}")
                    
                    elif event_type == 'complete':
                        print(f"\n✅ [Complete] Stream finished")
                        break
                
                except json.JSONDecodeError:
                    print(f"⚠️  Failed to parse JSON: {data_json[:100]}")
        
        # Analyze results
        print("\n" + "="*80)
        print("📊 STREAM ANALYSIS")
        print("="*80)
        print(f"   Thinking blocks: {len(thinking_blocks)}")
        print(f"   Text blocks: {len(text_blocks)}")
        print(f"   Tool blocks: {len(tool_blocks)}")
        print(f"   Errors: {len(errors)}")
        print()
        
        # Check for success
        if errors:
            print("❌ TEST FAILED - Errors detected:")
            for err in errors:
                print(f"   - {err}")
            return False
        
        if not text_blocks:
            print("❌ TEST FAILED - No text blocks received!")
            print("   This indicates the NameError bug may still exist.")
            print("   OR the AI only used thinking/tools without text.")
            return False
        
        print("✅ TEST PASSED - Text response received!")
        print("\n📝 Full text response:")
        print("-" * 80)
        for text in text_blocks:
            print(text)
        print("-" * 80)
        
        return True
    
    except requests.exceptions.Timeout:
        print("❌ TEST FAILED - Stream timeout (60s)")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the complete test"""
    print("="*80)
    print("STREAM RESPONSE TEST - NameError Fix Verification")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Create thread
    thread_slug = create_test_thread()
    if not thread_slug:
        print("\n❌ TEST ABORTED - Could not create thread")
        return False
    
    # Step 2: Send message
    time.sleep(1)
    if not send_message_to_agent(thread_slug):
        print("\n❌ TEST ABORTED - Could not send message")
        return False
    
    # Step 3: Stream response
    time.sleep(2)
    success = stream_agent_response(thread_slug)
    
    # Final result
    print("\n" + "="*80)
    if success:
        print("🎉 SUCCESS! NameError fix is working correctly!")
        print("   Text responses are being received from the AI.")
    else:
        print("⚠️  FAILURE! Stream did not produce text response.")
        print("   Check Flask logs for NameError or other exceptions.")
    print("="*80)
    
    return success


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
