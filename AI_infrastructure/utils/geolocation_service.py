"""
FILE: AI_infrastructure/utils/geolocation_service.py
PURPOSE: IP geolocation and temporal awareness utilities for user context

DEPENDENCIES:
- geolite2 - Free GeoIP database (pip install geolite2)
- pytz - Timezone handling
- datetime - Temporal calculations

EXPORTS:
- get_location_from_ip(ip_address) -> dict - Get country, city, timezone from IP
- get_temporal_awareness(timezone_str) -> dict - Get time_of_day, day_of_week, season, is_work_hours
- build_geolocation_context(ip_address) -> dict - Combined location and temporal context

USED BY:
- agent_routes_v4.py (inject context before agent execution)
- context_aware_ai.py (enhance system prompt with location/temporal awareness)

RELATED FILES:
- AI_infrastructure/utils/validators.py (validation utilities)
- AI_infrastructure/routes/user_preferences_routes.py (user preferences)

NOTES:
- Free tier uses GeoLite2 database (updated monthly)
- Requires: pip install geolite2 geoip2
- Fallback to generic timezone detection if exact lookup fails
- Work hours hardcoded as 9 AM - 5 PM in user's timezone
- Seasons based on Northern Hemisphere; can be made configurable

LAST MODIFIED: 2025-01-XX - Initial implementation
"""

import logging
from datetime import datetime
import pytz
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import geolocation library
try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False
    logger.warning("geoip2 not installed. Install with: pip install geoip2")

# Try to import geolite2 (free fallback)
try:
    from geolite2 import geolite2
    GEOLITE2_AVAILABLE = True
except ImportError:
    GEOLITE2_AVAILABLE = False
    logger.warning("geolite2 not installed. Install with: pip install geolite2")


def get_location_from_ip(ip_address: str) -> Optional[Dict]:
    """
    Get geographic location (country, city, coordinates) and timezone from IP address
    
    Uses GeoIP2 if available, falls back to geolite2, then generic timezone lookup
    
    Args:
        ip_address (str): IP address to geolocate (e.g., "8.8.8.8")
    
    Returns:
        dict with keys:
        {
            'ip': '8.8.8.8',
            'country': 'US',
            'country_name': 'United States',
            'city': 'Mountain View',
            'latitude': 37.386,
            'longitude': -122.084,
            'timezone': 'America/Los_Angeles',
            'success': True
        }
        
        or None if geolocation fails
    """
    try:
        # Validate IP address
        if not ip_address or ip_address == 'localhost' or ip_address == '127.0.0.1':
            # Default timezone for localhost
            return {
                'ip': ip_address,
                'country': 'US',
                'country_name': 'United States',
                'city': 'Unknown (Local)',
                'latitude': None,
                'longitude': None,
                'timezone': 'America/New_York',  # Default timezone
                'success': True
            }
        
        # Try GeoIP2 first (requires subscription)
        if GEOIP_AVAILABLE:
            try:
                reader = geoip2.database.Reader('GeoLite2-City.mmdb')
                response = reader.city(ip_address)
                
                return {
                    'ip': ip_address,
                    'country': response.country.iso_code,
                    'country_name': response.country.name,
                    'city': response.city.name or 'Unknown',
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude,
                    'timezone': response.location.time_zone,
                    'success': True
                }
            except Exception as e:
                logger.debug(f"GeoIP2 lookup failed for {ip_address}: {e}")
        
        # Fall back to geolite2
        if GEOLITE2_AVAILABLE:
            try:
                match = geolite2.reader().get(ip_address)
                if match:
                    return {
                        'ip': ip_address,
                        'country': match.get('country_code', 'US'),
                        'country_name': match.get('country_name', 'Unknown'),
                        'city': match.get('city', 'Unknown'),
                        'latitude': match.get('latitude'),
                        'longitude': match.get('longitude'),
                        'timezone': match.get('time_zone', 'America/New_York'),
                        'success': True
                    }
            except Exception as e:
                logger.debug(f"Geolite2 lookup failed for {ip_address}: {e}")
        
        # Generic fallback - determine timezone from coordinates or use default
        logger.warning(f"Could not geolocate IP {ip_address}, using default timezone")
        return {
            'ip': ip_address,
            'country': 'Unknown',
            'country_name': 'Unknown',
            'city': 'Unknown',
            'latitude': None,
            'longitude': None,
            'timezone': 'America/New_York',  # Default fallback
            'success': False
        }
        
    except Exception as e:
        logger.error(f"Error geolocalizing IP {ip_address}: {str(e)}")
        return None


