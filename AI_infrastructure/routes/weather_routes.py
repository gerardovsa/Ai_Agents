"""
Weather API Routes for Flask
Exposes weather module tools via REST API endpoints
"""

from flask import Blueprint, jsonify, request
from tools.registry_v3 import get_registry
import logging

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')
logger = logging.getLogger(__name__)

# Get tool registry
registry = get_registry()

@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    """
    GET /api/weather/current
    
    Query parameters:
    - lat (optional): Latitude
    - lon (optional): Longitude
    - location_name (optional): Display name
    
    Returns current weather for location (auto-detected if no coords provided)
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        location_name = request.args.get('location_name')
        
        result = registry.execute_tool(
            tool_name='get_current_weather',
            latitude=lat,
            longitude=lon,
            location_name=location_name
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[Weather API] Error in /current: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@weather_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """
    GET /api/weather/forecast
    
    Query parameters:
    - days (optional): Number of days (1-16, default: 7)
    - lat (optional): Latitude
    - lon (optional): Longitude
    - location_name (optional): Display name
    
    Returns multi-day weather forecast
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        days = request.args.get('days', default=7, type=int)
        location_name = request.args.get('location_name')
        
        result = registry.execute_tool(
            tool_name='get_weather_forecast',
            latitude=lat,
            longitude=lon,
            days=days,
            location_name=location_name
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[Weather API] Error in /forecast: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@weather_bp.route('/hourly', methods=['GET'])
def get_hourly():
    """
    GET /api/weather/hourly
    
    Query parameters:
    - hours (optional): Number of hours (1-168, default: 48)
    - lat (optional): Latitude
    - lon (optional): Longitude
    - location_name (optional): Display name
    
    Returns hourly weather forecast
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        hours = request.args.get('hours', default=48, type=int)
        location_name = request.args.get('location_name')
        
        result = registry.execute_tool(
            tool_name='get_hourly_forecast',
            latitude=lat,
            longitude=lon,
            hours=hours,
            location_name=location_name
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[Weather API] Error in /hourly: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@weather_bp.route('/search', methods=['GET'])
def search_location():
    """
    GET /api/weather/search?q=Brisbane,Australia
    
    Query parameters:
    - q (required): Location query (city name, address)
    
    Searches for location and returns weather data
    """
    try:
        query = request.args.get('q')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: q"
            }), 400
        
        result = registry.execute_tool(
            tool_name='search_location_weather',
            query=query
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[Weather API] Error in /search: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@weather_bp.route('/health', methods=['GET'])
def health_check():
    """
    GET /api/weather/health
    
    Returns health status of weather API
    """
    try:
        # Check if weather tools are registered
        weather_tools = [
            'get_current_weather',
            'get_weather_forecast',
            'get_hourly_forecast',
            'search_location_weather'
        ]
        
        registered_tools = {
            tool: registry.get_tool(tool) is not None
            for tool in weather_tools
        }
        
        all_registered = all(registered_tools.values())
        
        return jsonify({
            "success": True,
            "healthy": all_registered,
            "tools": registered_tools,
            "message": "Weather API operational" if all_registered else "Some tools not registered"
        })
    except Exception as e:
        logger.error(f"[Weather API] Error in /health: {e}")
        return jsonify({
            "success": False,
            "healthy": False,
            "error": str(e)
        }), 500
