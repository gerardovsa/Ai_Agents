"""
IP-based Location Detection for System Prompts
Detects user's location from IP address to customize web_search server tool behavior
Enhanced with temporal awareness (time of day, season, work hours)
Enhanced with weather data (temperature, conditions)
"""

import requests
from typing import Dict, Optional
from datetime import datetime
from threading import Lock
from time import monotonic
import pytz


_WEATHER_SUCCESS_TTL_SECONDS = 15 * 60
_WEATHER_FAILURE_TTL_SECONDS = 2 * 60
_WEATHER_CACHE_MAXSIZE = 128
_weather_cache = {}
_weather_cache_lock = Lock()


def get_location_from_ip(ip_address: Optional[str] = None) -> Dict[str, str]:
    """
    Get user location from IP address using ipapi.co (free, no API key required)
    
    Args:
        ip_address: Optional IP address. If None, uses request IP
    
    Returns:
        Dict with location info:
        {
            'city': 'Brisbane',
            'region': 'Queensland',
            'country': 'AU',
            'country_name': 'Australia',
            'timezone': 'Australia/Brisbane',
            'location_string': 'Brisbane, Queensland, Australia',
            'latitude': -27.4786,
            'longitude': 153.0244,
            'ip': '101.115.163.253',
            'current_time': '2025-11-06 12:30:00 AEST',
            'time_of_day': 'afternoon',
            'day_of_week': 'Wednesday',
            'day_of_week_num': 2,
            'is_weekend': False,
            'is_work_hours': True,
            'season': 'Spring',
            'hour': 12,
            'date': '2025-11-06',
            'temperature_c': 28.5,
            'temperature_f': 83.3,
            'weather_condition': 'Partly cloudy',
            'weather_code': 2
        }
        
        Falls back to Brisbane, Australia if detection fails
    """
    default_location = {
        'city': 'Brisbane',
        'region': 'Queensland',
        'country': 'AU',
        'country_name': 'Australia',
        'timezone': 'Australia/Brisbane',
        'location_string': 'Brisbane, Queensland, Australia',
        'latitude': -27.4786,
        'longitude': 153.0244,
        'ip': ip_address or '127.0.0.1',
        'resolved_from_ip': False
    }
    
    try:
        # Use ipapi.co free service (1000 requests/day, no key needed)
        if ip_address:
            url = f'https://ipapi.co/{ip_address}/json/'
        else:
            url = 'https://ipapi.co/json/'
        
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        data = response.json()
        
        # Check if we got valid data
        if 'error' in data:
            print(f"[IP Location] Error from API: {data.get('reason', 'Unknown')}")
            return default_location.copy()
        
        # Extract location info
        city = data.get('city', 'Unknown')
        region = data.get('region', '')
        country_code = data.get('country_code', 'AU')
        country_name = data.get('country_name', 'Australia')
        timezone = data.get('timezone', 'UTC')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        ip = data.get('ip', ip_address or '127.0.0.1')
        
        # Build location string
        parts = [p for p in [city, region, country_name] if p]
        location_string = ', '.join(parts)
        
        result = {
            'city': city,
            'region': region,
            'country': country_code,
            'country_name': country_name,
            'timezone': timezone,
            'location_string': location_string,
            'latitude': latitude,
            'longitude': longitude,
            'ip': ip,
            'resolved_from_ip': True
        }
        
        print(f"[IP Location] Detected: {location_string}")
        return result
        
    except requests.exceptions.Timeout:
        print("[IP Location] Timeout - using default Brisbane location")
        return default_location.copy()
    except requests.exceptions.RequestException as e:
        print(f"[IP Location] Request failed: {e} - using default Brisbane location")
        return default_location.copy()
    except Exception as e:
        print(f"[IP Location] Unexpected error: {e} - using default Brisbane location")
        return default_location.copy()


def _fetch_weather_data(latitude: float, longitude: float) -> Dict:
    """
    Get current weather data from Open-Meteo API (free, no API key required)
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        Dict with weather data:
        {
            'temperature_c': 28.5,
            'temperature_f': 83.3,
            'weather_condition': 'Partly cloudy',
            'weather_code': 2
        }
    """
    try:
        # Open-Meteo free API (no key required)
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,weather_code',
            'timezone': 'auto'
        }
        
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        # Extract current weather
        current = data.get('current', {})
        temp_c = current.get('temperature_2m', 20.0)  # Default to 20C
        temp_f = (temp_c * 9/5) + 32  # Convert to Fahrenheit
        weather_code = current.get('weather_code', 0)
        
        # Weather code mapping (WMO codes)
        weather_descriptions = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            71: 'Slight snow',
            73: 'Moderate snow',
            75: 'Heavy snow',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }
        
        weather_condition = weather_descriptions.get(weather_code, 'Unknown')
        
        return {
            'temperature_c': round(temp_c, 1),
            'temperature_f': round(temp_f, 1),
            'weather_condition': weather_condition,
            'weather_code': weather_code
        }
        
    except Exception as e:
        print(f"[Weather] Failed to fetch weather data: {e}")
        # Return default/unknown values
        return {
            'temperature_c': None,
            'temperature_f': None,
            'weather_condition': 'Unknown',
            'weather_code': 0
        }


