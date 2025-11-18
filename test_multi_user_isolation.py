"""
Multi-User Thread Isolation Test
Created: November 19, 2025

Purpose: Simulate multiple users sending messages to different agents
         and verify NO cross-contamination of responses between threads.

Test Scenarios:
1. User A → Agent 1 → "My name is Alice"
2. User B → Agent 8 → "My name is Bob" 
3. User C → Agent 1 → "My name is Charlie"
4. User D → Agent 8 → "My name is Diana"

Expected: Each agent remembers ONLY their own user's name
"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Tuple

BASE_URL = "http://localhost:5001"

# Test colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def create_thread(user_name: str, agent_location: str) -> str:
    """Create a thread for a user"""
    resp = requests.post(f"{BASE_URL}/api/threads/create", json={
        "title": f"{user_name}'s Thread",
        "location": agent_location,
        "user_id": 14
    })
    
    if resp.status_code == 200:
        thread_slug = resp.json()['data']['thread']['id']
        print(f"  [{user_name}] Thread created: {thread_slug}")
        return thread_slug
    else:
        print(f"  [{user_name}] FAILED to create thread: {resp.status_code}")
        return None

def send_message(user_name: str, agent_id: str, thread_slug: str, message: str) -> bool:
    """Send a message to an agent"""
    resp = requests.post(f"{BASE_URL}/api/agent/agent/{agent_id}/start", json={
        "message": message,
        "session_id": thread_slug,
        "thread_slug": thread_slug
    })
    
    if resp.status_code == 200:
        print(f"  [{user_name}] Message sent to Agent {agent_id}")
        return True
    else:
        print(f"  [{user_name}] FAILED to send message: {resp.status_code}")
        return False

def stream_response(user_name: str, agent_id: str, thread_slug: str) -> Tuple[str, List[str]]:
    """Stream response and extract text content"""
    url = f"{BASE_URL}/api/agent/stream/{agent_id}?thread_slug={thread_slug}"
    
    try:
        resp = requests.get(url, stream=True, timeout=45)
        
        if resp.status_code != 200:
            print(f"  [{user_name}] Stream failed: {resp.status_code}")
            return "", []
        
        text_blocks = []
        thinking_blocks = []
        
        for line in resp.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            
            if line.startswith('data:'):
                try:
                    data = json.loads(line.split(':', 1)[1])
                    
                    if data.get('type') == 'content_delta' and data.get('text'):
                        text_blocks.append(data['text'])
                    
                    if data.get('type') == 'thinking' and data.get('content'):
                        thinking_blocks.append(data['content'])
                    
                    if data.get('type') == 'complete':
                        break
                
                except json.JSONDecodeError:
                    pass
        
        full_text = ''.join(text_blocks)
        print(f"  [{user_name}] Response received: {full_text[:60]}...")
        
        return full_text, thinking_blocks
    
    except Exception as e:
        print(f"  [{user_name}] Stream error: {e}")
        return "", []

def test_user_scenario(user_name: str, agent_id: str, agent_location: str, 
                       intro_message: str, test_message: str) -> Dict:
    """Run complete test scenario for one user"""
    print(f"\n{Colors.OKBLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}Testing: {user_name} → Agent {agent_id}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*80}{Colors.ENDC}")
    
    result = {
        'user': user_name,
        'agent_id': agent_id,
        'thread_slug': None,
        'intro_response': '',
        'test_response': '',
        'success': False,
        'cross_contamination': False
    }
    
    # Step 1: Create thread
    print(f"\n[Step 1] Creating thread...")
    thread_slug = create_thread(user_name, agent_location)
    if not thread_slug:
        return result
    
    result['thread_slug'] = thread_slug
    time.sleep(1)
    
    # Step 2: Send introduction
    print(f"\n[Step 2] Sending introduction: '{intro_message}'")
    if not send_message(user_name, agent_id, thread_slug, intro_message):
        return result
    
    time.sleep(2)
    
    # Step 3: Get response
    print(f"\n[Step 3] Streaming response...")
    intro_response, _ = stream_response(user_name, agent_id, thread_slug)
    result['intro_response'] = intro_response
    
    time.sleep(2)
    
    # Step 4: Send test question
    print(f"\n[Step 4] Sending test question: '{test_message}'")
    if not send_message(user_name, agent_id, thread_slug, test_message):
        return result
    
    time.sleep(2)
    
    # Step 5: Get test response
    print(f"\n[Step 5] Streaming test response...")
    test_response, _ = stream_response(user_name, agent_id, thread_slug)
    result['test_response'] = test_response
    
    # Verify response contains correct name
    if user_name in test_response:
        result['success'] = True
        print(f"{Colors.OKGREEN}  ✓ SUCCESS: Agent remembered {user_name}'s name{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}  ✗ FAILED: Agent didn't remember name{Colors.ENDC}")
    
    # Check for cross-contamination (other users' names)
    other_names = ['Alice', 'Bob', 'Charlie', 'Diana']
    other_names.remove(user_name)
    
    for other_name in other_names:
        if other_name in test_response:
            result['cross_contamination'] = True
            print(f"{Colors.FAIL}  ✗ CROSS-CONTAMINATION: Found '{other_name}' in {user_name}'s response!{Colors.ENDC}")
            break
    
    return result

def run_sequential_test():
    """Run tests sequentially (one after another)"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}SEQUENTIAL TEST - Running tests one at a time{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    scenarios = [
        ("Alice", "1", "prime", "My name is Alice. Remember it.", "What is my name?"),
        ("Bob", "8", "agent-8", "My name is Bob. Remember it.", "What is my name?"),
        ("Charlie", "1", "prime", "My name is Charlie. Remember it.", "What is my name?"),
        ("Diana", "8", "agent-8", "My name is Diana. Remember it.", "What is my name?"),
    ]
    
    results = []
    
    for user_name, agent_id, location, intro, test in scenarios:
        result = test_user_scenario(user_name, agent_id, location, intro, test)
        results.append(result)
        time.sleep(3)  # Pause between users
    
    return results

