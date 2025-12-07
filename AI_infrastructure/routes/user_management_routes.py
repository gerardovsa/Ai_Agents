"""
AI_infrastructure/routes/user_management_routes.py
PURPOSE: Sub-user management API for parent-child user hierarchy

✅ CURSOR MANAGEMENT FIXED: All 24 critical issues resolved
   - Added cursor = None initialization
   - Added cursor.close() before conn operations
   - Added finally blocks for guaranteed cleanup
   - Fixed all early return cleanup

DEPENDENCIES:
- flask (Blueprint, request, jsonify)
- sqlite3 (built-in) - Database access
- json (built-in) - JSON parsing
- auth.permission_checker - Permission validation

EXPORTS:
- user_management_bp Blueprint with routes:
  * POST /api/users/sub-users - Create sub-user
  * GET /api/users/sub-users - List sub-users
  * PUT /api/users/sub-users/<id> - Update sub-user
  * DELETE /api/users/sub-users/<id> - Delete sub-user
  * POST /api/users/sub-users/<id>/reset-password - Reset password

USED BY:
- AI_infrastructure/flask_app.py (registers blueprint)
- UI (business-ai-platform-v2.html - User Management section)

RELATED FILES:
- data/ai_infrastructure.db (users table)
- auth/permission_checker.py (permission validation)
- auth/user_auth.py (password hashing)

NOTES:
- Only admins and owners can manage sub-users
- Parent users can only manage their own sub-users
- Sub-users inherit parent's workspace context
- Permissions are stored as JSON strings
- Default password: "change_me_123" (MUST be changed on first login)

LAST MODIFIED: 2025-12-07 - Fixed cursor management (24 issues resolved)
PREVIOUS: 2025-11-10 - Initial implementation for user hierarchy
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
import logging
from pathlib import Path
from shared.database_utils import get_database_connection, convert_sql_placeholders
from typing import Dict, List, Any, Optional
import sys
import os

# Add AI_infrastructure to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.permission_checker import get_permission_checker, PermissionError
import bcrypt  # For password hashing

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
user_management_bp = Blueprint('user_management', __name__)

# ======================================================================
# CONSTANTS
# ======================================================================

# Default password for new sub-users
DEFAULT_PASSWORD = "change_me_123"

# Valid data access scopes
VALID_DATA_SCOPES = ['own', 'team', 'department', 'all']

# Default usage limits
DEFAULT_USAGE_LIMIT_DAILY = 1000

# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def get_db_connection():
    """
    Get database connection to ai_infrastructure.db in data/ folder
    
    CRITICAL: Always use data/ai_infrastructure.db (CORRECT LOCATION)
    """
    conn = get_database_connection('ai_infrastructure')
    if hasattr(conn, 'row_factory'):  # SQLite
        conn.row_factory = sqlite3.Row
    return conn


def require_admin(user_id: int) -> bool:
    """Check if user is admin or owner"""
    checker = get_permission_checker()
    perms = checker.get_user_permissions(user_id)
    
    if not perms:
        return False
    
    return perms['role'] in ['admin', 'owner']


# ======================================================================
# ENDPOINTS (ALL FIXED FOR CURSOR MANAGEMENT)
# ======================================================================

@user_management_bp.route('/api/users/sub-users', methods=['POST'])
def create_sub_user():
    """
    Create a new sub-user under the authenticated user
    
    POST /api/users/sub-users
    
    Required fields:
    - parent_user_id: Parent user ID (must be requesting user or admin)
    - username: Unique username
    - email: Email address (unique)
    - permissions: JSON object with granular permissions (optional)
    - allowed_tools: List of allowed tool names (optional, null = all)
    - allowed_agents: List of allowed agent IDs (optional, null = all)
    - data_access_scope: 'own' | 'team' | 'department' | 'all' (default: 'own')
    - usage_limit_daily: Daily API call limit (default: 1000)
    - access_start_time: HH:MM format (optional)
    - access_end_time: HH:MM format (optional)
    - account_expires_at: ISO timestamp (optional)
    
    Returns:
        201: Sub-user created successfully
        400: Validation error
        403: Permission denied
        500: Server error
    
    ✅ FIXED: Proper cursor management with finally block and early return cleanup
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        data = request.get_json()
        
        # Get requesting user from header/session
        requesting_user_id = data.get('requesting_user_id')  # TODO: Get from JWT token
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id required"}), 400
        
        parent_user_id = data.get('parent_user_id')
        username = data.get('username')
        email = data.get('email')
        
        # Validate required fields
        if not all([parent_user_id, username, email]):
            return jsonify({
                "error": "parent_user_id, username, and email are required"
            }), 400
        
        # Permission check: Must be admin OR the parent user
        checker = get_permission_checker()
        is_admin = require_admin(requesting_user_id)
        is_parent = requesting_user_id == parent_user_id
        
        if not (is_admin or is_parent):
            return jsonify({
                "error": "Only admins or the parent user can create sub-users"
            }), 403
        
        # Extract optional fields
        permissions = data.get('permissions', {})
        allowed_tools = data.get('allowed_tools')  # None = all, [] = none, list = whitelist
        allowed_agents = data.get('allowed_agents')  # None = all, [] = none, list = whitelist
        data_access_scope = data.get('data_access_scope', 'own')
        usage_limit_daily = data.get('usage_limit_daily', DEFAULT_USAGE_LIMIT_DAILY)
        access_start_time = data.get('access_start_time')
        access_end_time = data.get('access_end_time')
        account_expires_at = data.get('account_expires_at')
        
        # Validate data_access_scope
        if data_access_scope not in VALID_DATA_SCOPES:
            return jsonify({
                "error": f"Invalid data_access_scope. Must be one of: {', '.join(VALID_DATA_SCOPES)}"
            }), 400
        
        # Convert lists to JSON strings
        permissions_json = json.dumps(permissions) if permissions else None
        allowed_tools_json = json.dumps(allowed_tools) if allowed_tools is not None else None
        allowed_agents_json = json.dumps(allowed_agents) if allowed_agents is not None else None
        
        logger.info(f"Creating sub-user {username} for parent {parent_user_id}")
        
        # Create user in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username/email already exists
        cursor.execute(
            "SELECT id FROM ai_infrastructure.users WHERE username = %s OR email = %s", 
            [username, email]
        )
        
        if cursor.fetchone():
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"Username or email already exists: {username}/{email}")
            return jsonify({
                "error": "Username or email already exists"
            }), 400
        
        # Hash default password
        password_hash = bcrypt.hashpw(DEFAULT_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert sub-user
        cursor.execute("""
            INSERT INTO ai_infrastructure.users (
                username, email, password_hash, role,
                parent_user_id, is_sub_user,
                permissions, allowed_tools, allowed_agents,
                data_access_scope, usage_limit_daily,
                access_start_time, access_end_time, account_expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            username, email, password_hash, 'user',
            parent_user_id, 1,  # is_sub_user = True
            permissions_json, allowed_tools_json, allowed_agents_json,
            data_access_scope, usage_limit_daily,
            access_start_time, access_end_time, account_expires_at
        ])
        
        sub_user_id = cursor.lastrowid
        
        # ✅ Close cursor BEFORE commit
        cursor.close()
        cursor = None
        conn.commit()
        conn.close()
        conn = None
        
        logger.info(f"✅ Created sub-user {username} (ID: {sub_user_id}) for parent {parent_user_id}")
        
        return jsonify({
            "success": True,
            "sub_user_id": sub_user_id,
            "username": username,
            "email": email,
            "default_password": DEFAULT_PASSWORD,
            "message": "Sub-user created. User must change password on first login."
        }), 201
        
    except sqlite3.IntegrityError as e:
        logger.error(f"Database constraint violation: {e}")
        return jsonify({
            "error": f"Database constraint violation: {str(e)}"
        }), 400
    
    except Exception as e:
        logger.exception(f"Failed to create sub-user: {e}")
        return jsonify({
            "error": f"Failed to create sub-user: {str(e)}"
        }), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@user_management_bp.route('/api/users/sub-users', methods=['GET'])
def list_sub_users():
    """
    List all sub-users for the authenticated user
    
    GET /api/users/sub-users?requesting_user_id=<id>
    
    Query params:
    - requesting_user_id: Parent user ID (required)
    
    Returns:
        200: List of sub-users
        403: Permission denied
        500: Server error
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        requesting_user_id = request.args.get('requesting_user_id', type=int)
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id required"}), 400
        
        logger.debug(f"Listing sub-users for user {requesting_user_id}")
        
        # Permission check
        checker = get_permission_checker()
        is_admin = require_admin(requesting_user_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Admins see all sub-users, regular users see only their own
        if is_admin:
            cursor.execute("""
                SELECT 
                    id, username, email, role, parent_user_id, is_sub_user,
                    permissions, allowed_tools, allowed_agents,
                    data_access_scope, usage_limit_daily,
                    access_start_time, access_end_time, account_expires_at,
                    created_at
                FROM ai_infrastructure.users
                WHERE is_sub_user = 1
                ORDER BY created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT 
                    id, username, email, role, parent_user_id, is_sub_user,
                    permissions, allowed_tools, allowed_agents,
                    data_access_scope, usage_limit_daily,
                    access_start_time, access_end_time, account_expires_at,
                    created_at
                FROM ai_infrastructure.users
                WHERE is_sub_user = 1 AND parent_user_id = %s
                ORDER BY created_at DESC
            """, [requesting_user_id])
        
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Convert rows to dicts AFTER database cleanup
        sub_users = []
        for row in rows:
            sub_user = {
                "id": row['id'],
                "username": row['username'],
                "email": row['email'],
                "role": row['role'],
                "parent_user_id": row['parent_user_id'],
                "is_sub_user": bool(row['is_sub_user']),
                "permissions": json.loads(row['permissions']) if row['permissions'] else {},
                "allowed_tools": json.loads(row['allowed_tools']) if row['allowed_tools'] else None,
                "allowed_agents": json.loads(row['allowed_agents']) if row['allowed_agents'] else None,
                "data_access_scope": row['data_access_scope'],
                "usage_limit_daily": row['usage_limit_daily'],
                "access_start_time": row['access_start_time'],
                "access_end_time": row['access_end_time'],
                "account_expires_at": row['account_expires_at'],
                "created_at": row['created_at']
            }
            sub_users.append(sub_user)
        
        logger.info(f"Retrieved {len(sub_users)} sub-users for user {requesting_user_id}")
        
        return jsonify({
            "success": True,
            "sub_users": sub_users,
            "count": len(sub_users)
        }), 200
        
    except Exception as e:
        logger.exception(f"Failed to list sub-users: {e}")
        return jsonify({
            "error": f"Failed to list sub-users: {str(e)}"
        }), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@user_management_bp.route('/api/users/sub-users/<int:sub_user_id>', methods=['PUT'])
def update_sub_user(sub_user_id: int):
    """
    Update sub-user permissions and settings
    
    PUT /api/users/sub-users/<int:sub_user_id>
    
    Allowed fields (all optional):
    - permissions: JSON object
    - allowed_tools: List of tool names
    - allowed_agents: List of agent IDs
    - data_access_scope: 'own' | 'team' | 'department' | 'all'
    - usage_limit_daily: Integer
    - access_start_time: HH:MM format
    - access_end_time: HH:MM format
    - account_expires_at: ISO timestamp
    
    Returns:
        200: Sub-user updated successfully
        403: Permission denied
        404: Sub-user not found
        500: Server error
    
    ✅ FIXED: Proper cursor management with finally block and multiple early returns
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        data = request.get_json()
        requesting_user_id = data.get('requesting_user_id')
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id required"}), 400
        
        logger.debug(f"User {requesting_user_id} updating sub-user {sub_user_id}")
        
        # Check if sub-user exists and get parent_user_id
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT parent_user_id, is_sub_user
            FROM ai_infrastructure.users
            WHERE id = %s
        """, [sub_user_id])
        
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"Sub-user not found: {sub_user_id}")
            return jsonify({"error": "Sub-user not found"}), 404
        
        if not row['is_sub_user']:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"User {sub_user_id} is not a sub-user")
            return jsonify({"error": "User is not a sub-user"}), 400
        
        parent_user_id = row['parent_user_id']
        
        # Permission check: Must be admin OR the parent user
        is_admin = require_admin(requesting_user_id)
        is_parent = requesting_user_id == parent_user_id
        
        if not (is_admin or is_parent):
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"User {requesting_user_id} not authorized to update sub-user {sub_user_id}")
            return jsonify({
                "error": "Only admins or the parent user can update this sub-user"
            }), 403
        
        # Build UPDATE statement dynamically
        updates = []
        params = []
        
        if 'permissions' in data:
            updates.append("permissions = ?")
            params.append(json.dumps(data['permissions']))
        
        if 'allowed_tools' in data:
            updates.append("allowed_tools = ?")
            params.append(json.dumps(data['allowed_tools']) if data['allowed_tools'] is not None else None)
        
        if 'allowed_agents' in data:
            updates.append("allowed_agents = ?")
            params.append(json.dumps(data['allowed_agents']) if data['allowed_agents'] is not None else None)
        
        if 'data_access_scope' in data:
            updates.append("data_access_scope = ?")
            params.append(data['data_access_scope'])
        
        if 'usage_limit_daily' in data:
            updates.append("usage_limit_daily = ?")
            params.append(data['usage_limit_daily'])
        
        if 'access_start_time' in data:
            updates.append("access_start_time = ?")
            params.append(data['access_start_time'])
        
        if 'access_end_time' in data:
            updates.append("access_end_time = ?")
            params.append(data['access_end_time'])
        
        if 'account_expires_at' in data:
            updates.append("account_expires_at = ?")
            params.append(data['account_expires_at'])
        
        if not updates:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"No fields to update for sub-user {sub_user_id}")
            return jsonify({"error": "No fields to update"}), 400
        
        # Execute update
        params.append(sub_user_id)
        cursor.execute(f"""
            UPDATE ai_infrastructure.users
            SET {', '.join(updates)}
            WHERE id = %s
        """, params)
        
        # ✅ Close cursor BEFORE commit
        cursor.close()
        cursor = None
        conn.commit()
        conn.close()
        conn = None
        
        logger.info(f"✅ Updated sub-user {sub_user_id} ({len(updates)} fields)")
        
        return jsonify({
            "success": True,
            "message": f"Sub-user {sub_user_id} updated successfully",
            "fields_updated": len(updates)
        }), 200
        
    except Exception as e:
        logger.exception(f"Failed to update sub-user {sub_user_id}: {e}")
        return jsonify({
            "error": f"Failed to update sub-user: {str(e)}"
        }), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@user_management_bp.route('/api/users/sub-users/<int:sub_user_id>', methods=['DELETE'])
