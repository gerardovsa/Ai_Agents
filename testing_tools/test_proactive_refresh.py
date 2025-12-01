"""
Test Proactive Token Refresh Logic
"""

from datetime import datetime, timedelta, timezone

def _should_refresh_token(expires_at, buffer_seconds=600):
    """Test implementation of the refresh logic"""
    if not expires_at:
        return False
    
    if isinstance(expires_at, str):
        try:
            expires_at_str = expires_at.replace('Z', '+00:00').replace(' ', 'T')
            expires_at = datetime.fromisoformat(expires_at_str)
        except Exception as e:
            print(f"Could not parse expires_at '{expires_at}': {e}")
            return False
    
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    buffer_time = expires_at - timedelta(seconds=buffer_seconds)
    
    should_refresh = now >= buffer_time
    
    if should_refresh:
        time_until_expiry = (expires_at - now).total_seconds()
        print(f"Token expiring in {int(time_until_expiry)} seconds - triggering proactive refresh")
    
    return should_refresh


# Run tests
print("Proactive Token Refresh Logic Tests")
print("=" * 60)

# Test 1: Token expires in 5 minutes (should refresh - within 10 min buffer)
expires_in_5_min = datetime.now(timezone.utc) + timedelta(minutes=5)
result1 = _should_refresh_token(expires_in_5_min, buffer_seconds=600)
print(f"\nTest 1: Token expires in 5 minutes")
print(f"Result: {'REFRESH NOW' if result1 else 'NO REFRESH NEEDED'}")
print(f"Expected: REFRESH NOW (within 10-minute buffer)")
print(f"Status: {'PASS' if result1 else 'FAIL'}")

# Test 2: Token expires in 15 minutes (should NOT refresh - outside buffer)
print("\n" + "-" * 60)
expires_in_15_min = datetime.now(timezone.utc) + timedelta(minutes=15)
result2 = _should_refresh_token(expires_in_15_min, buffer_seconds=600)
print(f"\nTest 2: Token expires in 15 minutes")
print(f"Result: {'REFRESH NOW' if result2 else 'NO REFRESH NEEDED'}")
print(f"Expected: NO REFRESH NEEDED (outside 10-minute buffer)")
print(f"Status: {'PASS' if not result2 else 'FAIL'}")

# Test 3: Token expires in 9 minutes (should refresh - edge case)
print("\n" + "-" * 60)
expires_in_9_min = datetime.now(timezone.utc) + timedelta(minutes=9)
result3 = _should_refresh_token(expires_in_9_min, buffer_seconds=600)
print(f"\nTest 3: Token expires in 9 minutes")
print(f"Result: {'REFRESH NOW' if result3 else 'NO REFRESH NEEDED'}")
print(f"Expected: REFRESH NOW (within 10-minute buffer)")
print(f"Status: {'PASS' if result3 else 'FAIL'}")

# Test 4: Token already expired (should definitely refresh)
print("\n" + "-" * 60)
already_expired = datetime.now(timezone.utc) - timedelta(minutes=1)
result4 = _should_refresh_token(already_expired, buffer_seconds=600)
print(f"\nTest 4: Token expired 1 minute ago")
print(f"Result: {'REFRESH NOW' if result4 else 'NO REFRESH NEEDED'}")
print(f"Expected: REFRESH NOW (already expired)")
print(f"Status: {'PASS' if result4 else 'FAIL'}")

# Summary
print("\n" + "=" * 60)
total_tests = 4
passed_tests = sum([result1, not result2, result3, result4])
print(f"\nTest Summary: {passed_tests}/{total_tests} tests passed")

if passed_tests == total_tests:
    print("Status: ALL TESTS PASSED - Logic is working correctly")
else:
    print("Status: SOME TESTS FAILED - Logic needs adjustment")
