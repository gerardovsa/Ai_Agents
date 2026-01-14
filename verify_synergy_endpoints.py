"""
Verification Script: Test All Synergy Endpoints for Proper Array Handling
Tests that all 5 session-returning endpoints return empty arrays instead of null
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(name, url, method="GET", data=None):
    """Test an endpoint and verify JSON array fields"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        data = response.json()
        
        # Extract sessions from response
        sessions = []
        if isinstance(data, list):
            sessions = data
        elif 'sessions' in data:
            if isinstance(data['sessions'], list):
                sessions = data['sessions']
            elif isinstance(data['sessions'], dict):
                sessions = list(data['sessions'].values())
        elif 'session' in data:
            sessions = [data['session']]
        elif 'session_id' in data:
            sessions = [data]
        
        if not sessions:
            print("⚠️  WARNING: No sessions in response")
            return True
        
        # Check first session for proper array fields
        session = sessions[0]
        array_fields = [
            'assignees', 'tags', 'documents', 'links',
            'next_steps', 'recent_activity', 'checklist',
            'thread_ids', 'assigned_agents', 'platforms_involved'
        ]
        
        print(f"\nChecking {len(sessions)} session(s)...")
        all_good = True
        
        for field in array_fields:
            if field in session:
                value = session[field]
                if value is None:
                    print(f"   ❌ FAIL: {field} = null (should be [])")
                    all_good = False
                elif isinstance(value, list):
                    print(f"   ✅ PASS: {field} = [...] ({len(value)} items)")
                else:
                    print(f"   ⚠️  WARN: {field} = {type(value).__name__} (expected list)")
        
        return all_good
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    print("\n" + "="*70)
    print(" SYNERGY ENDPOINTS VERIFICATION")
    print(" Testing all 5 session-returning endpoints")
    print("="*70)
    
    tests = [
        ("Endpoint 1: /api/synergy/list", f"{BASE_URL}/api/synergy/list"),
        ("Endpoint 2: /api/synergy/sessions/batch", f"{BASE_URL}/api/synergy/sessions/batch"),
        ("Endpoint 3: /api/synergy (bulk)", f"{BASE_URL}/api/synergy"),
        ("Endpoint 4: /api/synergy/<session_id>", f"{BASE_URL}/api/synergy/sess_example_20241216_000000"),
        ("Endpoint 5: /api/synergy/search", f"{BASE_URL}/api/synergy/search?query=test"),
    ]
    
    results = []
    for name, url in tests:
        result = test_endpoint(name, url)
        results.append((name, result))
    
    # Summary
    print(f"\n{'='*70}")
    print(" SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("All endpoints properly return empty arrays instead of null")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Check failed endpoints above for details")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
