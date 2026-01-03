"""
Weather Module Implementations
Uses existing ip_location.py integration with Open-Meteo API
Caches weather data in Supabase for 1 hour to minimize API calls
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
import time
from datetime import datetime, timedelta

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'AI_infrastructure'))

# Import existing location/weather utilities
from AI_infrastructure.core.ip_location import get_location_from_ip
from AI_infrastructure.shared.database_utils import execute_query

def _get_cached_weather(location_key: str) -> Optional[Dict]:
    """
    Get cached weather data from database
    
    Args:
        location_key: Unique key for location (lat_lon rounded to 2 decimals)
    
    Returns:
        Cached weather data or None if expired/not found
    """
    try:
        # Check if cache table exists, create if not
        execute_query("""
            CREATE TABLE IF NOT EXISTS weather_cache (
                location_key TEXT PRIMARY KEY,
                weather_data JSONB NOT NULL,
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """)
        
        # Get cached data
        result = execute_query("""
            SELECT weather_data, expires_at
            FROM weather_cache
            WHERE location_key = %s AND expires_at > NOW()
        """, (location_key,), fetch_mode='one')
        
        if result:
            return result[0]  # weather_data JSON
        
        return None
    except Exception as e:
        print(f"[Weather Cache] Error reading cache: {e}")
        return None

def _save_weather_cache(location_key: str, weather_data: Dict):
    """
    Save weather data to cache with 1 hour expiration
    
    Args:
        location_key: Unique key for location
        weather_data: Weather data to cache
    """
    try:
        expires_at = datetime.now() + timedelta(hours=1)
        
        execute_query("""
            INSERT INTO weather_cache (location_key, weather_data, expires_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (location_key)
            DO UPDATE SET
                weather_data = EXCLUDED.weather_data,
                last_updated = NOW(),
                expires_at = EXCLUDED.expires_at
        """, (location_key, json.dumps(weather_data), expires_at))
        
        print(f"[Weather Cache] Saved cache for {location_key}")
    except Exception as e:
        print(f"[Weather Cache] Error saving cache: {e}")

def _get_location_key(lat: float, lon: float) -> str:
    """Create cache key from coordinates (rounded to 2 decimals = ~1km resolution)"""
    return f"{round(lat, 2)}_{round(lon, 2)}"

def get_current_weather(latitude: Optional[float] = None, 
                       longitude: Optional[float] = None,
                       location_name: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
    """
    Get current weather conditions
    
    Args:
        latitude: Optional latitude (auto-detected if not provided)
        longitude: Optional longitude (auto-detected if not provided)
        location_name: Optional display name
        **kwargs: Additional parameters (e.g., from credential injection)
    
    Returns:
        Dict with success, location info, and current weather data
    """
    try:
        # Get location (from IP if coords not provided)
        if latitude is None or longitude is None:
            location = get_location_from_ip()
            latitude = location['latitude']
            longitude = location['longitude']
            if not location_name:
                location_name = location['location_string']
        
        # Check cache
        location_key = _get_location_key(latitude, longitude)
        cached = _get_cached_weather(location_key)
        
        if cached:
            print(f"[Weather] Using cached data for {location_name or location_key}")
            return {
                "success": True,
                "cached": True,
                **cached
            }
        
        # Fetch fresh data from Open-Meteo
        import requests
        
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl',
            'timezone': 'auto'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        
        result = {
            "success": True,
            "cached": False,
            "location": {
                "name": location_name or f"{latitude}, {longitude}",
                "latitude": latitude,
                "longitude": longitude
            },
            "current_weather": {
                "temperature_c": current['temperature_2m'],
                "temperature_f": (current['temperature_2m'] * 9/5) + 32,
                "feels_like_c": current['apparent_temperature'],
                "humidity": current['relative_humidity_2m'],
                "precipitation_mm": current.get('precipitation', 0),
                "wind_speed_kmh": current['wind_speed_10m'],
                "wind_direction": current['wind_direction_10m'],
                "pressure_hpa": current.get('pressure_msl'),
                "weather_code": current['weather_code'],
                "weather_description": _get_weather_description(current['weather_code']),
                "timestamp": current['time']
            }
        }
        
        # Save to cache
        _save_weather_cache(location_key, result)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch current weather"
        }

def get_weather_forecast(latitude: Optional[float] = None,
                        longitude: Optional[float] = None,
                        days: int = 7,
                        location_name: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
    """
    Get weather forecast for multiple days
    
    Args:
        latitude: Optional latitude (auto-detected if not provided)
        longitude: Optional longitude (auto-detected if not provided)
        days: Number of forecast days (1-16)
        location_name: Optional display name
        **kwargs: Additional parameters
    
    Returns:
        Dict with success and forecast data
    """
    try:
        # Get location
        if latitude is None or longitude is None:
            location = get_location_from_ip()
            latitude = location['latitude']
            longitude = location['longitude']
            if not location_name:
                location_name = location['location_string']
        
        # Validate days
        days = max(1, min(16, days))
        
        # Check cache
        location_key = f"{_get_location_key(latitude, longitude)}_forecast_{days}d"
        cached = _get_cached_weather(location_key)
        
        if cached:
            return {
                "success": True,
                "cached": True,
                **cached
            }
        
        # Fetch from Open-Meteo
        import requests
        
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,sunrise,sunset',
            'timezone': 'auto',
            'forecast_days': days
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily = data['daily']
        
        forecast_days = []
        for i in range(len(daily['time'])):
            forecast_days.append({
                "date": daily['time'][i],
                "temperature_max_c": daily['temperature_2m_max'][i],
                "temperature_min_c": daily['temperature_2m_min'][i],
                "temperature_max_f": (daily['temperature_2m_max'][i] * 9/5) + 32,
                "temperature_min_f": (daily['temperature_2m_min'][i] * 9/5) + 32,
                "precipitation_mm": daily['precipitation_sum'][i],
                "precipitation_probability": daily.get('precipitation_probability_max', [None]*len(daily['time']))[i],
                "wind_speed_max_kmh": daily['wind_speed_10m_max'][i],
                "weather_code": daily['weather_code'][i],
                "weather_description": _get_weather_description(daily['weather_code'][i]),
                "sunrise": daily.get('sunrise', [None]*len(daily['time']))[i],
                "sunset": daily.get('sunset', [None]*len(daily['time']))[i]
            })
        
        result = {
            "success": True,
            "cached": False,
            "location": {
                "name": location_name or f"{latitude}, {longitude}",
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast": forecast_days
        }
        
        # Save to cache
        _save_weather_cache(location_key, result)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to fetch {days}-day forecast"
        }

def get_hourly_forecast(latitude: Optional[float] = None,
                       longitude: Optional[float] = None,
                       hours: int = 48,
                       location_name: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
    """
    Get hourly weather forecast
    
    Args:
        latitude: Optional latitude
        longitude: Optional longitude
        hours: Number of hours ahead (1-168)
        location_name: Optional display name
        **kwargs: Additional parameters
    
    Returns:
        Dict with hourly forecast data
    """
    try:
        # Get location
        if latitude is None or longitude is None:
            location = get_location_from_ip()
            latitude = location['latitude']
            longitude = location['longitude']
            if not location_name:
                location_name = location['location_string']
        
        # Validate hours
        hours = max(1, min(168, hours))
        
        # Fetch from Open-Meteo
        import requests
        
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m',
            'timezone': 'auto',
            'forecast_hours': hours
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        hourly = data['hourly']
        
        hourly_forecast = []
        for i in range(min(hours, len(hourly['time']))):
            hourly_forecast.append({
                "time": hourly['time'][i],
                "temperature_c": hourly['temperature_2m'][i],
                "temperature_f": (hourly['temperature_2m'][i] * 9/5) + 32,
                "humidity": hourly['relative_humidity_2m'][i],
                "precipitation_probability": hourly.get('precipitation_probability', [None]*len(hourly['time']))[i],
                "precipitation_mm": hourly['precipitation'][i],
                "wind_speed_kmh": hourly['wind_speed_10m'][i],
                "weather_code": hourly['weather_code'][i],
                "weather_description": _get_weather_description(hourly['weather_code'][i])
            })
        
        return {
            "success": True,
            "location": {
                "name": location_name or f"{latitude}, {longitude}",
                "latitude": latitude,
                "longitude": longitude
            },
            "hourly_forecast": hourly_forecast
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to fetch {hours}-hour forecast"
        }

def search_location_weather(query: str, **kwargs) -> Dict[str, Any]:
    """
    Search for location and get weather
    
    Args:
        query: City name or address (e.g., "Brisbane, Australia")
        **kwargs: Additional parameters
    
    Returns:
        Dict with location and weather data
    """
    try:
        # Use Open-Meteo geocoding API
        import requests
        
        geocode_url = 'https://geocoding-api.open-meteo.com/v1/search'
        geocode_params = {
            'name': query,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(geocode_url, params=geocode_params, timeout=10)
        response.raise_for_status()
        geocode_data = response.json()
        
        if not geocode_data.get('results'):
            return {
                "success": False,
                "error": f"Location not found: {query}"
            }
        
        location = geocode_data['results'][0]
        latitude = location['latitude']
        longitude = location['longitude']
        location_name = f"{location['name']}, {location.get('admin1', '')}, {location['country']}"
        
        # Get weather for resolved location
        weather = get_current_weather(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        
        return weather
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search location weather for: {query}"
        }

def _get_weather_description(code: int) -> str:
    """Convert WMO weather code to description"""
    descriptions = {
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
        77: 'Snow grains',
        80: 'Slight rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers',
        85: 'Slight snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with slight hail',
        99: 'Thunderstorm with heavy hail'
    }
    return descriptions.get(code, 'Unknown')
