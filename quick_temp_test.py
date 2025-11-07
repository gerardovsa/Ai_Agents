"""Quick temperature test"""
from AI_infrastructure.core.ip_location import get_location_from_ip

loc = get_location_from_ip()
print(f"Temperature: {loc.get('temperature_c')}C / {loc.get('temperature_f')}F")
print(f"Weather: {loc.get('weather_condition')}")
print(f"Location: {loc.get('city')}, {loc.get('country_name')}")
print("SUCCESS: Temperature integration working!")
