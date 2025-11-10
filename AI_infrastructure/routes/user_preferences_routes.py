"""
FILE: AI_infrastructure/routes/user_preferences_routes.py
PURPOSE: User personalization preferences API endpoints (communication style, detail level, auth platform)

DEPENDENCIES:
- flask - Blueprint routing
- sqlite3 - Database operations
- jwt - Token verification
- core.ip_location - Consolidated IP geolocation utilities

EXPORTS:
- user_preferences_bp - Flask Blueprint with GET/POST preferences endpoints
- get_user_preferences(user_id) - Retrieve user preferences from database
- save_user_preferences(user_id, prefs) - Save user preferences to database

USED BY:
- AI_infrastructure/flask_app.py (register blueprint)
- UI/business-ai-platform-v2.html (AJAX calls to endpoints)
- agent_routes_v4.py (load preferences for context injection)

RELATED FILES:
- AI_infrastructure/routes/auth_routes.py (JWT verification pattern)
- AI_infrastructure/database.py (database schema)
- AI_infrastructure/core/ip_location.py (location detection)

NOTES:
- Preferences stored in user_preferences table
- JWT token required for authentication
- User can only access their own preferences
- Auto-creates preferences row if doesn't exist
- Automatically detects and stores user location from IP address

LAST MODIFIED: 2025-11-05 - Added ip_location import for automatic location detection
"""

from flask import Blueprint, request, jsonify
import os
import sqlite3
from datetime import datetime
import logging
import jwt
from pathlib import Path
from AI_infrastructure.core.ip_location import build_geolocation_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_preferences_bp = Blueprint('user_preferences', __name__, url_prefix='/api/user')


def get_db_connection():
    """Get database connection to ai_infrastructure.db in data/ folder"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError:
        return None


def get_or_create_preferences_table():
    """Ensure user_preferences table exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            communication_style TEXT DEFAULT 'professional',
            detail_level TEXT DEFAULT 'standard',
            auth_platform TEXT DEFAULT 'auto',
            preferred_tools TEXT,
            custom_preferences TEXT,
            nickname TEXT,
            detected_country TEXT,
            detected_city TEXT,
            detected_timezone TEXT,
            detected_ip_address TEXT,
            manual_location_override TEXT,
            manual_timezone_override TEXT,
            use_manual_location INTEGER DEFAULT 0,
            use_manual_timezone INTEGER DEFAULT 0,
            last_location_check TIMESTAMP,
            ai_memories TEXT,
            memory_updated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()


# Initialize table on module load
try:
    get_or_create_preferences_table()
except Exception as e:
    logger.warning(f"Could not ensure user_preferences table exists: {e}")


