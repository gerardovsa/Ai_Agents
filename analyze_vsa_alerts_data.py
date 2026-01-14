"""
Analyze VSA Veterinary Alerts Database
Query actual data to understand header display issue
"""

import os
import json
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*80)
print("VSA VETERINARY ALERTS - DATABASE ANALYSIS")
print("="*80 + "\n")

# Query 1: Check call_manager_alerts structure
print("📊 QUERY 1: Sample alerts from call_manager_alerts")
print("-" * 80)
try:
    alerts_response = supabase.table('call_manager_alerts').select('*').limit(3).execute()
    
    if alerts_response.data:
        print(f"✅ Found {len(alerts_response.data)} sample alerts\n")
        
        for i, alert in enumerate(alerts_response.data, 1):
            print(f"Alert #{i}:")
            print(f"  call_id: {alert.get('call_id')}")
            print(f"  alert_1_type: {alert.get('alert_1_type')}")
            print(f"  alert_1_severity: {alert.get('alert_1_severity')}")
            print(f"  alert_1_priority: {alert.get('alert_1_priority')}")
            print(f"  created_at: {alert.get('created_at')}")
            print()
    else:
        print("⚠️  No alerts found in call_manager_alerts table")
        
except Exception as e:
    print(f"❌ Error querying call_manager_alerts: {e}")

print("\n" + "="*80)

# Query 2: Check veterinary_calls structure (for staff/client/pet data)
print("📊 QUERY 2: Sample calls from veterinary_calls")
print("-" * 80)
try:
    calls_response = supabase.table('veterinary_calls').select('*').limit(3).execute()
    
    if calls_response.data:
        print(f"✅ Found {len(calls_response.data)} sample calls\n")
        
        for i, call in enumerate(calls_response.data, 1):
            print(f"Call #{i}:")
            print(f"  call_id: {call.get('call_id')}")
            print(f"  key_staffname: {call.get('key_staffname')}")
            print(f"  key_call_date: {call.get('key_call_date')}")
            print(f"  key_call_time: {call.get('key_call_time')}")
            print(f"  key_otherspeaker_firstname: {call.get('key_otherspeaker_firstname')}")
            print(f"  key_otherspeaker_lastname: {call.get('key_otherspeaker_lastname')}")
            print(f"  key_pet_petname: {call.get('key_pet_petname')}")
            print(f"  key_phonenumber: {call.get('key_phonenumber')}")
            print()
    else:
        print("⚠️  No calls found in veterinary_calls table")
        
except Exception as e:
    print(f"❌ Error querying veterinary_calls: {e}")

print("\n" + "="*80)

# Query 3: JOIN to see how alerts map to calls
print("📊 QUERY 3: Alerts with associated call data (JOIN)")
print("-" * 80)
try:
    # Get alerts with call_id
    alerts_response = supabase.table('call_manager_alerts').select('call_id').limit(5).execute()
    
    if alerts_response.data:
        call_ids = [alert['call_id'] for alert in alerts_response.data if alert.get('call_id')]
        
        if call_ids:
            # Get corresponding calls
            calls_response = supabase.table('veterinary_calls').select('*').in_('call_id', call_ids).execute()
            
            print(f"✅ Found {len(calls_response.data)} matching calls\n")
            
            for call in calls_response.data:
                print(f"Call ID: {call.get('call_id')}")
                print(f"  Staff: {call.get('key_staffname')}")
                print(f"  Date: {call.get('key_call_date')}")
                print(f"  Time: {call.get('key_call_time')}")
                print(f"  Client: {call.get('key_otherspeaker_firstname')} {call.get('key_otherspeaker_lastname')}")
                print(f"  Pet: {call.get('key_pet_petname')}")
                print(f"  Phone: {call.get('key_phonenumber')}")
                print()
        else:
            print("⚠️  No call_ids found in alerts")
    else:
        print("⚠️  No alerts found")
        
except Exception as e:
    print(f"❌ Error in JOIN query: {e}")

print("\n" + "="*80)

# Query 4: Check date formatting
print("📊 QUERY 4: Date/Time formatting analysis")
print("-" * 80)
try:
    calls_response = supabase.table('veterinary_calls').select('key_call_date, key_call_time, created_at').limit(3).execute()
    
    if calls_response.data:
        print(f"✅ Found {len(calls_response.data)} sample date/time records\n")
        
        for i, call in enumerate(calls_response.data, 1):
            print(f"Record #{i}:")
            print(f"  key_call_date: {call.get('key_call_date')} (type: {type(call.get('key_call_date')).__name__})")
            print(f"  key_call_time: {call.get('key_call_time')} (type: {type(call.get('key_call_time')).__name__})")
            print(f"  created_at: {call.get('created_at')} (type: {type(call.get('created_at')).__name__})")
            print()
    else:
        print("⚠️  No date/time data found")
        
except Exception as e:
    print(f"❌ Error querying date/time: {e}")

print("\n" + "="*80)

# Query 5: Count records to verify data exists
print("📊 QUERY 5: Record counts")
print("-" * 80)
try:
    alerts_count = supabase.table('call_manager_alerts').select('id', count='exact').execute()
    calls_count = supabase.table('veterinary_calls').select('call_id', count='exact').execute()
    
    print(f"  call_manager_alerts: {alerts_count.count} records")
    print(f"  veterinary_calls: {calls_count.count} records")
    
except Exception as e:
    print(f"❌ Error counting records: {e}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80 + "\n")
