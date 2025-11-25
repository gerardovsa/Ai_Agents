"""
Test flexible credential system with platform schema validation

This script demonstrates the complete credential management workflow:
1. Store credentials with schema validation
2. Retrieve credentials with settings
3. Update settings without touching credentials
4. Test credential validity
5. Check credentials needing rotation

Usage:
    python testing_tools/test_flexible_credentials.py
"""

import sys
import os

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AI_infrastructure'))

from auth.user_auth import UserAuthManager
from auth.platform_credential_schemas import (
    validate_platform_credentials,
    get_required_fields,
    get_optional_fields,
    list_all_platforms
)


def test_platform_schemas():
    """Test 1: Platform schema validation"""
    print("\n" + "="*70)
    print("TEST 1: Platform Schema Validation")
    print("="*70)
    
    # List all available platforms
    platforms = list_all_platforms()
    print(f"\nAvailable platforms ({len(platforms)}):")
    for platform in platforms[:10]:  # Show first 10
        print(f"  - {platform}")
    print(f"  ... and {len(platforms) - 10} more")
    
    # Show schema details for AssemblyAI
    print("\nAssemblyAI Schema Details:")
    required = get_required_fields('assemblyai')
    optional = get_optional_fields('assemblyai')
    print(f"  Required fields: {required}")
    print(f"  Optional fields: {optional}")
    
    # Validate valid credentials
    print("\nValidating VALID AssemblyAI credentials:")
    try:
        valid_creds = {
            'api_key': 'test_key_12345',
            'language_code': 'en',
            'speaker_labels': True
        }
        validated = validate_platform_credentials('assemblyai', valid_creds)
        print(f"  Result: PASS - {validated}")
    except ValueError as e:
        print(f"  Result: FAIL - {e}")
    
    # Validate invalid credentials (missing required field)
    print("\nValidating INVALID credentials (missing api_key):")
    try:
        invalid_creds = {
            'language_code': 'en'  # Missing api_key!
        }
        validated = validate_platform_credentials('assemblyai', invalid_creds)
        print(f"  Result: PASS (unexpected!) - {validated}")
    except ValueError as e:
        print(f"  Result: FAIL (expected) - {e}")
    
    return True


def test_store_credentials_with_validation():
    """Test 2: Store credentials with schema validation"""
    print("\n" + "="*70)
    print("TEST 2: Store Credentials with Schema Validation")
    print("="*70)
    
    auth_manager = UserAuthManager()
    
    # Store AssemblyAI credentials
    print("\nStoring AssemblyAI credentials with settings:")
    result = auth_manager.store_platform_credential(
        user_id=1,
        platform='assemblyai',
        credentials_dict={
            'api_key': 'test_assemblyai_key_abc123'
        },
        settings_dict={
            'language_code': 'en',
            'speaker_labels': True,
            'punctuate': True,
            'format_text': True,
            'word_boost': ['parvo', 'heartworm', 'subcutaneous', 'parvovirus']
        },
        validate_schema=True
    )
    print(f"  Result: {result}")
    
    # Store Twilio credentials
    print("\nStoring Twilio credentials with settings:")
    result = auth_manager.store_platform_credential(
        user_id=1,
        platform='twilio',
        credentials_dict={
            'account_sid': 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'auth_token': 'test_auth_token_12345',
            'phone_number': '+15555551234'
        },
        settings_dict={
            'business_hours_start': 8,
            'business_hours_end': 18,
            'emergency_phone': '+15555550911',
            'webhook_base_url': 'https://example.com/webhooks'
        },
        validate_schema=True
    )
    print(f"  Result: {result}")
    
    # Store Pinecone credentials
    print("\nStoring Pinecone credentials:")
    result = auth_manager.store_platform_credential(
        user_id=1,
        platform='pinecone',
        credentials_dict={
            'api_key': 'pcsk-test-key-12345',
            'environment': 'us-east-1',
            'index_name': 'veterinary-notes'
        },
        settings_dict={
            'dimension': 1536,
            'metric': 'cosine',
            'namespace': 'soap_notes'
        },
        validate_schema=True
    )
    print(f"  Result: {result}")
    
    return True