def run_parallel_test():
    """Run tests in parallel (simulate concurrent users)"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}PARALLEL TEST - Simulating concurrent users{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    scenarios = [
        ("Alice", "1", "prime", "My name is Alice. Remember it.", "What is my name?"),
        ("Bob", "8", "agent-8", "My name is Bob. Remember it.", "What is my name?"),
        ("Charlie", "1", "prime", "My name is Charlie. Remember it.", "What is my name?"),
        ("Diana", "8", "agent-8", "My name is Diana. Remember it.", "What is my name?"),
    ]
    
    results = []
    threads = []
    
    def worker(user_name, agent_id, location, intro, test):
        result = test_user_scenario(user_name, agent_id, location, intro, test)
        results.append(result)
    
    # Start all users simultaneously
    for user_name, agent_id, location, intro, test in scenarios:
        t = threading.Thread(target=worker, args=(user_name, agent_id, location, intro, test))
        threads.append(t)
        t.start()
        time.sleep(0.5)  # Slight stagger to avoid overwhelming server
    
    # Wait for all to complete
    for t in threads:
        t.join()
    
    return results

def print_summary(results: List[Dict], test_type: str):
    """Print test summary"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{test_type} TEST RESULTS SUMMARY{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    total = len(results)
    success = sum(1 for r in results if r['success'])
    contaminated = sum(1 for r in results if r['cross_contamination'])
    
    print(f"Total tests: {total}")
    print(f"Successful: {Colors.OKGREEN}{success}{Colors.ENDC}")
    print(f"Failed: {Colors.FAIL}{total - success}{Colors.ENDC}")
    print(f"Cross-contamination detected: {Colors.FAIL if contaminated > 0 else Colors.OKGREEN}{contaminated}{Colors.ENDC}\n")
    
    # Detailed results
    for result in results:
        status = Colors.OKGREEN + "✓ PASS" if result['success'] and not result['cross_contamination'] else Colors.FAIL + "✗ FAIL"
        contamination = Colors.FAIL + " [CONTAMINATED]" if result['cross_contamination'] else ""
        
        print(f"{status}{Colors.ENDC} {result['user']} (Agent {result['agent_id']})")
        print(f"       Thread: {result['thread_slug']}")
        print(f"       Response: {result['test_response'][:80]}{contamination}{Colors.ENDC}")
        print()
    
    # Final verdict
    if success == total and contaminated == 0:
        print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}🎉 ALL TESTS PASSED - NO CROSS-CONTAMINATION!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}{'='*80}{Colors.ENDC}")
        print(f"{Colors.FAIL}⚠️  TESTS FAILED - ISSUES DETECTED{Colors.ENDC}")
        print(f"{Colors.FAIL}{'='*80}{Colors.ENDC}")
        return False

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}MULTI-USER THREAD ISOLATION TEST{Colors.ENDC}")
    print(f"{Colors.BOLD}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    print(f"\nTest Scenarios:")
    print(f"  1. Alice → Agent 1 → 'My name is Alice'")
    print(f"  2. Bob → Agent 8 → 'My name is Bob'")
    print(f"  3. Charlie → Agent 1 → 'My name is Charlie' (DIFFERENT THREAD)")
    print(f"  4. Diana → Agent 8 → 'My name is Diana' (DIFFERENT THREAD)")
    
    print(f"\nExpected Behavior:")
    print(f"  - Each agent should remember ONLY their conversation's name")
    print(f"  - Agent 1 should have TWO separate threads (Alice + Charlie)")
    print(f"  - Agent 8 should have TWO separate threads (Bob + Diana)")
    print(f"  - NO cross-contamination between threads")
    
    input(f"\nPress Enter to start SEQUENTIAL test...")
    
    # Run sequential test
    sequential_results = run_sequential_test()
    sequential_pass = print_summary(sequential_results, "SEQUENTIAL")
    
    input(f"\nPress Enter to start PARALLEL test...")
    
    # Run parallel test
    parallel_results = run_parallel_test()
    parallel_pass = print_summary(parallel_results, "PARALLEL")
    
    # Overall results
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}OVERALL TEST RESULTS{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    print(f"Sequential Test: {Colors.OKGREEN + 'PASS' if sequential_pass else Colors.FAIL + 'FAIL'}{Colors.ENDC}")
    print(f"Parallel Test: {Colors.OKGREEN + 'PASS' if parallel_pass else Colors.FAIL + 'FAIL'}{Colors.ENDC}")
    
    if sequential_pass and parallel_pass:
        print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✅ THREAD ISOLATION FIX VERIFIED - ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}{'='*80}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ THREAD ISOLATION BROKEN - CROSS-CONTAMINATION DETECTED{Colors.ENDC}")
        print(f"{Colors.FAIL}{'='*80}{Colors.ENDC}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