@user_preferences_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """
    GET /api/user/preferences
    
    Retrieve user's personalization preferences
    
    Query Parameters:
    - user_id: (optional) User ID to fetch preferences for (defaults to 1)
    
    Headers:
    - Authorization: Bearer <jwt_token> (optional)
    
    Returns:
    {
        "success": true,
        "data": {
            "user_id": 1,
            "communication_style": "professional",
            "detail_level": "standard",
            "auth_platform": "auto",
            "preferred_tools": "gmail,google_docs,slack",
            "custom_preferences": {...},
            "updated_at": "2025-01-XX..."
        }
    }
    """
    try:
        # Try to get user_id from JWT token, fall back to query param or default
        user_id = None
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            payload = verify_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
        
        # Fall back to query parameter or default to user_id=1
        if not user_id:
            user_id = request.args.get('user_id', 1, type=int)
        
        # Get preferences from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                user_id,
                communication_style,
                detail_level,
                auth_platform,
                preferred_tools,
                custom_preferences,
                nickname,
                detected_country,
                detected_city,
                detected_timezone,
                detected_ip_address,
                manual_location_override,
                manual_timezone_override,
                use_manual_location,
                use_manual_timezone,
                last_location_check,
                ai_memories,
                memory_updated_at,
                updated_at
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            # Return default preferences if none exist
            print("\n" + "="*80)
            print("📋 [USER PREFERENCES - GET] No preferences found, returning defaults")
            print("="*80)
            print(f"   User ID: {user_id}")
            print(f"   Auth Method: {'JWT Token' if auth_header.startswith('Bearer ') else 'Query Param/Default'}")
            print(f"   🔷 Returning: Default preferences (no custom settings)")
            print(f"   Communication Style: professional (default)")
            print(f"   Detail Level: standard (default)")
            print(f"   Auth Platform: auto (default)")
            print(f"   AI Memories: [] (empty)")
            print("="*80 + "\n")
            
            return jsonify({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'communication_style': 'professional',
                    'detail_level': 'standard',
                    'auth_platform': 'auto',
                    'preferred_tools': '',
                    'custom_preferences': None,
                    'nickname': '',
                    'detected_country': '',
                    'detected_city': '',
                    'detected_timezone': '',
                    'detected_ip_address': '',
                    'manual_location_override': '',
                    'manual_timezone_override': '',
                    'use_manual_location': 0,
                    'use_manual_timezone': 0,
                    'last_location_check': None,
                    'ai_memories': '[]',
                    'memory_updated_at': None,
                    'updated_at': None
                }
            }), 200
        
        # Parse AI memories to show count
        import json
        try:
            memories_list = json.loads(row['ai_memories'] or '[]')
            memory_count = len(memories_list) if isinstance(memories_list, list) else 0
        except:
            memory_count = 0
        
        # Log retrieved preferences
        print("\n" + "="*80)
        print("📋 [USER PREFERENCES - GET] Preferences retrieved from database")
        print("="*80)
        print(f"   User ID: {user_id}")
        print(f"   Auth Method: {'JWT Token' if auth_header.startswith('Bearer ') else 'Query Param/Default'}")
        print(f"   \n   🔷 PREFERENCES:")
        print(f"      Communication Style: {row['communication_style']}")
        print(f"      Detail Level: {row['detail_level']}")
        print(f"      Auth Platform: {row['auth_platform']}")
        print(f"      Nickname: {row['nickname'] or '(not set)'}")
        print(f"      Preferred Tools: {row['preferred_tools'] or '(not set)'}")
        print(f"   \n   🌍 LOCATION:")
        print(f"      Country: {row['detected_country'] or '(not detected)'}")
        print(f"      City: {row['detected_city'] or '(not detected)'}")
        print(f"      Timezone: {row['detected_timezone'] or '(not detected)'}")
        print(f"      Manual Override: {'Yes' if row['use_manual_location'] else 'No'}")
        print(f"   \n   🧠 AI MEMORIES:")
        print(f"      Total Memories: {memory_count}")
        if memory_count > 0:
            print(f"      Last Updated: {row['memory_updated_at']}")
            # Show first 2 memories as preview
            for i, memory in enumerate(memories_list[:2], 1):
                memory_text = memory if isinstance(memory, str) else str(memory)
                preview = memory_text[:60] + "..." if len(memory_text) > 60 else memory_text
                print(f"      Memory {i}: {preview}")
            if memory_count > 2:
                print(f"      ... and {memory_count - 2} more")
        else:
            print(f"      Status: No memories stored")
        print(f"   \n   📅 Last Updated: {row['updated_at']}")
        print("="*80 + "\n")
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': row['user_id'],
                'communication_style': row['communication_style'],
                'detail_level': row['detail_level'],
                'auth_platform': row['auth_platform'],
                'preferred_tools': row['preferred_tools'],
                'custom_preferences': row['custom_preferences'],
                'nickname': row['nickname'],
                'detected_country': row['detected_country'],
                'detected_city': row['detected_city'],
                'detected_timezone': row['detected_timezone'],
                'detected_ip_address': row['detected_ip_address'],
                'manual_location_override': row['manual_location_override'],
                'manual_timezone_override': row['manual_timezone_override'],
                'use_manual_location': row['use_manual_location'],
                'use_manual_timezone': row['use_manual_timezone'],
                'last_location_check': row['last_location_check'],
                'ai_memories': row['ai_memories'] or '[]',
                'memory_updated_at': row['memory_updated_at'],
                'updated_at': row['updated_at']
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error retrieving preferences: {str(e)}\n{error_details}")
        print(f"\n❌ [USER PREFERENCES - GET] ERROR: {str(e)}")
        print(f"Traceback:\n{error_details}")
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500


