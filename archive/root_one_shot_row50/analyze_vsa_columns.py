"""
Analyze column structure and data formatting
"""

import os
import json
from supabase import create_client, Client
from datetime import datetime

# Supabase credentials
SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*80)
print("VSA ALERTS - COLUMN & DATA ANALYSIS")
print("="*80 + "\n")

# Get one sample call and print ALL columns
print("📊 FULL COLUMN STRUCTURE - veterinary_calls")
print("-" * 80)
try:
    call_response = supabase.table('veterinary_calls').select('*').limit(1).execute()
    
    if call_response.data:
        call = call_response.data[0]
        print(f"✅ Sample record with ALL columns:\n")
        
        for key, value in sorted(call.items()):
            print(f"  {key}: {value}")
    else:
        print("⚠️  No data found")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)

# Get one sample alert and print ALL columns
print("📊 FULL COLUMN STRUCTURE - call_manager_alerts")
print("-" * 80)
try:
    alert_response = supabase.table('call_manager_alerts').select('*').limit(1).execute()
    
    if alert_response.data:
        alert = alert_response.data[0]
        print(f"✅ Sample record with ALL columns:\n")
        
        for key, value in sorted(alert.items()):
            print(f"  {key}: {value}")
    else:
        print("⚠️  No data found")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)

# Test date parsing
print("📊 DATE PARSING TEST")
print("-" * 80)
try:
    call_response = supabase.table('veterinary_calls').select('call_id, key_call_date, key_staffname').limit(5).execute()
    
    if call_response.data:
        print(f"✅ Testing date formatting on {len(call_response.data)} records:\n")
        
        for call in call_response.data:
            call_date = call.get('key_call_date')
            staff_name = call.get('key_staffname')
            call_id = call.get('call_id')
            
            # Try to extract time from call_id (format: NAME-TIME or DATETIME)
            time_str = "UNKNOWN"
            if call_id and '_' in call_id:
                parts = call_id.split('_')
                if len(parts) > 1:
                    time_str = parts[-1]  # Last part after underscore
            
            # Format date
            if call_date:
                try:
                    if isinstance(call_date, str):
                        date_obj = datetime.strptime(call_date, '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%m/%d/%Y')
                    else:
                        formatted_date = str(call_date)
                except:
                    formatted_date = str(call_date)
            else:
                formatted_date = "UNKNOWN"
            
            print(f"Call: {call_id[:50]}...")
            print(f"  Staff: {staff_name or 'UNKNOWN'}")
            print(f"  Time: {time_str}")
            print(f"  Date: {formatted_date}")
            print(f"  → Header would show: {staff_name or 'UNKNOWN'} - {time_str} - {formatted_date}")
            print()
    else:
        print("⚠️  No data found")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80 + "\n")

print("\n🔍 KEY FINDINGS:")
print("1. Check if 'key_call_time' column exists (it doesn't - we get time from call_id)")
print("2. Check date format in key_call_date")
print("3. Verify staffName field name in veterinary_calls")
print("4. Test how VSA JavaScript is parsing these fields")
