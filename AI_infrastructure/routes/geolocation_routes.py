"""
FILE: AI_infrastructure/routes/geolocation_routes.py
PURPOSE: Geolocation detection API endpoints for user context awareness

DEPENDENCIES:
- flask - Blueprint routing
- core.ip_location - Consolidated IP geolocation utilities

EXPORTS:
- geolocation_bp - Flask Blueprint with geolocation detection endpoints

USED BY:
- AI_infrastructure/flask_app.py (register blueprint)
- UI/business-ai-platform-v2.html (AJAX calls to detect user location)

RELATED FILES:
- AI_infrastructure/core/ip_location.py (consolidated geolocation logic)
- AI_infrastructure/routes/user_preferences_routes.py (store detected location)

NOTES:
- Automatically detects user location from IP address
- Returns country, city, timezone, and temporal context
- Falls back to default timezone if IP lookup fails
- Now uses consolidated ip_location.py instead of separate geolocation_service

LAST MODIFIED: 2025-11-05 - Updated to use consolidated ip_location.py
"""

from flask import Blueprint, request, jsonify
import logging
from AI_infrastructure.core.ip_location import get_location_from_ip, get_temporal_awareness, build_geolocation_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

geolocation_bp = Blueprint('geolocation', __name__, url_prefix='/api/geolocation')


@geolocation_bp.route('/detect', methods=['GET'])
def detect_location():
    """
    GET /api/geolocation/detect
    
    Detect user's geographic location and timezone from IP address
    
    Query Parameters:
    - ip: (optional) Override IP address for testing
    
    Returns:
    {
        "success": true,
        "data": {
            "ip": "8.8.8.8",
            "country": "US",
            "country_name": "United States",
            "city": "Mountain View",
            "timezone": "America/Los_Angeles",
            "time_of_day": "afternoon",
            "day_of_week": "Tuesday",
            "is_work_hours": true,
            "current_time": "2025-11-05 14:30:00"
        }
    }
    """
    try:
        # Get IP address from query param or request
        ip_address = request.args.get('ip')
        
        if not ip_address:
            # Try to get IP from X-Forwarded-For header (if behind proxy)
            ip_address = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        
        if not ip_address:
            # Fall back to remote_addr
            ip_address = request.remote_addr
        
        logger.info(f"Detecting location for IP: {ip_address}")
        
        # Get location data
        location_data = get_location_from_ip(ip_address)
        
        if not location_data:
            # Return default if geolocation fails
            return jsonify({
                'success': True,
                'data': {
                    'ip': ip_address,
                    'country': 'US',
                    'country_name': 'United States',
                    'city': 'Unknown',
                    'timezone': 'America/New_York',
                    'time_of_day': 'unknown',
                    'day_of_week': 'unknown',
                    'is_work_hours': False,
                    'current_time': ''
                },
                'message': 'Could not detect precise location, using defaults'
            }), 200
        
        # Get temporal awareness (time of day, work hours, etc.)
        timezone_str = location_data.get('timezone', 'America/New_York')
        temporal_data = get_temporal_awareness(timezone_str)
        
        # Combine location and temporal data
        response_data = {
            **location_data,
            **temporal_data
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error detecting location: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to detect location: {str(e)}',
            'data': {
                'ip': request.remote_addr,
                'country': 'US',
                'country_name': 'United States',
                'city': 'Unknown',
                'timezone': 'America/New_York',
                'time_of_day': 'unknown',
                'day_of_week': 'unknown',
                'is_work_hours': False,
                'current_time': ''
            }
        }), 200  # Return 200 with default data instead of 500


@geolocation_bp.route('/timezone/<timezone_name>', methods=['GET'])
def get_timezone_info(timezone_name):
    """
    GET /api/geolocation/timezone/<timezone_name>
    
    Get temporal awareness for a specific timezone
    
    Example: /api/geolocation/timezone/America/New_York
    
    Returns:
    {
        "success": true,
        "data": {
            "timezone": "America/New_York",
            "current_time": "2025-11-05 14:30:00",
            "time_of_day": "afternoon",
            "day_of_week": "Tuesday",
            "is_work_hours": true,
            "season": "autumn"
        }
    }
    """
    try:
        temporal_data = get_temporal_awareness(timezone_name)
        
        return jsonify({
            'success': True,
            'data': temporal_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting timezone info: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get timezone info: {str(e)}'
        }), 500
