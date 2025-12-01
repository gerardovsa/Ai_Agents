"""
Direct Supabase API Test for VSA Veterinary Alerts
Tests the actual REST API endpoint using requests library
"""

import requests
import json
from datetime import datetime, timedelta

# Credentials from vsa-veterinary-alerts.js
SUPABASE_URL = 'https://wuwmvtslltqhaycyukxk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4'

def test_veterinary_calls_endpoint():
    """Test the veterinary_calls table endpoint"""
    
    print("\n" + "=" * 80)
    print("VSA VETERINARY ALERTS - DIRECT SUPABASE API TEST")
    print("=" * 80)
    print(f"URL: {SUPABASE_URL}")
    print(f"Table: veterinary_calls")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/veterinary_calls"
    
    # TEST 1: Get total count
    print("TEST 1: Get Total Record Count")
    print("-" * 80)
    try:
        response = requests.head(endpoint, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_range = response.headers.get('content-range', 'unknown')
            print(f"✅ SUCCESS - Content-Range: {content_range}")
            if '/' in content_range:
                total = content_range.split('/')[-1]
                print(f"✅ Total Records: {total}")
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
    
    # TEST 2: Fetch 5 recent records
    print("TEST 2: Fetch 5 Recent Records")
    print("-" * 80)
    try:
        params = {
            'select': 'call_id,call_date,caller_name,staff_name,call_purpose',
            'order': 'call_date.desc',
            'limit': '5'
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Fetched {len(data)} records\n")
            
            for i, record in enumerate(data, 1):
                print(f"  Record {i}:")
                print(f"    Call ID: {record.get('call_id', 'N/A')}")
                print(f"    Date: {record.get('call_date', 'N/A')}")
                print(f"    Caller: {record.get('caller_name', 'N/A')}")
                print(f"    Staff: {record.get('staff_name', 'N/A')}")
                print(f"    Purpose: {record.get('call_purpose', 'N/A')}")
                print()
        else:
            print(f"❌ FAILED - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
    
    # TEST 3: Get records with alerts
    print("TEST 3: Filter Records with Manager Alerts")
    print("-" * 80)
    try:
        params = {
            'select': 'call_id,caller_name,manager_alerts_tags',
            'manager_alerts_tags': 'not.is.null',
            'manager_alerts_tags': 'neq.',
            'order': 'call_date.desc',
            'limit': '3'
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Found {len(data)} records with alerts\n")
            
            for i, record in enumerate(data, 1):
                print(f"  Alert Record {i}:")
                print(f"    Call ID: {record.get('call_id', 'N/A')}")
                print(f"    Caller: {record.get('caller_name', 'N/A')}")
                alerts = record.get('manager_alerts_tags', '')
                if alerts:
                    lines = [l.strip() for l in alerts.split('\n') if l.strip()]
                    print(f"    Alerts ({len(lines)} total):")
                    for line in lines[:2]:
                        print(f"      - {line}")
                print()
        else:
            print(f"❌ FAILED - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
    
    # TEST 4: Date range filter
    print("TEST 4: Filter Last 7 Days")
    print("-" * 80)
    try:
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'select': 'count',
            'call_date': f'gte.{week_ago}'
        }
        
        response = requests.head(endpoint, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_range = response.headers.get('content-range', '0')
            if '/' in content_range:
                count = content_range.split('/')[-1]
                print(f"✅ SUCCESS - Records in last 7 days: {count}")
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
    
    # TEST 5: Verify all required fields
    print("TEST 5: Verify Required Fields Schema")
    print("-" * 80)
    
    required_fields = [
        'call_id', 'call_date', 'caller_name', 'staff_name',
        'call_purpose', 'manager_alerts_tags', 'cqa_overall',
        'sentiment_label', 'follow_up_needed'
    ]
    
    try:
        params = {
            'select': ','.join(required_fields),
            'limit': '1'
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                record = data[0]
                print(f"✅ SUCCESS - Schema validation\n")
                
                for field in required_fields:
                    value = record.get(field)
                    has_value = value is not None and value != ''
                    status = "✅" if has_value else "⚠️ (null)"
                    print(f"  {status} {field:25} Type: {type(value).__name__:10} Value: {str(value)[:40]}")
        else:
            print(f"❌ FAILED - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    test_veterinary_calls_endpoint()
