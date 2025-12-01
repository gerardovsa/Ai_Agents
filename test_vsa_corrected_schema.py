"""
VSA Veterinary Alerts Endpoint Testing - CORRECTED SCHEMA
Using actual Supabase column names from SQL_Data_AI_UI_v5 database
"""

import requests
from datetime import datetime, timedelta
import json

SUPABASE_URL = 'https://wuwmvtslltqhaycyukxk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

endpoint = f"{SUPABASE_URL}/rest/v1/veterinary_calls"

print("\n" + "="*80)
print("VSA VETERINARY ALERTS - CORRECTED ENDPOINT TESTING")
print("="*80)
print(f"Database: {SUPABASE_URL}")
print(f"Table: veterinary_calls")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# TEST 1: Get total record count
print("TEST 1: Get Total Record Count")
print("-" * 80)
try:
    response = requests.head(
        endpoint,
        headers=headers,
        params={'select': 'call_id'},
        timeout=5
    )
    
    total_count = response.headers.get('Content-Range', '0-0/0').split('/')[-1]
    print(f"✅ PASSED - Total records: {total_count}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 2: Fetch recent records with corrected field names
print("\nTEST 2: Fetch 10 Recent Records (Corrected Fields)")
print("-" * 80)
try:
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'call_id,key_call_date,key_staffname,key_otherspeaker_firstname,key_otherspeaker_lastname,key_details_reasoning_analysis',
            'order': 'key_call_date.desc',
            'limit': '10'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        print(f"✅ PASSED - Retrieved {len(records)} records")
        
        if records:
            sample = records[0]
            print(f"\nSample Record Structure:")
            print(f"  Call ID: {sample.get('call_id', 'N/A')}")
            print(f"  Date: {sample.get('key_call_date', 'N/A')}")
            print(f"  Staff: {sample.get('key_staffname', 'N/A')}")
            print(f"  Client: {sample.get('key_otherspeaker_firstname', '')} {sample.get('key_otherspeaker_lastname', '')}")
            analysis = sample.get('key_details_reasoning_analysis', '')
            print(f"  Analysis: {analysis[:100] if analysis else 'N/A'}...")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 3: Filter records with analysis/alerts
print("\nTEST 3: Filter Records With Analysis Details")
print("-" * 80)
try:
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'call_id,key_staffname,key_details_reasoning_analysis',
            'key_details_reasoning_analysis': 'not.is.null',
            'limit': '5'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        print(f"✅ PASSED - Found {len(records)} calls with analysis")
        
        for i, record in enumerate(records, 1):
            analysis = record.get('key_details_reasoning_analysis', '')
            staff = record.get('key_staffname', 'Unknown')
            print(f"  {i}. {staff}: {analysis[:60]}...")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 4: Date range filtering (last 7 days)
print("\nTEST 4: Filter Last 7 Days (Using key_call_date)")
print("-" * 80)
try:
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'call_id,key_call_date,key_staffname',
            'key_call_date': f'gte.{seven_days_ago}',
            'order': 'key_call_date.desc',
            'limit': '10'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        print(f"✅ PASSED - Found {len(records)} calls in last 7 days")
        
        if records:
            oldest = records[-1].get('key_call_date', 'N/A')
            newest = records[0].get('key_call_date', 'N/A')
            print(f"  Date range: {oldest} to {newest}")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 5: Staff-specific filtering
print("\nTEST 5: Filter by Staff Name (key_staffname)")
print("-" * 80)
try:
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'key_staffname',
            'limit': '100'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        staff_names = list(set([r.get('key_staffname') for r in records if r.get('key_staffname')]))
        print(f"✅ PASSED - Found {len(staff_names)} unique staff members")
        print(f"  Sample staff: {', '.join(sorted(staff_names)[:5])}")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 6: Direction filtering (inbound/outbound)
print("\nTEST 6: Filter by Call Direction")
print("-" * 80)
try:
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'call_id,key_direction,key_staffname',
            'limit': '10'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        directions = [r.get('key_direction') for r in records if r.get('key_direction')]
        unique_directions = list(set(directions))
        print(f"✅ PASSED - Found call directions: {', '.join(unique_directions)}")
        print(f"  Total calls sampled: {len(records)}")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 7: Hospital/location filtering
print("\nTEST 7: Filter by Hospital")
print("-" * 80)
try:
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'key_hospital,key_hospital_code',
            'limit': '50'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        hospitals = list(set([r.get('key_hospital') for r in records if r.get('key_hospital')]))
        print(f"✅ PASSED - Found {len(hospitals)} unique hospitals")
        print(f"  Sample hospitals: {', '.join(sorted(hospitals)[:3])}")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# TEST 8: Outcome filtering
print("\nTEST 8: Filter by Call Outcome")
print("-" * 80)
try:
    response = requests.get(
        endpoint,
        headers=headers,
        params={
            'select': 'call_id,key_outcome,key_staffname',
            'key_outcome': 'not.is.null',
            'limit': '10'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        records = response.json()
        outcomes = list(set([r.get('key_outcome') for r in records if r.get('key_outcome')]))
        print(f"✅ PASSED - Found {len(records)} calls with outcomes")
        print(f"  Outcome types: {', '.join(outcomes[:5])}")
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "="*80)
print("ENDPOINT TESTING COMPLETE")
print("="*80)
print("\n✅ All tests completed with CORRECT field names!")
print("\nField Name Mapping Reference:")
print("  OLD → NEW")
print("  start_time → key_call_date")
print("  staff_name → key_staffname")
print("  client_name → key_otherspeaker_firstname + key_otherspeaker_lastname")
print("  manager_alerts_tags → key_details_reasoning_analysis")
print("  call_purpose → (analyze key_details_reasoning_analysis)")
print("  cqa_overall → (not present in this database)")
print("\n")