def _get_weather_data(latitude: float, longitude: float) -> Dict:
    """Return current weather with a bounded per-process TTL cache."""
    cache_key = (round(float(latitude), 3), round(float(longitude), 3))
    now = monotonic()

    with _weather_cache_lock:
        cached = _weather_cache.get(cache_key)
        if cached and cached['expires_at'] > now:
            return cached['value'].copy()
        if cached:
            _weather_cache.pop(cache_key, None)

    weather = _fetch_weather_data(latitude, longitude)
    ttl = (
        _WEATHER_SUCCESS_TTL_SECONDS
        if weather.get('temperature_c') is not None
        else _WEATHER_FAILURE_TTL_SECONDS
    )

    with _weather_cache_lock:
        if len(_weather_cache) >= _WEATHER_CACHE_MAXSIZE:
            oldest_key = min(
                _weather_cache,
                key=lambda key: _weather_cache[key]['expires_at'],
            )
            _weather_cache.pop(oldest_key, None)
        _weather_cache[cache_key] = {
            'expires_at': now + ttl,
            'value': weather.copy(),
        }

    return weather


def _safe_iso_country(value):
    """Return ``value`` if it is a 2-letter ISO 3166-1 alpha-2 code, else ``None``.

    Anthropic's ``web_search_20250305`` server tool requires the
    ``user_location.country`` field to be at most 2 characters. Stored
    location rows (e.g. ``ai_infrastructure.user_preferences.detected_country``)
    historically hold the full country NAME (e.g. ``"Australia"``) under the
    ``"country"`` key by mistake; this helper rejects that shape so the
    default 2-letter code (e.g. ``"AU"``) can survive the merge in
    :func:`build_context_from_stored_location`. Non-string, empty, longer-than-2,
    or non-alphabetic values are all treated as missing.
    """
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if len(stripped) == 2 and stripped.isalpha():
        return stripped.upper()
    return None


def _add_temporal_data(location: Dict) -> Dict:
    """
    Add temporal awareness data (time, day, season) and weather to location dict
    
    Args:
        location: Location dict with 'timezone', 'latitude', 'longitude' keys
    
    Returns:
        Enhanced location dict with temporal and weather data
    """
    try:
        timezone_str = location.get('timezone', 'UTC')
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        
        # Time of day
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # Day of week
        day_of_week = now.strftime('%A')
        day_of_week_num = now.weekday()
        is_weekend = day_of_week_num >= 5
        
        # Work hours (9 AM - 5 PM)
        is_work_hours = 9 <= hour < 17 and not is_weekend
        
        # Season - Detect hemisphere based on latitude
        month = now.month
        latitude = location.get('latitude') or 0
        
        # Southern Hemisphere (latitude < 0) has opposite seasons
        if latitude < 0:
            # Southern Hemisphere
            if month in [12, 1, 2]:
                season = 'Summer'
            elif month in [3, 4, 5]:
                season = 'Autumn'
            elif month in [6, 7, 8]:
                season = 'Winter'
            else:
                season = 'Spring'
        else:
            # Northern Hemisphere
            if month in [12, 1, 2]:
                season = 'Winter'
            elif month in [3, 4, 5]:
                season = 'Spring'
            elif month in [6, 7, 8]:
                season = 'Summer'
            else:
                season = 'Fall/Autumn'
        
        # Add temporal data (use 12-hour format with AM/PM)
        location['current_time'] = now.strftime('%Y-%m-%d at %I:%M %p %Z')
        location['time_of_day'] = time_of_day
        location['day_of_week'] = day_of_week
        location['day_of_week_num'] = day_of_week_num
        location['is_weekend'] = is_weekend
        location['is_work_hours'] = is_work_hours
        location['season'] = season
        location['hour'] = hour
        location['date'] = now.strftime('%Y-%m-%d')
        location['month_name'] = now.strftime('%B')
        location['success'] = True
        
        # Add weather data if coordinates available
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        if latitude is not None and longitude is not None:
            weather_data = _get_weather_data(latitude, longitude)
            location.update(weather_data)
        
    except Exception as e:
        print(f"[IP Location] Error adding temporal data: {e}")
        location['success'] = False
    
    return location