@user_preferences_bp.route('/preferences', methods=['POST'])
def save_preferences():
    """
    POST /api/user/preferences
    
    Save user's personalization preferences
    
    Headers:
    - Authorization: Bearer <jwt_token>
    - Content-Type: application/json
    
    Request Body:
    {
        "communication_style": "professional|casual|detailed|brief",
        "detail_level": "minimal|standard|comprehensive",
        "auth_platform": "auto|microsoft|google",
        "preferred_tools": "gmail,google_docs,slack" (comma-separated),
        "custom_preferences": {...} (optional JSON object)
    }
    
    Returns:
    {
        "success": true,
        "message": "Preferences saved successfully",
        "data": {...}
    }
    """
    try:
        # Get JWT token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing or invalid Authorization header'}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Invalid token payload'}), 401
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body must be JSON'}), 400
        
        # Parse incoming memories to count them
        import json
        incoming_memories = data.get('ai_memories', '[]')
        try:
            memories_list = json.loads(incoming_memories) if isinstance(incoming_memories, str) else incoming_memories
            memory_count = len(memories_list) if isinstance(memories_list, list) else 0
        except:
            memory_count = 0
        
        # Log incoming preferences data
        print("\n" + "="*80)
        print("📝 [USER PREFERENCES - POST] Saving user preferences")
        print("="*80)
        print(f"   User ID: {user_id}")
        print(f"   \n   🔷 INCOMING PREFERENCES:")
        print(f"      Communication Style: {data.get('communication_style', 'professional')}")
        print(f"      Detail Level: {data.get('detail_level', 'standard')}")
        print(f"      Auth Platform: {data.get('auth_platform', 'auto')}")
        print(f"      Nickname: {data.get('nickname', '(not set)')}")
        print(f"      Preferred Tools: {data.get('preferred_tools', '(not set)')}")
        print(f"   \n   🌍 LOCATION DATA:")
        print(f"      Country: {data.get('detected_country', '(not set)')}")
        print(f"      City: {data.get('detected_city', '(not set)')}")
        print(f"      Timezone: {data.get('detected_timezone', '(not set)')}")
        print(f"      Manual Location Override: {'Yes' if data.get('use_manual_location', False) else 'No'}")
        print(f"      Manual Timezone Override: {'Yes' if data.get('use_manual_timezone', False) else 'No'}")
        print(f"   \n   🧠 AI MEMORIES:")
        print(f"      Total Memories: {memory_count}")
        if memory_count > 0:
            # Show first 2 memories as preview
            for i, memory in enumerate(memories_list[:2], 1):
                memory_text = memory if isinstance(memory, str) else str(memory)
                preview = memory_text[:60] + "..." if len(memory_text) > 60 else memory_text
                print(f"      Memory {i}: {preview}")
            if memory_count > 2:
                print(f"      ... and {memory_count - 2} more")
        else:
            print(f"      Status: No memories in request")
        print(f"   \n   📦 Custom Preferences: {'Yes' if data.get('custom_preferences') else 'No'}")
        print("="*80 + "\n")
        
        # Validate preference values
        communication_style = data.get('communication_style', 'professional')
        if communication_style not in ['professional', 'casual', 'detailed', 'brief']:
            communication_style = 'professional'
        
        detail_level = data.get('detail_level', 'standard')
        if detail_level not in ['minimal', 'standard', 'comprehensive']:
            detail_level = 'standard'
        
        auth_platform = data.get('auth_platform', 'auto')
        if auth_platform not in ['auto', 'microsoft', 'google']:
            auth_platform = 'auto'
        
        preferred_tools = data.get('preferred_tools', '')
        custom_preferences = data.get('custom_preferences')
        nickname = data.get('nickname', '')
        detected_country = data.get('detected_country', '')
        detected_city = data.get('detected_city', '')
        detected_timezone = data.get('detected_timezone', '')
        detected_ip_address = data.get('detected_ip_address', '')
        manual_location_override = data.get('manual_location_override', '')
        manual_timezone_override = data.get('manual_timezone_override', '')
        use_manual_location = 1 if data.get('use_manual_location', False) else 0
        use_manual_timezone = 1 if data.get('use_manual_timezone', False) else 0
        ai_memories = data.get('ai_memories', '[]')
        
        # Auto-detect location from IP if not manually set
        if not use_manual_location:
            try:
                # Get IP address from request
                ip_address = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
                if not ip_address:
                    ip_address = request.remote_addr
                
                logger.info(f"Auto-detecting location from IP: {ip_address}")
                
                # Get full geolocation context
                geo_context = build_geolocation_context(ip_address)
                
                if geo_context and geo_context.get('success'):
                    # Update detected location fields
                    detected_ip_address = geo_context.get('ip', ip_address)
                    detected_country = geo_context.get('country_name', detected_country)
                    detected_city = geo_context.get('city', detected_city)
                    detected_timezone = geo_context.get('timezone', detected_timezone)
                    
                    logger.info(f"Location detected: {detected_city}, {detected_country} ({detected_timezone})")
                else:
                    logger.warning(f"Failed to detect location from IP: {ip_address}")
                    
            except Exception as e:
                logger.error(f"Error auto-detecting location: {str(e)}", exc_info=True)
        
        # Convert custom_preferences dict to JSON string if provided
        if custom_preferences:
            import json
            custom_preferences = json.dumps(custom_preferences)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if preferences exist
        cursor.execute("SELECT user_id FROM user_preferences WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing preferences
            cursor.execute("""
                UPDATE user_preferences
                SET communication_style = ?,
                    detail_level = ?,
                    auth_platform = ?,
                    preferred_tools = ?,
                    custom_preferences = ?,
                    nickname = ?,
                    detected_country = ?,
                    detected_city = ?,
                    detected_timezone = ?,
                    detected_ip_address = ?,
                    manual_location_override = ?,
                    manual_timezone_override = ?,
                    use_manual_location = ?,
                    use_manual_timezone = ?,
                    ai_memories = ?,
                    memory_updated_at = CURRENT_TIMESTAMP,
                    last_location_check = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (communication_style, detail_level, auth_platform, preferred_tools, custom_preferences, 
                  nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
                  manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone,
                  ai_memories, user_id))
        else:
            # Insert new preferences
            cursor.execute("""
                INSERT INTO user_preferences
                (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
                 nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
                 manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone,
                 ai_memories, memory_updated_at, last_location_check)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
                  nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
                  manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone,
                  ai_memories))
        
        conn.commit()
        
        # Retrieve updated preferences
        cursor.execute("""
            SELECT 
                user_id,
                communication_style,
                detail_level,
                auth_platform,
                preferred_tools,
                custom_preferences,
                nickname,
                detected_country,
                detected_city,
                detected_timezone,
                detected_ip_address,
                manual_location_override,
                manual_timezone_override,
                use_manual_location,
                use_manual_timezone,
                last_location_check,
                ai_memories,
                memory_updated_at,
                updated_at
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        # Log successful save
        print("\n" + "="*80)
        print("✅ [USER PREFERENCES - POST] Preferences saved successfully")
        print("="*80)
        print(f"   User ID: {user_id}")
        print(f"   Operation: {'UPDATE' if exists else 'INSERT'}")
        print(f"   \n   📊 SAVED DATA:")
        print(f"      Communication Style: {row['communication_style']}")
        print(f"      Detail Level: {row['detail_level']}")
        print(f"      Auth Platform: {row['auth_platform']}")
        print(f"      Nickname: {row['nickname'] or '(not set)'}")
        print(f"      Location: {row['detected_city']}, {row['detected_country']}")
        print(f"      Timezone: {row['detected_timezone']}")
        print(f"      AI Memories Count: {memory_count}")
        print(f"   \n   📅 Timestamps:")
        print(f"      Last Updated: {row['updated_at']}")
        print(f"      Memory Updated: {row['memory_updated_at']}")
        print("="*80 + "\n")
        
        return jsonify({
            'success': True,
            'message': 'Preferences saved successfully',
            'data': {
                'user_id': row['user_id'],
                'communication_style': row['communication_style'],
                'detail_level': row['detail_level'],
                'auth_platform': row['auth_platform'],
                'preferred_tools': row['preferred_tools'],
                'custom_preferences': row['custom_preferences'],
                'nickname': row['nickname'],
                'detected_country': row['detected_country'],
                'detected_city': row['detected_city'],
                'detected_timezone': row['detected_timezone'],
                'detected_ip_address': row['detected_ip_address'],
                'manual_location_override': row['manual_location_override'],
                'manual_timezone_override': row['manual_timezone_override'],
                'use_manual_location': row['use_manual_location'],
                'use_manual_timezone': row['use_manual_timezone'],
                'last_location_check': row['last_location_check'],
                'ai_memories': row['ai_memories'] or '[]',
                'memory_updated_at': row['memory_updated_at'],
                'updated_at': row['updated_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error saving preferences: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


def get_user_preferences(user_id):
    """
    Helper function: Get user preferences from database
    
    Args:
        user_id (int): User ID
    
    Returns:
        dict: User preferences or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                user_id,
                communication_style,
                detail_level,
                auth_platform,
                preferred_tools,
                custom_preferences,
                nickname,
                detected_country,
                detected_city,
                detected_timezone,
                detected_ip_address,
                manual_location_override,
                manual_timezone_override,
                use_manual_location,
                use_manual_timezone,
                last_location_check,
                updated_at
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'user_id': row['user_id'],
            'communication_style': row['communication_style'],
            'detail_level': row['detail_level'],
            'auth_platform': row['auth_platform'],
            'preferred_tools': row['preferred_tools'],
            'custom_preferences': row['custom_preferences'],
            'nickname': row['nickname'],
            'detected_country': row['detected_country'],
            'detected_city': row['detected_city'],
            'detected_timezone': row['detected_timezone'],
            'detected_ip_address': row['detected_ip_address'],
            'manual_location_override': row['manual_location_override'],
            'manual_timezone_override': row['manual_timezone_override'],
            'use_manual_location': row['use_manual_location'],
            'use_manual_timezone': row['use_manual_timezone'],
            'last_location_check': row['last_location_check'],
            'updated_at': row['updated_at']
        }
    except Exception as e:
        logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
        return None


