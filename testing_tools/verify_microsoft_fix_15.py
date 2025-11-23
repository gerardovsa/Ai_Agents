"""
Verify Fix #15: Microsoft Platform Migration
Quick verification that Microsoft authentication is working
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path
from datetime import datetime

def main():
    """Verify Microsoft authentication status"""
    
    print("=" * 70)
    print("MICROSOFT AUTHENTICATION STATUS - Fix #15 Verification")
    print("=" * 70)
    
    # Connect to database
    db_path = Path(__file__).parent.parent / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check platform distribution
    cursor.execute('SELECT platform, COUNT(*) FROM oauth_tokens GROUP BY platform')
    platforms = cursor.fetchall()
    
    print("\n📊 Token Distribution:")
    for platform, count in platforms:
        print(f"  {platform}: {count} tokens")
    
    # Verify no microsoft365 tokens exist
    sql, params = convert_sql_placeholders('SELECT COUNT(*) FROM oauth_tokens WHERE platform = ?', ('microsoft365',))

    cursor.execute(sql, params)
    old_count = cursor.fetchone()[0]
    
    if old_count == 0:
        print("\n✅ No deprecated 'microsoft365' tokens found")
    else:
        print(f"\n⚠️ WARNING: {old_count} 'microsoft365' tokens still exist!")
    
    # Check Microsoft tokens
    sql, params = convert_sql_placeholders('''
        SELECT user_id, account_name, account_identifier, expires_at, is_valid, refresh_token
        FROM oauth_tokens 
        WHERE platform = ?
    ''', ('microsoft',))

    cursor.execute(sql, params)
    
    tokens = cursor.fetchall()
    
    if not tokens:
        print("\n❌ No Microsoft tokens found!")
        conn.close()
        return
    
    print(f"\n🔐 Microsoft Tokens ({len(tokens)} total):")
    
    active_count = 0
    expired_count = 0
    
    for user_id, account_name, account_identifier, expires_at, is_valid, refresh_token in tokens:
        account = account_name or account_identifier or f"User {user_id}"
        
        print(f"\n  User {user_id}: {account}")
        print(f"    Expires: {expires_at}")
        
        # Check expiration
        exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        now_dt = datetime.now()
        expired = now_dt > exp_dt
        
        if expired:
            status = "⚠️ EXPIRED"
            expired_count += 1
        else:
            status = "✅ ACTIVE"
            active_count += 1
        
        print(f"    Status: {status}")
        print(f"    Valid: {'✅ Yes' if is_valid else '❌ No'}")
        print(f"    Has Refresh Token: {'✅ Yes' if refresh_token else '❌ No'}")
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    checks = []
    
    # Check 1: No microsoft365 tokens
    if old_count == 0:
        checks.append(("✅", "No deprecated 'microsoft365' tokens"))
    else:
        checks.append(("❌", f"{old_count} 'microsoft365' tokens still exist"))
    
    # Check 2: At least one Microsoft token
    if len(tokens) > 0:
        checks.append(("✅", f"{len(tokens)} Microsoft token(s) found"))
    else:
        checks.append(("❌", "No Microsoft tokens found"))
    
    # Check 3: Active tokens
    if active_count > 0:
        checks.append(("✅", f"{active_count} active token(s)"))
    else:
        checks.append(("⚠️", "No active tokens (all expired)"))
    
    # Check 4: Gerardo's account
    gerardo_found = any('minivetguide' in (t[1] or t[2] or '') for t in tokens)
    if gerardo_found:
        checks.append(("✅", "Gerardo's account token found"))
    else:
        checks.append(("❌", "Gerardo's account token NOT found"))
    
    for status, message in checks:
        print(f"{status} {message}")
    
    # Overall status
    all_passed = all(check[0] == "✅" for check in checks)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 Fix #15 COMPLETE - All Microsoft authentication working!")
    else:
        print("⚠️ Some issues detected - see summary above")
    print("=" * 70)

if __name__ == '__main__':
    main()
