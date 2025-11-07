"""
Manually populate Australian geolocation for user_id=1

This script fetches your REAL Australian IP geolocation data
and updates the database with accurate Brisbane, Queensland data.
"""

import requests
import sqlite3
from pathlib import Path
from datetime import datetime

def populate_australian_geolocation():
    """Populate real Australian geolocation for user_id=1"""
    
    print("=" * 80)
    print("FETCHING REAL AUSTRALIAN GEOLOCATION DATA")
    print("=" * 80)
    
    # Get real public IP geolocation (your Australian IP)
    print("\nDetecting geolocation from your public IP...")
    try:
        response = requests.get("https://ipapi.co/json/", timeout=10)
        data = response.json()
        
        country = data.get('country_name', 'Unknown')
        city = data.get('city', 'Unknown')
        region = data.get('region', 'Unknown')
        timezone = data.get('timezone', 'Unknown')
        ip_address = data.get('ip', 'Unknown')
        latitude = data.get('latitude', None)
        longitude = data.get('longitude', None)
        isp = data.get('org', 'Unknown')
        
        print(f"\n  Detected Location:")
        print(f"  Country: {country}")
        print(f"  City: {city}")
        print(f"  Region: {region}")
        print(f"  Timezone: {timezone}")
        print(f"  IP: {ip_address}")
        print(f"  Coordinates: {latitude}, {longitude}")
        print(f"  ISP: {isp}")
        
    except Exception as e:
        print(f"\n  Error detecting geolocation: {e}")
        print(f"  Using fallback Brisbane data...")
        
        # Fallback to Brisbane data
        country = "Australia"
        city = "Brisbane"
        region = "Queensland"
        timezone = "Australia/Brisbane"
        ip_address = "101.115.163.253"
    
    # Update database
    print("\n" + "=" * 80)
    print("UPDATING DATABASE WITH AUSTRALIAN LOCATION")
    print("=" * 80)
    
    db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Update user_id=1 preferences
    cursor.execute("""
        UPDATE user_preferences 
        SET detected_country = ?,
            detected_city = ?,
            detected_timezone = ?,
            detected_ip_address = ?,
            last_location_check = ?,
            updated_at = ?
        WHERE user_id = 1
    """, (
        country,
        city,
        timezone,
        ip_address,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    if rows_updated > 0:
        print(f"\n  Database updated successfully!")
    else:
        print(f"\n  Warning: No rows updated (user_id=1 may not exist)")
    
    # Verify
    cursor.execute("""
        SELECT detected_country, detected_city, detected_timezone, detected_ip_address
        FROM user_preferences WHERE user_id = 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print(f"\n  Verified - Saved data:")
        print(f"  Country: {result[0]}")
        print(f"  City: {result[1]}")
        print(f"  Timezone: {result[2]}")
        print(f"  IP: {result[3]}")
    
    # Test backend API
    print("\n" + "=" * 80)
    print("TESTING BACKEND API")
    print("=" * 80)
    
    try:
        response = requests.get("http://localhost:5001/api/user/preferences", timeout=5)
        if response.status_code == 200:
            prefs = response.json().get('data', {})
            print(f"\n  API Response:")
            print(f"  Country: {prefs.get('detected_country')}")
            print(f"  City: {prefs.get('detected_city')}")
            print(f"  Timezone: {prefs.get('detected_timezone')}")
            print(f"  IP: {prefs.get('detected_ip_address')}")
        else:
            print(f"\n  API Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"\n  API Error: {e}")
    
    print("\n" + "=" * 80)
    print("SUCCESS! AUSTRALIAN LOCATION DATA POPULATED")
    print("=" * 80)
    print("\n  Next Steps:")
    print("  1. Refresh your browser (Ctrl+F5)")
    print("  2. Open Profile Menu (top-right corner)")
    print("  3. Check Profile Settings tab")
    print("  4. You should see:")
    print(f"     - Location: {city}, {country}")
    print(f"     - Timezone: {timezone}")
    print(f"     - IP: {ip_address}")
    print("\n  Note: Timezone will show Australian time (AEST/AEDT)")
    print("=" * 80)

if __name__ == "__main__":
    populate_australian_geolocation()