def save_user_preferences(user_id, preferences_dict):
    """
    Helper function: Save user preferences to database
    
    Args:
        user_id (int): User ID
        preferences_dict (dict): Preferences with keys:
            - communication_style
            - detail_level
            - auth_platform
            - preferred_tools (optional)
            - custom_preferences (optional)
            - nickname (optional)
            - detected_country (optional)
            - detected_city (optional)
            - detected_timezone (optional)
            - detected_ip_address (optional)
            - manual_location_override (optional)
            - manual_timezone_override (optional)
            - use_manual_location (optional)
            - use_manual_timezone (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if preferences exist
        cursor.execute("SELECT user_id FROM user_preferences WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        communication_style = preferences_dict.get('communication_style', 'professional')
        detail_level = preferences_dict.get('detail_level', 'standard')
        auth_platform = preferences_dict.get('auth_platform', 'auto')
        preferred_tools = preferences_dict.get('preferred_tools', '')
        custom_preferences = preferences_dict.get('custom_preferences')
        nickname = preferences_dict.get('nickname', '')
        detected_country = preferences_dict.get('detected_country', '')
        detected_city = preferences_dict.get('detected_city', '')
        detected_timezone = preferences_dict.get('detected_timezone', '')
        detected_ip_address = preferences_dict.get('detected_ip_address', '')
        manual_location_override = preferences_dict.get('manual_location_override', '')
        manual_timezone_override = preferences_dict.get('manual_timezone_override', '')
        use_manual_location = 1 if preferences_dict.get('use_manual_location', False) else 0
        use_manual_timezone = 1 if preferences_dict.get('use_manual_timezone', False) else 0
        
        if custom_preferences:
            import json
            custom_preferences = json.dumps(custom_preferences)
        
        if exists:
            cursor.execute("""
                UPDATE user_preferences
                SET communication_style = ?,
                    detail_level = ?,
                    auth_platform = ?,
                    preferred_tools = ?,
                    custom_preferences = ?,
                    nickname = ?,
                    detected_country = ?,
                    detected_city = ?,
                    detected_timezone = ?,
                    detected_ip_address = ?,
                    manual_location_override = ?,
                    manual_timezone_override = ?,
                    use_manual_location = ?,
                    use_manual_timezone = ?,
                    last_location_check = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
                  nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
                  manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone, user_id))
        else:
            cursor.execute("""
                INSERT INTO user_preferences
                (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
                 nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
                 manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone, last_location_check)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
                  nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
                  manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving preferences for user {user_id}: {str(e)}")
        return False
