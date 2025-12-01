"""
Quick Supabase Connection Test - VSA Veterinary Alerts
Run this after database restart to verify connectivity
"""

import requests
from datetime import datetime

SUPABASE_URL = 'https://wuwmvtslltqhaycyukxk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4'

def quick_test():
    print(f"\n{'='*70}")
    print("VSA VETERINARY ALERTS - QUICK CONNECTION TEST")
    print(f"{'='*70}")
    print(f"Database: {SUPABASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/veterinary_calls"
    
    # Quick connectivity test
    try:
        print("Testing connection...")
        response = requests.get(
            endpoint,
            headers=headers,
            params={'select': 'call_id', 'limit': '1'},
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CONNECTION SUCCESSFUL!")
            data = response.json()
            print(f"✅ Can access veterinary_calls table")
            print(f"✅ Sample record retrieved: {len(data)} record(s)")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  TIMEOUT - Database may still be restarting...")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR - Database not accessible yet")
        print(f"   {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    finally:
        print(f"{'='*70}\n")

if __name__ == '__main__':
    import time
    
    print("\n🔄 Waiting for database to come online...")
    print("Will retry every 10 seconds for up to 2 minutes...\n")
    
    max_attempts = 12  # 2 minutes
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}:")
        
        if quick_test():
            print("✅ DATABASE IS ONLINE AND READY!")
            break
        
        if attempt < max_attempts:
            print(f"Waiting 10 seconds before retry...\n")
            time.sleep(10)
    else:
        print("❌ Database did not come online within 2 minutes")
        print("Please check Supabase dashboard and try again")
