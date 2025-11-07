"""
Populate user_id=1 with current IP-based geolocation data

This script:
1. Detects geolocation from IP (via backend API)
2. Updates user_preferences for user_id=1
3. Verifies the data was saved
"""

import requests
import sqlite3
from pathlib import Path
from datetime import datetime

def populate_geolocation():
    """Populate geolocation for user_id=1"""
    
    # Get geolocation from API
    print("Detecting geolocation from IP...")
    response = requests.get("http://localhost:5001/api/geolocation/detect", timeout=5)
    
    if response.status_code != 200:
        print(f"Failed to get geolocation: {response.status_code}")
        return
    
    data = response.json().get('data', {})
    
    country = data.get('country_name', 'Unknown')
    city = data.get('city', 'Unknown')
    timezone = data.get('timezone', 'Unknown')
    ip_address = data.get('ip', 'Unknown')
    
    print(f"Detected:")
    print(f"  Country: {country}")
    print(f"  City: {city}")
    print(f"  Timezone: {timezone}")
    print(f"  IP: {ip_address}")
    
    # Update database
    db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT user_id FROM user_preferences WHERE user_id = 1")
    exists = cursor.fetchone()
    
    if exists:
        # Update existing record
        print("\nUpdating user_id=1 preferences...")
        cursor.execute("""
            UPDATE user_preferences 
            SET detected_country = ?,
                detected_city = ?,
                detected_timezone = ?,
                detected_ip_address = ?,
                last_location_check = ?,
                updated_at = ?
            WHERE user_id = 1
        """, (country, city, timezone, ip_address, datetime.now().isoformat(), datetime.now().isoformat()))
    else:
        # Insert new record
        print("\nCreating user_id=1 preferences...")
        cursor.execute("""
            INSERT INTO user_preferences (
                user_id, 
                communication_style, 
                detail_level, 
                auth_platform,
                detected_country,
                detected_city,
                detected_timezone,
                detected_ip_address,
                last_location_check,
                ai_memories,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 
            'professional', 
            'standard', 
            'auto',
            country,
            city,
            timezone,
            ip_address,
            datetime.now().isoformat(),
            '[]',
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    
    # Verify
    cursor.execute("""
        SELECT detected_country, detected_city, detected_timezone, detected_ip_address
        FROM user_preferences WHERE user_id = 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    print("\nVerification - Saved data:")
    print(f"  Country: {result[0]}")
    print(f"  City: {result[1]}")
    print(f"  Timezone: {result[2]}")
    print(f"  IP: {result[3]}")
    
    print("\nSuccess! Geolocation data populated for user_id=1")
    print("Refresh your browser to see the changes.")

if __name__ == "__main__":
    populate_geolocation()
