"""
FILE: AI_infrastructure/utils/user_context_builder.py
PURPOSE: Build comprehensive user context (personal, geographic, temporal, preference-based)

DEPENDENCIES:
- user_preferences_routes.get_user_preferences() - Load user preferences
- geolocation_service.build_geolocation_context() - Get location and temporal data
- sqlite3 - Database access

EXPORTS:
- build_user_context(user_id, ip_address) -> dict - Build complete user context
- format_context_for_system_prompt(context) -> str - Format context for AI system prompt

USED BY:
- agent_routes_v4.py (inject before agent execution)
- context_aware_ai.py (enhance system prompt)

RELATED FILES:
- AI_infrastructure/routes/user_preferences_routes.py (load preferences)
- AI_infrastructure/utils/geolocation_service.py (location + temporal)
- AI_infrastructure/routes/agent_routes_v4.py (inject context)

NOTES:
- Combines 5 dimensions: personal, platform, geographic, temporal, preference
- Preferences are optional (graceful fallback to defaults)
- Geolocation auto-injected (no user setup needed)
- Called before every agent execution

LAST MODIFIED: 2025-01-XX - Initial implementation
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def build_user_context(user_id: int, ip_address: Optional[str] = None) -> Dict:
    """
    Build comprehensive user context from user ID and IP address
    
    Combines:
    1. Personal: user_id, username, email
    2. Platform: auth platform (Microsoft/Google), connection status
    3. Geographic: country, city, timezone (from IP)
    4. Temporal: time_of_day, day_of_week, season, work hours
    5. Preferences: communication_style, detail_level, preferred_tools
    
    Args:
        user_id (int): User ID
        ip_address (str): Client IP address for geolocation (optional)
    
    Returns:
        dict with complete user context structure:
        {
            'user_id': 1,
            'personal': {
                'user_id': 1,
                'username': 'john_doe',
                'email': 'john@example.com'
            },
            'authentication': {
                'platform': 'microsoft',  # or 'google'
                'status': 'connected',
                'platforms_available': ['microsoft', 'google']
            },
            'geographic': {
                'country': 'US',
                'city': 'New York',
                'timezone': 'America/New_York'
            },
            'temporal': {
                'current_time': '2025-01-15 14:30:00 EST',
                'time_of_day': 'afternoon',
                'day_of_week': 'Wednesday',
                'is_work_hours': True,
                'season': 'Winter'
            },
            'preferences': {
                'communication_style': 'professional',
                'detail_level': 'standard',
                'auth_platform': 'auto'
            },
            'context_message': '...'  # Human-readable context summary
        }
    """
    try:
        # Import here to avoid circular imports
        from routes.user_preferences_routes import get_user_preferences
        from utils.geolocation_service import build_geolocation_context
        
        context = {
            'user_id': user_id,
            'personal': {},
            'authentication': {},
            'geographic': {},
            'temporal': {},
            'preferences': {},
            'context_message': '',
            'success': False
        }
        
        # 1. Load user personal data
        try:
            from pathlib import Path
            import sqlite3
            import sys
            
            # Add parent directory for imports
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from shared.database_utils import get_database_connection
            
            conn = get_database_connection('ai_infrastructure')
            if hasattr(conn, 'row_factory'):  # SQLite
                conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, created_at
                FROM users
                WHERE id = ?
            """, (user_id,))
            
            user_row = cursor.fetchone()
            if user_row:
                context['personal'] = {
                    'user_id': user_row['id'],
                    'username': user_row['username'],
                    'email': user_row['email']
                }
            
            # 2. Load user authentication status
            cursor.execute("""
                SELECT platform, is_connected
                FROM user_platform_credentials
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,))
            
            auth_platforms = []
            connected_platforms = []
            for row in cursor.fetchall():
                platform = row['platform']
                if row['is_connected']:
                    connected_platforms.append(platform)
                auth_platforms.append(platform)
            
            context['authentication'] = {
                'platforms_available': list(set(auth_platforms)),  # Unique list
                'platforms_connected': connected_platforms,
                'primary_platform': connected_platforms[0] if connected_platforms else 'none'
            }
            
            conn.close()
        except Exception as e:
            logger.warning(f"Could not load personal data for user {user_id}: {e}")
        
        # 3. Load user preferences
        try:
            prefs = get_user_preferences(user_id)
            if prefs:
                context['preferences'] = {
                    'communication_style': prefs.get('communication_style', 'professional'),
                    'detail_level': prefs.get('detail_level', 'standard'),
                    'auth_platform': prefs.get('auth_platform', 'auto'),
                    'preferred_tools': prefs.get('preferred_tools', '')
                }
            else:
                # Use defaults if no preferences saved
                context['preferences'] = {
                    'communication_style': 'professional',
                    'detail_level': 'standard',
                    'auth_platform': 'auto',
                    'preferred_tools': ''
                }
        except Exception as e:
            logger.warning(f"Could not load preferences for user {user_id}: {e}")
            context['preferences'] = {
                'communication_style': 'professional',
                'detail_level': 'standard',
                'auth_platform': 'auto',
                'preferred_tools': ''
            }
        
        # 4. Get geolocation and temporal context
        if ip_address:
            try:
                geo_context = build_geolocation_context(ip_address)
                if geo_context and geo_context.get('success'):
                    context['geographic'] = {
                        'ip': geo_context.get('ip'),
                        'country': geo_context['location'].get('country', 'Unknown'),
                        'city': geo_context['location'].get('city', 'Unknown'),
                        'timezone': geo_context['location'].get('timezone', 'UTC')
                    }
                    context['temporal'] = {
                        'current_time': geo_context['temporal'].get('current_time'),
                        'time_of_day': geo_context['temporal'].get('time_of_day'),
                        'day_of_week': geo_context['temporal'].get('day_of_week'),
                        'is_work_hours': geo_context['temporal'].get('is_work_hours'),
                        'hour': geo_context['temporal'].get('hour'),
                        'date': geo_context['temporal'].get('date'),
                        'season': geo_context['temporal'].get('season'),
                        'is_weekend': geo_context['temporal'].get('is_weekend')
                    }
            except Exception as e:
                logger.warning(f"Could not get geolocation for IP {ip_address}: {e}")
        
        # 5. Build context message
        username = context['personal'].get('username', 'User')
        city = context['geographic'].get('city', 'Unknown location')
        country = context['geographic'].get('country', '')
        time_of_day = context['temporal'].get('time_of_day', 'unknown time')
        day = context['temporal'].get('day_of_week', 'unknown day')
        is_work_hours = context['temporal'].get('is_work_hours')
        season = context['temporal'].get('season', 'unknown season')
        comm_style = context['preferences'].get('communication_style', 'professional')
        detail_level = context['preferences'].get('detail_level', 'standard')
        
        work_status = "during work hours" if is_work_hours else "outside work hours"
        
        context_message = (
            f"User: {username} from {city}, {country}. "
            f"Current time: {time_of_day} on {day} ({work_status}, {season}). "
            f"Preferences: {comm_style} tone, {detail_level} detail level."
        )
        
        context['context_message'] = context_message
        context['success'] = True
        
        return context
        
    except Exception as e:
        logger.error(f"Error building user context for user {user_id}: {str(e)}")
        return {
            'user_id': user_id,
            'personal': {},
            'authentication': {},
            'geographic': {},
            'temporal': {},
            'preferences': {},
            'context_message': '',
            'success': False,
            'error': str(e)
        }


def format_context_for_system_prompt(context: Dict) -> str:
    """
    Format user context as a system prompt injection
    
    Creates a string that can be injected into the system prompt to make the AI
    aware of the user's context
    
    Args:
        context (dict): User context dict from build_user_context()
    
    Returns:
        str: Formatted context for system prompt
        
    Example output:
    ```
    USER CONTEXT:
    - Location: New York, US (timezone: America/New_York)
    - Time: 2:30 PM EST on Wednesday (work hours, Winter)
    - Communication style: Professional, Standard detail
    - Connected platforms: Microsoft 365, Google Workspace
    
    Tailor your responses to the user's current context and preferences.
    ```
    """
    try:
        if not context or not context.get('success'):
            return ""
        
        personal = context.get('personal', {})
        auth = context.get('authentication', {})
        geographic = context.get('geographic', {})
        temporal = context.get('temporal', {})
        preferences = context.get('preferences', {})
        
        # Build formatted context
        lines = ["USER CONTEXT:", ""]
        
        # Location
        if geographic.get('city'):
            tz = geographic.get('timezone', 'Unknown')
            lines.append(f"- Location: {geographic['city']}, {geographic.get('country', '')} (timezone: {tz})")
        
        # Time
        if temporal.get('current_time'):
            time_str = temporal['current_time']
            day = temporal.get('day_of_week', '')
            work_hours = "work hours" if temporal.get('is_work_hours') else "outside work hours"
            season = temporal.get('season', '')
            lines.append(f"- Time: {time_str} on {day} ({work_hours}, {season})")
        
        # Preferences
        if preferences:
            comm_style = preferences.get('communication_style', 'professional')
            detail = preferences.get('detail_level', 'standard')
            lines.append(f"- Communication style: {comm_style.capitalize()}, {detail.capitalize()} detail level")
        
        # Connected platforms
        if auth.get('platforms_connected'):
            platforms = ', '.join(auth['platforms_connected'])
            lines.append(f"- Connected platforms: {platforms}")
        
        lines.append("")
        lines.append("Tailor your responses to the user's current context and preferences.")
        
        return '\n'.join(lines)
        
    except Exception as e:
        logger.error(f"Error formatting context for system prompt: {str(e)}")
        return ""


# For testing
if __name__ == '__main__':
    # Test building user context
    context = build_user_context(user_id=1, ip_address='8.8.8.8')
    
    import json
    print("Full Context:")
    print(json.dumps({k: v for k, v in context.items() if k != 'context_message'}, indent=2, default=str))
    
    print("\n\nFormatted for System Prompt:")
    print(format_context_for_system_prompt(context))