def get_temporal_awareness(timezone_str: Optional[str] = None) -> Dict:
    """
    Get temporal awareness data for user based on their timezone
    
    Calculates: time_of_day, day_of_week, is_work_hours, season
    
    Args:
        timezone_str (str): Timezone string (e.g., "America/New_York")
                           If None, uses UTC
    
    Returns:
        dict with keys:
        {
            'timezone': 'America/New_York',
            'current_time': '2025-01-15 14:30:00 EST',
            'time_of_day': 'afternoon',  # morning/afternoon/evening/night
            'day_of_week': 'Wednesday',
            'day_of_week_num': 2,  # 0=Monday, 6=Sunday
            'is_work_hours': True,  # 9 AM - 5 PM
            'hour': 14,
            'date': '2025-01-15',
            'season': 'Winter',  # Spring/Summer/Fall/Winter (Northern Hemisphere)
            'is_weekend': False
        }
    """
    try:
        # Get timezone object
        if timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                logger.warning(f"Unknown timezone {timezone_str}, using UTC")
                tz = pytz.UTC
        else:
            tz = pytz.UTC
        
        # Get current time in user's timezone
        now_utc = datetime.now(pytz.UTC)
        now_local = now_utc.astimezone(tz)
        
        # Calculate time of day
        hour = now_local.hour
        if 6 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # Calculate work hours (9 AM - 5 PM)
        is_work_hours = 9 <= hour < 17
        
        # Get day of week
        day_of_week_num = now_local.weekday()  # 0=Monday, 6=Sunday
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_of_week = days[day_of_week_num]
        is_weekend = day_of_week_num >= 5
        
        # Calculate season (Northern Hemisphere)
        month = now_local.month
        day = now_local.day
        
        if (month == 3 and day >= 20) or (month == 4) or (month == 5) or (month == 6 and day < 21):
            season = 'Spring'
        elif (month == 6 and day >= 21) or (month == 7) or (month == 8) or (month == 9 and day < 23):
            season = 'Summer'
        elif (month == 9 and day >= 23) or (month == 10) or (month == 11) or (month == 12 and day < 21):
            season = 'Fall'
        else:
            season = 'Winter'
        
        return {
            'timezone': str(tz),
            'current_time': now_local.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'day_of_week_num': day_of_week_num,
            'is_work_hours': is_work_hours,
            'hour': hour,
            'date': now_local.strftime('%Y-%m-%d'),
            'season': season,
            'is_weekend': is_weekend
        }
        
    except Exception as e:
        logger.error(f"Error calculating temporal awareness for {timezone_str}: {str(e)}")
        # Return safe defaults
        return {
            'timezone': 'UTC',
            'current_time': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'time_of_day': 'unknown',
            'day_of_week': 'Unknown',
            'day_of_week_num': None,
            'is_work_hours': None,
            'hour': None,
            'date': datetime.now(pytz.UTC).strftime('%Y-%m-%d'),
            'season': 'Unknown',
            'is_weekend': None
        }


def build_geolocation_context(ip_address: str) -> Dict:
    """
    Build complete geolocation and temporal context from IP address
    
    Combines geolocation lookup with temporal awareness calculation
    
    Args:
        ip_address (str): IP address to geolocate
    
    Returns:
        dict with combined geographic and temporal context:
        {
            'ip': '8.8.8.8',
            'location': {
                'country': 'US',
                'city': 'Mountain View',
                'timezone': 'America/Los_Angeles',
                ...
            },
            'temporal': {
                'time_of_day': 'afternoon',
                'day_of_week': 'Wednesday',
                'is_work_hours': True,
                ...
            },
            'user_context_message': "User in Mountain View, US during afternoon on Wednesday (work hours)"
        }
    """
    try:
        # Get location from IP
        location = get_location_from_ip(ip_address)
        if not location:
            location = {
                'country': 'Unknown',
                'city': 'Unknown',
                'timezone': 'America/New_York'
            }
        
        # Get temporal awareness for that timezone
        temporal = get_temporal_awareness(location.get('timezone'))
        
        # Build user context message
        city = location.get('city', 'Unknown')
        country = location.get('country', 'Unknown')
        time_of_day = temporal.get('time_of_day', 'unknown')
        day_of_week = temporal.get('day_of_week', 'Unknown')
        is_work_hours = temporal.get('is_work_hours', False)
        season = temporal.get('season', 'Unknown')
        
        work_status = "work hours" if is_work_hours else "outside work hours"
        
        user_context_message = (
            f"User is located in {city}, {country} during {time_of_day} on {day_of_week} "
            f"({work_status}, {season})"
        )
        
        return {
            'ip': ip_address,
            'location': location,
            'temporal': temporal,
            'user_context_message': user_context_message,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error building geolocation context for {ip_address}: {str(e)}")
        return {
            'ip': ip_address,
            'location': None,
            'temporal': None,
            'user_context_message': 'Unable to determine location and time context',
            'success': False
        }


# For quick testing
if __name__ == '__main__':
    # Test with Google's public DNS server
    context = build_geolocation_context('8.8.8.8')
    import json
    print(json.dumps(context, indent=2, default=str))
