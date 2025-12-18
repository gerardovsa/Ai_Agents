"""
Test Auto Database Entry with Computer Use
==========================================

Tests automated data entry using:
1. Computer Use API for web form automation
2. Direct PostgreSQL insertion
3. Batch processing

REQUIREMENTS:
- Docker Desktop running
- Anthropic API key in environment
- PostgreSQL database accessible

RUN:
    python test_auto_database_entry.py

CREATED: December 18, 2025
"""

import asyncio
import sys
import os
from pathlib import Path

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools' / 'implementations'))

from auto_database_entry import (
    auto_enter_verification_results,
    auto_enter_to_postgres,
    batch_enter_verifications
)


async def test_postgres_direct_insert():
    """Test direct PostgreSQL insertion"""
    print("\n" + "="*80)
    print("TEST 1: Direct PostgreSQL Insertion")
    print("="*80)
    
    verification_data = {
        'full_name': 'Gregory Dutton',
        'company_name': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'domain': 'isb.eco',
        'legitimacy_score': 42.3,
        'verification_status': 'UNCERTAIN',
        'domain_authority': 27,
        'web_archive_snapshots': 27,
        'ssl_certificates': 27,
        'web_traffic_score': 0.0,
        'requires_manual_review': True,
        'verification_date': '2025-12-18',
        'notes': 'Low legitimacy score - ISB domain has history but traffic is low'
    }
    
    print("\n📊 Data to insert:")
    for key, value in verification_data.items():
        print(f"   {key}: {value}")
    
    # Note: This will fail if table doesn't exist - that's expected
    print("\n🔍 Attempting PostgreSQL insert...")
    print("   (Will fail if 'verified_professionals' table doesn't exist - create it first)")
    
    result = await auto_enter_to_postgres(
        verification_data=verification_data,
        table_name='verified_professionals',
        schema_name='verification'
    )
    
    print(f"\n📊 Result:")
    print(f"   Success: {result['success']}")
    print(f"   Records created: {result.get('records_created', 0)}")
    if result['success']:
        print(f"   Insert ID: {result.get('insert_id')}")
        print(f"   Table: {result.get('table')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    return result


async def test_computer_use_form_fill():
    """Test Computer Use automation for web form"""
    print("\n" + "="*80)
    print("TEST 2: Computer Use Form Automation")
    print("="*80)
    
    verification_data = {
        'name': 'Gregory Dutton',
        'company': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'legitimacy_score': 42.3,
        'status': 'UNCERTAIN',
        'notes': 'Requires video call verification'
    }
    
    print("\n📊 Data to enter:")
    for key, value in verification_data.items():
        print(f"   {key}: {value}")
    
    print("\n🤖 Starting Computer Use automation...")
    print("   Claude will:")
    print("   1. Start browser in Docker container")
    print("   2. Navigate to target URL")
    print("   3. Find and fill form fields")
    print("   4. Submit the form")
    print("   5. Capture before/after screenshots")
    
    # Example: Fill a Google Form (you can change this to your CRM)
    result = await auto_enter_verification_results(
        verification_data=verification_data,
        target_system='custom',
        target_url='https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform',
        form_fields={
            'entry.123456789': 'name',  # Replace with actual form field IDs
            'entry.987654321': 'company',
            'entry.111222333': 'email',
            'entry.444555666': 'legitimacy_score',
            'entry.777888999': 'status',
            'entry.000111222': 'notes'
        }
    )
    
    print(f"\n📊 Result:")
    print(f"   Success: {result['success']}")
    print(f"   Records created: {result.get('records_created', 0)}")
    print(f"   Execution time: {result.get('execution_time', 0):.2f}s")
    
    if result['success']:
        print(f"\n✅ Actions taken:")
        for action in result.get('actions_taken', []):
            print(f"      {action}")
        
        print(f"\n📸 Screenshots captured:")
        print(f"   Before: {len(result.get('screenshot_before', ''))} chars")
        print(f"   After: {len(result.get('screenshot_after', ''))} chars")
        
        if result.get('ai_response'):
            print(f"\n🤖 Claude says:")
            print(f"   {result['ai_response']}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    return result


async def test_batch_processing():
    """Test batch processing multiple records"""
    print("\n" + "="*80)
    print("TEST 3: Batch Processing")
    print("="*80)
    
    verification_list = [
        {
            'name': 'Gregory Dutton',
            'company': 'ISB',
            'email': 'gregory.dutton@isb.eco',
            'score': 42.3,
            'status': 'UNCERTAIN'
        },
        {
            'name': 'Test Person',
            'company': 'SCA Technology',
            'email': 'test@scatechnology.ai',
            'score': 0.0,
            'status': 'SUSPICIOUS'
        }
    ]
    
    print(f"\n📊 Processing {len(verification_list)} records:")
    for idx, data in enumerate(verification_list):
        print(f"\n   Record {idx+1}:")
        for key, value in data.items():
            print(f"      {key}: {value}")
    
    print("\n🤖 Starting batch automation...")
    
    result = await batch_enter_verifications(
        verification_list=verification_list,
        target_system='custom',
        target_url='https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform',
        form_fields={
            'entry.123456789': 'name',
            'entry.987654321': 'company',
            'entry.111222333': 'email',
            'entry.444555666': 'score',
            'entry.777888999': 'status'
        }
    )
    
    print(f"\n📊 Batch Result:")
    print(f"   Success: {result['success']}")
    print(f"   Total records: {result['total_records']}")
    print(f"   Records created: {result['records_created']}")
    print(f"   Records failed: {result['records_failed']}")
    print(f"   Execution time: {result['execution_time']:.2f}s")
    
    if result.get('results'):
        print(f"\n📋 Individual Results:")
        for idx, res in enumerate(result['results']):
            print(f"\n   Record {idx+1}:")
            print(f"      Success: {res['success']}")
            if res['success']:
                print(f"      Records created: {res['records_created']}")
            else:
                print(f"      Error: {res.get('error')}")
    
    return result


async def demo_real_world_scenario():
    """Demo: Complete verification workflow with automatic database entry"""
    print("\n" + "="*80)
    print("DEMO: Complete Verification → Database Entry Workflow")
    print("="*80)
    
    print("\n📋 SCENARIO:")
    print("   Gregory Dutton from ISB requests access")
    print("   1. Run verification")
    print("   2. Get legitimacy score: 42.3/100")
    print("   3. Automatically enter into CRM")
    print("   4. Flag for manual review")
    
    # Step 1: Verification data (from previous tests)
    verification_data = {
        'full_name': 'Gregory Dutton',
        'company_name': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'domain': 'isb.eco',
        'phone': '+61 461 357 358',
        'legitimacy_score': 42.3,
        'verification_status': 'UNCERTAIN',
        'domain_authority': 27,
        'historical_presence': 100.0,
        'web_traffic': 0.0,
        'web_archive_snapshots': 27,
        'ssl_certificates': 27,
        'backlinks_found': 0,
        'government_sources': 4,
        'requires_manual_review': True,
        'recommended_action': 'Video call verification + employment confirmation',
        'risk_level': 'MEDIUM',
        'verification_date': '2025-12-18T10:30:00Z',
        'ai_analysis': 'Domain has history but low traffic. Manual verification required.',
        'notes': 'ISB legitimacy uncertain. 27 historical snapshots indicate established presence but zero web traffic is concerning.'
    }
    
    print("\n✅ Step 1: Verification Complete")
    print(f"   Legitimacy Score: {verification_data['legitimacy_score']}/100")
    print(f"   Status: {verification_data['verification_status']}")
    print(f"   Risk Level: {verification_data['risk_level']}")
    
    # Step 2: Enter into PostgreSQL
    print("\n✅ Step 2: Entering into PostgreSQL...")
    db_result = await auto_enter_to_postgres(
        verification_data=verification_data,
        table_name='verified_professionals',
        schema_name='verification'
    )
    
    if db_result['success']:
        print(f"   ✅ Database record created (ID: {db_result.get('insert_id')})")
    else:
        print(f"   ⚠️ Database entry skipped: {db_result.get('error')}")
    
    # Step 3: Enter into CRM (Computer Use)
    print("\n✅ Step 3: Entering into CRM via Computer Use...")
    print("   (This would actually fill your CRM form)")
    
    # Uncomment to actually run Computer Use:
    # crm_result = await auto_enter_verification_results(
    #     verification_data={
    #         'name': verification_data['full_name'],
    #         'company': verification_data['company_name'],
    #         'email': verification_data['email'],
    #         'score': verification_data['legitimacy_score'],
    #         'status': verification_data['verification_status']
    #     },
    #     target_system='crm',
    #     target_url='https://your-crm.com/contacts/new',
    #     form_fields={'full_name': 'name', 'company': 'company', 'email': 'email'}
    # )
    
    print("   ⚠️ Computer Use skipped in demo (enable by uncommenting)")
    
    print("\n✅ Step 4: Workflow Complete")
    print("   ✅ Verification analyzed")
    print(f"   ✅ Database record created: {db_result['success']}")
    print("   ⚠️ Manual review required (flagged in system)")
    
    print("\n🎯 NEXT ACTIONS:")
    print("   1. Video call with Gregory Dutton")
    print("   2. Verify Australian ID")
    print("   3. Call ISB main office for employment confirmation")
    print("   4. Check LinkedIn profile for consistency")
    print("   5. Update database with final decision")


async def main():
    """Run all tests"""
    print("="*80)
    print("AUTO DATABASE ENTRY TEST SUITE")
    print("Testing Computer Use + PostgreSQL automation")
    print("="*80)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    # Check Anthropic API key
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_key:
        print("   ✅ Anthropic API key found")
    else:
        print("   ⚠️ Anthropic API key not found (Computer Use will not work)")
    
    # Check Docker
    try:
        import docker
        client = docker.from_env()
        print("   ✅ Docker is available")
    except Exception as e:
        print(f"   ⚠️ Docker not available: {e}")
    
    # Run tests
    try:
        # Test 1: Direct PostgreSQL (will likely fail if table doesn't exist)
        await test_postgres_direct_insert()
        
        # Test 2: Computer Use (requires Docker + Anthropic API)
        # await test_computer_use_form_fill()  # Uncomment to test
        
        # Test 3: Batch processing
        # await test_batch_processing()  # Uncomment to test
        
        # Demo: Complete workflow
        await demo_real_world_scenario()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
    print("\nNOTE: Computer Use tests are commented out by default.")
    print("Uncomment them in main() to test actual browser automation.")
    print("\nTo create the PostgreSQL table:")
    print("""
    CREATE SCHEMA IF NOT EXISTS verification;
    
    CREATE TABLE IF NOT EXISTS verification.verified_professionals (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255),
        company_name VARCHAR(255),
        email VARCHAR(255),
        domain VARCHAR(255),
        phone VARCHAR(50),
        legitimacy_score DECIMAL(5,2),
        verification_status VARCHAR(50),
        domain_authority INT,
        historical_presence DECIMAL(5,2),
        web_traffic DECIMAL(5,2),
        web_archive_snapshots INT,
        ssl_certificates INT,
        backlinks_found INT,
        government_sources INT,
        requires_manual_review BOOLEAN,
        recommended_action TEXT,
        risk_level VARCHAR(50),
        verification_date TIMESTAMP,
        ai_analysis TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)


if __name__ == '__main__':
    asyncio.run(main())
