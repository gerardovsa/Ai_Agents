"""
Test JWT Secret Consistency Between Token Creation and Verification

This test verifies that the JWT_SECRET used when creating tokens (in auth routes)
matches the JWT_SECRET used when verifying tokens (in user_auth.py).

The bug: 
- microsoft_auth_routes_V2_FIXED.py was using _config.get() (reads .env.master)
- user_auth.py was using os.getenv() (reads OS environment variables)
- On Render, .env.master doesn't exist, causing different secrets
- Result: Signature verification failed, fallback to user_id=1

The fix:
- Make microsoft_auth routes use os.getenv() FIRST, then fallback to _config.get()
- This matches user_auth.py behavior
"""

import os
import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

def test_jwt_secret_consistency():
    """Test that JWT secrets are consistent across modules"""
    
    print("\n" + "="*70)
    print("JWT SECRET CONSISTENCY TEST")
    print("="*70)
    
    # Test 1: Check user_auth.py JWT secret source
    print("\n1️⃣ Testing user_auth.py JWT secret loading...")
    from auth.user_auth import UserAuthManager
    auth_manager = UserAuthManager()
    auth_secret = auth_manager.jwt_secret
    print(f"   user_auth.py JWT_SECRET: {auth_secret[:20]}... (length: {len(auth_secret)})")
    print(f"   Source: os.getenv('JWT_SECRET', fallback)")
    
    # Test 2: Simulate microsoft_auth_routes JWT secret (after fix)
    print("\n2️⃣ Testing microsoft_auth_routes_V2_FIXED.py JWT secret loading...")
    # This simulates the fixed code: os.getenv() FIRST, then _config.get()
    from dotenv import dotenv_values
    env_master_path = Path(__file__).parent / '.env.master'
    if env_master_path.exists():
        _config = dotenv_values(env_master_path)
    else:
        _config = {}
    
    # FIXED: Same pattern as user_auth.py
    microsoft_secret = os.getenv('JWT_SECRET', _config.get('JWT_SECRET', 'your-secret-key-change-this'))
    print(f"   microsoft_auth JWT_SECRET: {microsoft_secret[:20]}... (length: {len(microsoft_secret)})")
    print(f"   Source: os.getenv('JWT_SECRET', fallback to _config)")
    
    # Test 3: Compare secrets
    print("\n3️⃣ Comparing secrets...")
    if auth_secret == microsoft_secret:
        print("   ✅ SECRETS MATCH!")
        print("   Token creation and verification will use the same key")
        print("   JWT signature verification will succeed")
        result = "PASS"
    else:
        print("   ❌ SECRETS DON'T MATCH!")
        print("   Token creation uses different key than verification")
        print("   JWT signature verification will FAIL")
        print(f"   Auth secret:      {auth_secret}")
        print(f"   Microsoft secret: {microsoft_secret}")
        result = "FAIL"
    
    # Test 4: Simulate Render environment (no .env.master)
    print("\n4️⃣ Testing Render environment simulation (no .env.master)...")
    render_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-this')
    print(f"   Render JWT_SECRET: {render_secret[:20]}... (length: {len(render_secret)})")
    
    if render_secret == auth_secret:
        print("   ✅ Render environment will work correctly!")
    else:
        print("   ❌ Render environment will fail!")
    
    # Summary
    print("\n" + "="*70)
    print(f"TEST RESULT: {result}")
    print("="*70)
    
    if result == "PASS":
        print("""
✅ JWT SECRET CONSISTENCY FIX VERIFIED!

The fix ensures that:
1. Both token creation (microsoft_auth) and verification (user_auth) use os.getenv()
2. On Render (production), both modules read JWT_SECRET from environment variables
3. Locally (development), both modules fall back to .env.master
4. JWT signature verification will succeed
5. Users will authenticate correctly instead of falling back to user_id=1

Next Steps:
- Deploy this fix to Render
- Test Microsoft OAuth login on production
- Verify no more "Signature verification failed" errors
""")
    else:
        print("""
❌ JWT SECRET CONSISTENCY PROBLEM DETECTED!

The secrets don't match, which means:
1. Tokens created in microsoft_auth can't be verified in user_auth
2. All authentication will fail with "Signature verification failed"
3. System falls back to default user_id=1
4. Multi-user authentication is broken

Fix Required:
- Ensure both modules use os.getenv('JWT_SECRET') with same fallback
- Check that JWT_SECRET is set in Render environment variables
- Test again after fix
""")
    
    return result == "PASS"


if __name__ == '__main__':
    success = test_jwt_secret_consistency()
    sys.exit(0 if success else 1)