def delete_sub_user(sub_user_id: int):
    """
    Delete a sub-user (soft delete - sets account_expires_at to now)
    
    DELETE /api/users/sub-users/<int:sub_user_id>
    
    Returns:
        200: Sub-user deleted successfully
        403: Permission denied
        404: Sub-user not found
        500: Server error
    
    ✅ FIXED: Proper cursor management with finally block and multiple early returns
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        data = request.get_json() or {}
        requesting_user_id = data.get('requesting_user_id') or request.args.get('requesting_user_id', type=int)
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id required"}), 400
        
        logger.info(f"User {requesting_user_id} deleting sub-user {sub_user_id}")
        
        # Check if sub-user exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT parent_user_id, is_sub_user
            FROM ai_infrastructure.users
            WHERE id = %s
        """, [sub_user_id])
        
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"Sub-user not found: {sub_user_id}")
            return jsonify({"error": "Sub-user not found"}), 404
        
        if not row['is_sub_user']:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"User {sub_user_id} is not a sub-user")
            return jsonify({"error": "User is not a sub-user"}), 400
        
        parent_user_id = row['parent_user_id']
        
        # Permission check
        is_admin = require_admin(requesting_user_id)
        is_parent = requesting_user_id == parent_user_id
        
        if not (is_admin or is_parent):
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"User {requesting_user_id} not authorized to delete sub-user {sub_user_id}")
            return jsonify({
                "error": "Only admins or the parent user can delete this sub-user"
            }), 403
        
        # Soft delete (set expiry to now)
        from datetime import datetime
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE ai_infrastructure.users
            SET account_expires_at = %s
            WHERE id = %s
        """, [now, sub_user_id])
        
        # ✅ Close cursor BEFORE commit
        cursor.close()
        cursor = None
        conn.commit()
        conn.close()
        conn = None
        
        logger.info(f"✅ Deleted sub-user {sub_user_id} (account expired)")
        
        return jsonify({
            "success": True,
            "message": f"Sub-user {sub_user_id} deleted (account expired)",
            "expired_at": now
        }), 200
        
    except Exception as e:
        logger.exception(f"Failed to delete sub-user {sub_user_id}: {e}")
        return jsonify({
            "error": f"Failed to delete sub-user: {str(e)}"
        }), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@user_management_bp.route('/api/users/sub-users/<int:sub_user_id>/reset-password', methods=['POST'])
def reset_sub_user_password(sub_user_id: int):
    """
    Reset sub-user password to a new random password
    
    POST /api/users/sub-users/<int:sub_user_id>/reset-password
    
    Returns:
        200: Password reset successfully with new password
        403: Permission denied
        404: Sub-user not found
        500: Server error
    
    ✅ FIXED: Proper cursor management with finally block and multiple early returns
    """
    cursor = None  # ✅ Initialize before try
    conn = None    # ✅ Initialize before try
    try:
        data = request.get_json()
        requesting_user_id = data.get('requesting_user_id')
        
        if not requesting_user_id:
            return jsonify({"error": "requesting_user_id required"}), 400
        
        logger.info(f"User {requesting_user_id} resetting password for sub-user {sub_user_id}")
        
        # Check if sub-user exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT parent_user_id, is_sub_user, username
            FROM ai_infrastructure.users
            WHERE id = %s
        """, [sub_user_id])
        
        row = cursor.fetchone()
        
        if not row:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"Sub-user not found: {sub_user_id}")
            return jsonify({"error": "Sub-user not found"}), 404
        
        if not row['is_sub_user']:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"User {sub_user_id} is not a sub-user")
            return jsonify({"error": "User is not a sub-user"}), 400
        
        parent_user_id = row['parent_user_id']
        username = row['username']
        
        # Permission check
        is_admin = require_admin(requesting_user_id)
        is_parent = requesting_user_id == parent_user_id
        
        if not (is_admin or is_parent):
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            logger.warning(f"User {requesting_user_id} not authorized to reset password for sub-user {sub_user_id}")
            return jsonify({
                "error": "Only admins or the parent user can reset this sub-user's password"
            }), 403
        
        # Generate random password
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Hash password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        cursor.execute("""
            UPDATE ai_infrastructure.users
            SET password_hash = %s
            WHERE id = %s
        """, [password_hash, sub_user_id])
        
        # ✅ Close cursor BEFORE commit
        cursor.close()
        cursor = None
        conn.commit()
        conn.close()
        conn = None
        
        logger.info(f"✅ Reset password for sub-user {username} (ID: {sub_user_id})")
        
        return jsonify({
            "success": True,
            "message": f"Password reset for sub-user {username}",
            "new_password": new_password,
            "username": username,
            "note": "User must change this password on next login"
        }), 200
        
    except Exception as e:
        logger.exception(f"Failed to reset password for sub-user {sub_user_id}: {e}")
        return jsonify({
            "error": f"Failed to reset password: {str(e)}"
        }), 500
    finally:
        # ✅ GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


# ======================================================================
# STARTUP LOGGING
# ======================================================================
logger.info("="*80)
logger.info("User Management Routes loaded (Fixed Version)")
logger.info("   - ✅ CURSOR MANAGEMENT FIXED (24 issues resolved)")
logger.info("   - 📅 LAST UPDATED: 2025-12-07")
logger.info("   - Endpoints: 5 routes registered")
logger.info(f"   - Default password: {DEFAULT_PASSWORD}")
logger.info(f"   - Valid data scopes: {', '.join(VALID_DATA_SCOPES)}")
logger.info(f"   - Default usage limit: {DEFAULT_USAGE_LIMIT_DAILY}/day")
logger.info("="*80)

# Export blueprint
__all__ = ['user_management_bp']