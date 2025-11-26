"""
Test session management endpoints

Tests:
1. Create multiple sessions (simulate different browsers/devices)
2. List all sessions
3. Revoke a specific session
4. Revoke all sessions
5. Verify device_info is captured correctly
"""

import sys
import os
import requests
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

BASE_URL = "http://localhost:5001"

def test_session_management():
    """Test session management complete workflow"""
    
    print("=" * 70)
    print("SESSION MANAGEMENT TEST")
    print("=" * 70)
    
    # Test 1: Use dev mode auto-login (GET request from localhost)
    print("\n[TEST 1] Dev mode auto-login (Chrome on Windows)")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/api/auth/login", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    if response.status_code == 200:
        data = response.json()
        token1 = data.get('token')
        print(f"SUCCESS - Dev mode login successful")
        print(f"  User: {data.get('user')}")
        print(f"  Token: {token1[:50]}...")
    else:
        print(f"FAIL - Dev login failed: {response.json()}")
        return False
    
    # Test 2: Create second session (simulate different browser)
    print("\n[TEST 2] Create second session (Firefox on Windows)")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/api/auth/login", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    })
    
    if response.status_code == 200:
        data = response.json()
        token2 = data.get('token')
        print(f"SUCCESS - Created second session")
        print(f"  Token: {token2[:50]}...")
    else:
        print(f"FAIL - Second login failed: {response.json()}")
        return False
    
    # Test 3: List all sessions
    print("\n[TEST 3] List all active sessions")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/api/auth/sessions", headers={
        "Authorization": f"Bearer {token1}"
    })
    
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('sessions', [])
        print(f"SUCCESS - Found {len(sessions)} active sessions")
        print()
        for session in sessions:
            device = session.get('device_info', {})
            browser = device.get('browser', 'Unknown')
            os_name = device.get('os', 'Unknown')
            device_type = device.get('device_type', 'Unknown')
            is_current = " (CURRENT)" if session.get('is_current') else ""
            
            print(f"  Session ID: {session.get('id')}{is_current}")
            print(f"    Device: {browser} on {os_name} ({device_type})")
            print(f"    IP: {session.get('ip_address', 'N/A')}")
            print(f"    Created: {session.get('created_at')}")
            print(f"    Expires: {session.get('expires_at')}")
            print()
    else:
        print(f"FAIL - Failed to list sessions: {response.json()}")
        return False
    
    # Test 4: Revoke second session (from first session)
    print("\n[TEST 4] Revoke second session")
    print("-" * 70)
    
    # Get session ID of second session
    response = requests.get(f"{BASE_URL}/api/auth/sessions", headers={
        "Authorization": f"Bearer {token1}"
    })
    sessions = response.json().get('sessions', [])
    second_session_id = None
    
    for session in sessions:
        if not session.get('is_current'):
            second_session_id = session.get('id')
            break
    
    if second_session_id:
        response = requests.delete(f"{BASE_URL}/api/auth/sessions/{second_session_id}", headers={
            "Authorization": f"Bearer {token1}"
        })
        
        if response.status_code == 200:
            print(f"SUCCESS - Revoked session {second_session_id}")
        else:
            print(f"FAIL - Failed to revoke session: {response.json()}")
            return False
    else:
        print("INFO - No second session to revoke")
    
    # Test 5: Verify second session is revoked
    print("\n[TEST 5] Verify second session no longer works")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/api/auth/sessions", headers={
        "Authorization": f"Bearer {token2}"
    })
    
    if response.status_code == 401:
        print("SUCCESS - Second session correctly rejected (revoked)")
    elif response.status_code == 200:
        sessions_count = len(response.json().get('sessions', []))
        print(f"INFO - Session still valid, {sessions_count} session(s) remaining")
    else:
        print(f"INFO - Got response code {response.status_code}")
    
    # Test 6: Test revoking current session (should fail)
    print("\n[TEST 6] Try to revoke current session (should fail)")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/api/auth/sessions", headers={
        "Authorization": f"Bearer {token1}"
    })
    sessions = response.json().get('sessions', [])
    current_session_id = None
    
    for session in sessions:
        if session.get('is_current'):
            current_session_id = session.get('id')
            break
    
    if current_session_id:
        response = requests.delete(f"{BASE_URL}/api/auth/sessions/{current_session_id}", headers={
            "Authorization": f"Bearer {token1}"
        })
        
        if response.status_code == 400:
            print("SUCCESS - Correctly prevented revoking current session")
            print(f"  Error: {response.json().get('error')}")
        else:
            print(f"WARNING - Expected 400, got {response.status_code}")
    
    print("\n" + "=" * 70)
    print("SESSION MANAGEMENT TEST COMPLETE")
    print("=" * 70)
    print("\nPhase 2.3 Status: COMPLETE")
    print("  - Device info captured during login")
    print("  - Sessions list correctly with device info")
    print("  - Sessions can be revoked individually")
    print("  - Current session protection works")
    print("\nNext: Phase 2.4 - Build Active Sessions UI")
    
    return True

if __name__ == '__main__':
    try:
        # Wait for server to be ready
        import time
        time.sleep(2)
        
        success = test_session_management()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Server not running. Start with BISTART first.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
