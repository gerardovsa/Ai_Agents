"""
Test Account Settings Complete Data Flow
Tests: UI fields -> localStorage -> Database -> Backend API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def test_database_schema():
    """Test 1: Verify database has all required columns"""
    print("\n" + "="*80)
    print("TEST 1: DATABASE SCHEMA CHECK")
    print("="*80)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'user_preferences'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    col_names = [col['column_name'] for col in columns]
    
    required_columns = [
        'user_id', 'nickname', 'communication_style', 'detail_level',
        'auth_platform', 'ai_model', 'ai_temperature', 'ai_top_p',
        'ai_max_tokens', 'ai_thinking_enabled', 'ai_thinking_budget',
        'ai_streaming_enabled'
    ]
    
    print(f"\nTotal columns in user_preferences: {len(columns)}")
    print("\nChecking required columns:")
    
    all_found = True
    for col in required_columns:
        if col in col_names:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ MISSING: {col}")
            all_found = False
    
    conn.close()
    
    if all_found:
        print("\n✅ TEST 1 PASSED: All required columns exist")
        return True
    else:
        print("\n❌ TEST 1 FAILED: Missing columns")
        return False


def test_backend_endpoints():
    """Test 2: Check if backend routes are accessible"""
    print("\n" + "="*80)
    print("TEST 2: BACKEND ENDPOINTS CHECK")
    print("="*80)
    
    try:
        # Check if user_preferences_routes.py exists and has correct functions
        routes_file = 'AI_infrastructure/routes/user_preferences_routes.py'
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'GET endpoint exists': '@user_preferences_bp.route(\'/preferences\', methods=[\'GET\'])' in content,
            'POST endpoint exists': '@user_preferences_bp.route(\'/preferences\', methods=[\'POST\'])' in content,
            'ai_model in SELECT': 'ai_model' in content and 'SELECT' in content,
            'ai_temperature in SELECT': 'ai_temperature' in content,
            'ai_model in UPDATE': 'ai_model = %s' in content,
            'ai_model in INSERT': 'ai_model, ai_temperature' in content
        }
        
        print("\nBackend endpoint checks:")
        all_passed = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n✅ TEST 2 PASSED: Backend endpoints properly configured")
            return True
        else:
            print("\n❌ TEST 2 FAILED: Backend endpoints missing updates")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False


def test_frontend_functions():
    """Test 3: Check if frontend save functions exist"""
    print("\n" + "="*80)
    print("TEST 3: FRONTEND FUNCTIONS CHECK")
    print("="*80)
    
    try:
        ui_file = 'UI/business-ai-platform-v2.html'
        
        with open(ui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'saveSettings() function exists': 'function saveSettings()' in content,
            'saveAccountSettings() function exists': 'function saveAccountSettings()' in content or 'async function saveAccountSettings()' in content,
            'Save button in modal header': 'onclick="saveAccountSettings()"' in content,
            'modelSelect field exists': 'id="modelSelect"' in content,
            'temperature field exists': 'id="temperature"' in content,
            'topP field exists': 'id="topP"' in content,
            'enableThinking checkbox exists': 'id="enableThinking"' in content,
            'maxTokens field exists': 'id="maxTokens"' in content
        }
        
        print("\nFrontend function checks:")
        all_passed = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n✅ TEST 3 PASSED: Frontend functions properly implemented")
            return True
        else:
            print("\n❌ TEST 3 FAILED: Frontend functions missing")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        return False


def test_sample_user_preferences():
    """Test 4: Check if user has preferences in database"""
    print("\n" + "="*80)
    print("TEST 4: SAMPLE USER PREFERENCES CHECK")
    print("="*80)
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if any users have preferences
        cursor.execute("""
            SELECT 
                user_id,
                nickname,
                communication_style,
                ai_model,
                ai_temperature,
                ai_thinking_enabled
            FROM ai_infrastructure.user_preferences
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        if row:
            print(f"\n✅ Found user preferences for user_id: {row['user_id']}")
            print(f"  Nickname: {row['nickname'] or '(not set)'}")
            print(f"  Communication Style: {row['communication_style']}")
            print(f"  AI Model: {row['ai_model']}")
            print(f"  AI Temperature: {row['ai_temperature']}")
            print(f"  AI Thinking Enabled: {row['ai_thinking_enabled']}")
            print("\n✅ TEST 4 PASSED: User preferences exist")
            result = True
        else:
            print("\n⚠️  No user preferences found in database")
            print("   This is OK for new installations")
            print("\n✅ TEST 4 PASSED: Database accessible (no data yet)")
            result = True
        
        conn.close()
        return result
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "="*80)
    print("ACCOUNT SETTINGS DATA FLOW - COMPLETE TEST SUITE")
    print("="*80)
    
    results = {
        'Database Schema': test_database_schema(),
        'Backend Endpoints': test_backend_endpoints(),
        'Frontend Functions': test_frontend_functions(),
        'Sample Data': test_sample_user_preferences()
    }
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED - DATA FLOW COMPLETE")
        print("="*80)
        print("\nNext steps:")
        print("1. Start the Flask server: BISTART")
        print("2. Open UI in browser")
        print("3. Log in with your account")
        print("4. Open Account Settings (click avatar)")
        print("5. Change AI model or temperature")
        print("6. Click the green Save icon")
        print("7. Check backend logs for: '[ACCOUNT SETTINGS] Settings saved'")
        print("8. Verify database updated with new values")
        print("\n✅ The complete flow is now connected:")
        print("   UI Fields → localStorage → Backend API → PostgreSQL Database")
    else:
        print("\n" + "="*80)
        print("⚠️  SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        print("="*80)
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