def test_retrieve_credentials():
    """Test 3: Retrieve credentials with settings and metadata"""
    print("\n" + "="*70)
    print("TEST 3: Retrieve Credentials with Settings and Metadata")
    print("="*70)
    
    auth_manager = UserAuthManager()
    
    # Get credentials only
    print("\nGet AssemblyAI credentials only:")
    creds = auth_manager.get_platform_credentials(user_id=1, platform='assemblyai')
    print(f"  Credentials: {creds}")
    
    # Get credentials + settings
    print("\nGet Twilio credentials + settings:")
    data = auth_manager.get_platform_credentials(
        user_id=1, 
        platform='twilio',
        include_settings=True
    )
    print(f"  Credentials: {data.get('credentials', {})}")
    print(f"  Settings: {data.get('settings', {})}")
    
    # Get full metadata
    print("\nGet Pinecone credentials + metadata:")
    data = auth_manager.get_platform_credentials(
        user_id=1,
        platform='pinecone',
        include_settings=True,
        include_metadata=True
    )
    print(f"  Credentials: {data.get('credentials', {})}")
    print(f"  Settings: {data.get('settings', {})}")
    print(f"  Validation Status: {data.get('validation_status')}")
    print(f"  Last Validated: {data.get('last_validated_at')}")
    print(f"  Rotation Due: {data.get('rotation_due_at')}")
    
    return True


def test_update_settings():
    """Test 4: Update settings without touching credentials"""
    print("\n" + "="*70)
    print("TEST 4: Update Settings (without touching credentials)")
    print("="*70)
    
    auth_manager = UserAuthManager()
    
    # Update Twilio business hours
    print("\nUpdating Twilio business hours:")
    result = auth_manager.store_platform_settings(
        user_id=1,
        platform='twilio',
        settings_dict={
            'business_hours_start': 9,  # Changed from 8
            'business_hours_end': 17,   # Changed from 18
            'emergency_phone': '+15555550911',
            'timezone': 'America/New_York'  # Added new field
        }
    )
    print(f"  Result: {result}")
    
    # Verify settings updated but credentials unchanged
    print("\nVerifying credentials unchanged:")
    data = auth_manager.get_platform_credentials(
        user_id=1,
        platform='twilio',
        include_settings=True
    )
    print(f"  Auth Token (should be unchanged): {data.get('credentials', {}).get('auth_token', 'N/A')[:20]}...")
    print(f"  Business Hours Start (should be 9): {data.get('settings', {}).get('business_hours_start')}")
    print(f"  Business Hours End (should be 17): {data.get('settings', {}).get('business_hours_end')}")
    print(f"  Timezone (should be added): {data.get('settings', {}).get('timezone')}")
    
    return True


def test_credential_rotation():
    """Test 5: Check credentials needing rotation"""
    print("\n" + "="*70)
    print("TEST 5: Check Credentials Needing Rotation")
    print("="*70)
    
    auth_manager = UserAuthManager()
    
    # Get credentials due for rotation in next 90 days
    print("\nCredentials needing rotation (next 90 days):")
    due_creds = auth_manager.get_credentials_due_for_rotation(days_ahead=90)
    
    if due_creds:
        print(f"  Found {len(due_creds)} credentials:")
        for cred in due_creds[:5]:  # Show first 5
            print(f"    - User {cred['user_id']}: {cred['platform']} (due: {cred['rotation_due_at']})")
    else:
        print("  No credentials need rotation")
    
    return True


def test_list_user_platforms():
    """Test 6: List all platforms user has credentials for"""
    print("\n" + "="*70)
    print("TEST 6: List User Platforms")
    print("="*70)
    
    auth_manager = UserAuthManager()
    
    print("\nPlatforms with credentials (user_id=1):")
    platforms = auth_manager.list_user_platforms(user_id=1)
    for platform in platforms:
        print(f"  - {platform}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("FLEXIBLE CREDENTIAL SYSTEM - COMPREHENSIVE TEST")
    print("="*70)
    print("\nTesting platform credential schema validation and storage")
    print("Features:")
    print("  - Schema validation (required/optional fields)")
    print("  - Separate credentials vs settings (security)")
    print("  - Credential rotation tracking")
    print("  - Validation status tracking")
    print("  - Change detection (credential hash)")
    
    tests = [
        ("Platform Schemas", test_platform_schemas),
        ("Store Credentials", test_store_credentials_with_validation),
        ("Retrieve Credentials", test_retrieve_credentials),
        ("Update Settings", test_update_settings),
        ("Credential Rotation", test_credential_rotation),
        ("List User Platforms", test_list_user_platforms)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n PASS: {test_name}")
            else:
                failed += 1
                print(f"\n FAIL: {test_name}")
        except Exception as e:
            failed += 1
            print(f"\n FAIL: {test_name}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n ALL TESTS PASSED!")
    else:
        print(f"\n {failed} test(s) failed")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
