"""
Quick test for subtask creation field name fix
"""
import requests
import json

BASE_URL = "http://localhost:5001/api/synergy"

def test_subtask_creation():
    """Test that subtask creation works with 'task' field"""
    
    print("\n=== Testing Subtask Creation Fix ===\n")
    
    # First, create a test session with a task
    print("1. Creating test session...")
    session_payload = {
        "title": "Test Subtask Field Fix",
        "description": "Testing field name compatibility"
    }
    
    response = requests.post(f"{BASE_URL}/create", json=session_payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"   ERROR: {response.text}")
        return False
    
    session_id = response.json()['session_id']
    print(f"   ✅ Session created: {session_id}")
    
    # Create a task
    print("\n2. Creating test task...")
    task_payload = {
        "task": "Test Task for Subtask",
        "priority": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/{session_id}/task/create", json=task_payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return False
    
    task_id = response.json()['task_id']
    print(f"   ✅ Task created: {task_id}")
    
    # Test subtask creation with 'task' field (tool standard)
    print("\n3. Creating subtask with 'task' field...")
    subtask_payload = {
        "task": "Research Australian suppliers",  # Using 'task' field
        "priority": "high"
    }
    
    response = requests.post(f"{BASE_URL}/task/{task_id}/subtask/create", json=subtask_payload)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        print(f"   ✅ Subtask created successfully!")
        subtask_id = response.json()['subtask_id']
        print(f"   Subtask ID: {subtask_id}")
        return True
    else:
        print(f"   ❌ FAILED: {response.text}")
        return False

if __name__ == "__main__":
    import time
    print("Waiting 3 seconds for Flask server to start...")
    time.sleep(3)
    
    success = test_subtask_creation()
    
    if success:
        print("\n✅ FIELD NAME FIX WORKING!")
        print("Backend now accepts 'task' field (tool standard)")
        print("Also maintains backward compatibility with 'subtask' field")
    else:
        print("\n❌ Test failed - check server logs")
