"""
Get your real IP address for geolocation testing

This script:
1. Gets your local network IP
2. Gets your public IP (via external API)
3. Tests geolocation detection with real IP
4. Updates the Flask server to accept external connections
"""

import socket
import requests

def get_local_ip():
    """Get local network IP address"""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google DNS
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error: {e}"

def get_public_ip():
    """Get public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception as e:
        return f"Error: {e}"

def test_geolocation_with_ip(ip_address):
    """Test geolocation detection with a specific IP"""
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
        data = response.json()
        
        print(f"\n  Country: {data.get('country_name', 'Unknown')}")
        print(f"  City: {data.get('city', 'Unknown')}")
        print(f"  Region: {data.get('region', 'Unknown')}")
        print(f"  Timezone: {data.get('timezone', 'Unknown')}")
        print(f"  Latitude: {data.get('latitude', 'Unknown')}")
        print(f"  Longitude: {data.get('longitude', 'Unknown')}")
        print(f"  ISP: {data.get('org', 'Unknown')}")
        
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    print("=" * 80)
    print("IP ADDRESS & GEOLOCATION DETECTION")
    print("=" * 80)
    
    # Get local network IP
    local_ip = get_local_ip()
    print(f"\n1. Local Network IP: {local_ip}")
    print(f"   Use this to access from other devices on your network")
    print(f"   URL: http://{local_ip}:5001")
    
    # Get public IP
    print(f"\n2. Public IP Address:")
    public_ip = get_public_ip()
    print(f"   {public_ip}")
    
    # Test geolocation with public IP
    print(f"\n3. Geolocation for Public IP ({public_ip}):")
    test_geolocation_with_ip(public_ip)
    
    # Instructions
    print("\n" + "=" * 80)
    print("HOW TO USE YOUR REAL IP FOR GEOLOCATION:")
    print("=" * 80)
    
    print("\nOPTION 1: Access via Network IP (for testing on same network)")
    print(f"  1. Open browser and go to: http://{local_ip}:5001")
    print(f"  2. The server will still see localhost (127.0.0.1)")
    print(f"  3. Not recommended for real IP detection")
    
    print("\nOPTION 2: Deploy to Public Server (RECOMMENDED)")
    print(f"  1. Deploy Flask app to Render/Heroku/Railway/etc.")
    print(f"  2. Access via public URL (e.g., https://yourapp.onrender.com)")
    print(f"  3. Server will see your real Australian IP: {public_ip}")
    print(f"  4. Geolocation will show your actual location")
    
    print("\nOPTION 3: Test with Public IP API Directly")
    print(f"  1. Open browser console (F12)")
    print(f"  2. Run: fetch('https://ipapi.co/json/').then(r=>r.json()).then(console.log)")
    print(f"  3. You'll see your real Australian location data")
    
    print("\nOPTION 4: Modify Flask to Trust X-Forwarded-For Header")
    print(f"  1. Use a proxy/tunnel (ngrok, cloudflared)")
    print(f"  2. Proxy forwards real IP in X-Forwarded-For header")
    print(f"  3. Flask reads that header for geolocation")
    
    print("\n" + "=" * 80)
    print("CURRENT STATUS:")
    print("=" * 80)
    print(f"  Running on localhost → sees 127.0.0.1 (loopback)")
    print(f"  Your actual public IP: {public_ip}")
    print(f"  To see real location: Deploy to public server or use proxy")
    print("=" * 80)

if __name__ == "__main__":
    main()