def build_context_from_stored_location(
    location: Optional[Dict] = None,
    location_override: Optional[str] = None,
    timezone_override: Optional[str] = None,
) -> Dict:
    """Build fresh temporal/weather context without resolving an IP address."""
    stored = dict(location or {})
    # Sanitize the country value: a stored full country name (e.g. "Australia")
    # under the "country" key would break Anthropic's web_search tool, which
    # requires the country field to be <=2 characters. If the value isn't a
    # valid ISO 3166-1 alpha-2 code, drop it so the default "AU" survives.
    safe_country = _safe_iso_country(stored.get('country'))
    if safe_country is not None:
        stored['country'] = safe_country
    else:
        stored.pop('country', None)

    default_location = {
        'city': 'Brisbane',
        'region': 'Queensland',
        'country': 'AU',
        'country_name': 'Australia',
        'timezone': 'Australia/Brisbane',
        'location_string': 'Brisbane, Queensland, Australia',
        'latitude': None,
        'longitude': None,
    }

    context = {**default_location, **{k: v for k, v in stored.items() if v is not None}}
    if timezone_override:
        context['timezone'] = timezone_override
    if location_override:
        context['location_string'] = location_override
    elif not context.get('location_string'):
        parts = [
            context.get('city'),
            context.get('region'),
            context.get('country_name') or context.get('country'),
        ]
        context['location_string'] = ', '.join(part for part in parts if part)

    return _add_temporal_data(context)


def get_location_for_prompt(request_ip: Optional[str] = None) -> str:
    """
    Get location string formatted for system prompt
    
    Args:
        request_ip: Optional IP from Flask request
    
    Returns:
        Formatted location string like "Brisbane, Queensland, Australia"
    """
    location = get_location_from_ip(request_ip)
    return location['location_string']


def get_location_dict(request_ip: Optional[str] = None) -> Dict[str, str]:
    """
    Get full location dictionary for web_search tool configuration
    
    Args:
        request_ip: Optional IP from Flask request
    
    Returns:
        Dict with city, region, country, timezone for web_search tool
    """
    return build_context_from_stored_location(get_location_from_ip(request_ip))


def get_temporal_awareness(timezone_str: str) -> Dict:
    """
    Get temporal awareness data (time of day, season, work hours) for a timezone
    
    Args:
        timezone_str: Timezone string like 'Australia/Brisbane'
    
    Returns:
        Dict with temporal data:
        {
            'current_time': '2025-11-06 12:30:00 AEST',
            'time_of_day': 'afternoon',
            'day_of_week': 'Wednesday',
            'is_weekend': False,
            'is_work_hours': True,
            'season': 'Spring',
            'hour': 12
        }
    """
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        
        # Time of day
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # Day of week
        day_of_week = now.strftime('%A')
        day_of_week_num = now.weekday()
        is_weekend = day_of_week_num >= 5
        
        # Work hours (9 AM - 5 PM)
        is_work_hours = 9 <= hour < 17 and not is_weekend
        
        # Season (Northern Hemisphere - can be adjusted)
        month = now.month
        if month in [12, 1, 2]:
            season = 'Winter'
        elif month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        else:
            season = 'Fall'
        
        return {
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'day_of_week_num': day_of_week_num,
            'is_weekend': is_weekend,
            'is_work_hours': is_work_hours,
            'season': season,
            'hour': hour,
            'date': now.strftime('%Y-%m-%d')
        }
    except Exception as e:
        print(f"[Temporal Awareness] Error: {e}")
        return {
            'current_time': 'Unknown',
            'time_of_day': 'unknown',
            'day_of_week': 'Unknown',
            'is_weekend': False,
            'is_work_hours': False,
            'season': 'Unknown',
            'hour': 0
        }


def build_geolocation_context(request_ip: Optional[str] = None) -> Dict:
    """
    Build complete geolocation context with location + temporal awareness
    
    Args:
        request_ip: Optional IP from Flask request
    
    Returns:
        Full geolocation context with all data
    """
    return build_context_from_stored_location(get_location_from_ip(request_ip))


# Example usage in routes:
"""
from core.ip_location import (
    get_location_for_prompt, 
    get_location_dict, 
    get_temporal_awareness,
    build_geolocation_context
)

# In route handler:
user_ip = request.remote_addr
location_string = get_location_for_prompt(user_ip)
location_dict = get_location_dict(user_ip)
full_context = build_geolocation_context(user_ip)

# Inject into system prompt:
system_prompt = system_prompt.replace('{{USER_LOCATION}}', location_string)

# Update web_search tool user_location:
web_search_tool = {
    "type": "web_search_20250305",
    "name": "web_search",
    "user_location": {
        "type": "approximate",
        "city": location_dict['city'],
        "region": location_dict['region'],
        "country": location_dict['country'],
        "timezone": location_dict['timezone']
    }
}

# Use temporal awareness:
temporal = get_temporal_awareness('Australia/Brisbane')
if temporal['is_work_hours']:
    # Business hours context
    pass
"""
