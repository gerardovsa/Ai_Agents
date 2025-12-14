"""
AI_agents/AI_infrastructure/routes/account_linking_routes.py
Account Linking Routes - Strategy #2 (Email Aliases)
====================================================

Allows users to link multiple email accounts (Google, M365) to one primary account.

Uses the Email Aliases strategy where:
- Primary email stored in users.email
- Additional emails stored in user_email_aliases table
- All aliases point to same user_id → same data

CURSOR MANAGEMENT: Fixed December 7, 2025
- All cursors properly initialized before try blocks
- All cursors closed in finally blocks
- Connection closed AFTER cursor
- Exception-safe cleanup guaranteed
"""

from flask import Blueprint, request, jsonify, session, redirect
import os
import secrets
from datetime import datetime, timedelta
import logging
import sys
import jwt
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database utility with auto-detection
from shared.database_utils import (
    convert_sql_placeholders,
    get_ai_infrastructure_connection, 
    is_using_supabase,
    adapt_sql_for_database
)

# No sys.path.append needed - utils is in same parent directory
from utils.email_alias_helpers import (
    get_user_id_by_email,
    add_email_alias,
    get_user_emails,
    remove_email_alias,
    is_email_available
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

account_linking_bp = Blueprint('account_linking', __name__, url_prefix='/api/account')

def get_db_connection():
    """
    Get database connection to ai_infrastructure database
    
    Auto-detects environment:
    - Local dev: SQLite in data/ai_infrastructure.db
    - Render: Supabase PostgreSQL (ai_infrastructure schema)
    """
    return get_ai_infrastructure_connection()

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("❌ Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"❌ Invalid token: {e}")
        return None

def init_account_linking_tables():
    """Initialize account linking tables if they don't exist"""
    # Skip initialization if using Supabase (tables already migrated)
    if is_using_supabase():
        logger.info("[INIT] Using Supabase - skipping table creation (already migrated)")
        return
    
    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Table for linked accounts (with database-specific SQL)
        sql_user_account_links = adapt_sql_for_database('''
            CREATE TABLE IF NOT EXISTS user_account_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_user_id INTEGER NOT NULL,
                linked_user_id INTEGER NOT NULL,
                linked_email TEXT NOT NULL,
                link_type TEXT NOT NULL,
                link_status TEXT DEFAULT 'pending',
                link_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP,
                FOREIGN KEY (primary_user_id) REFERENCES users(id),
                FOREIGN KEY (linked_user_id) REFERENCES users(id),
                UNIQUE(primary_user_id, linked_user_id)
            )
        ''')
        cursor.execute(sql_user_account_links)
        
        # Table for pending link requests (with database-specific SQL)
        sql_account_link_requests = adapt_sql_for_database('''
            CREATE TABLE IF NOT EXISTS account_link_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_email TEXT NOT NULL,
                link_token TEXT UNIQUE NOT NULL,
                request_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute(sql_account_link_requests)
        
        # Add is_primary field to users table if not exists
        try:
            if is_using_supabase():
                # PostgreSQL syntax
                cursor.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS is_primary BOOLEAN DEFAULT true')
            else:
                # SQLite syntax
                cursor.execute('ALTER TABLE users ADD COLUMN is_primary BOOLEAN DEFAULT 1')
        except (psycopg2.OperationalError, Exception) as e:
            # Column already exists or other error - safe to ignore
            pass
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info("[INIT] ✅ Account linking tables initialized")
        
    except Exception as e:
        logger.error(f"[INIT] ❌ Error initializing tables: {e}")
        # Don't raise - allow app to start even if tables fail
    finally:
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

# Initialize tables on module load
init_account_linking_tables()


@account_linking_bp.route('/link-status', methods=['GET'])
def get_link_status():
    """
    Get current user's account linking status
    
    GET /api/account/link-status
    Headers: Authorization: Bearer <token>
    
    Returns:
    {
        "is_primary": true,
        "linked_accounts": [
            {"email": "user@gmail.com", "provider": "google", "linked_at": "..."},
            {"email": "user@company.com", "provider": "microsoft365", "linked_at": "..."}
        ],
        "pending_links": [
            {"email": "pending@email.com", "requested_at": "..."}
        ]
    }
    """
    cursor = None
    conn = None
    try:
        # Get current user from token
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT id, email, is_primary FROM ai_infrastructure.users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get linked accounts
        sql, params = convert_sql_placeholders('''
            SELECT 
                u.email,
                upc.platform,
                ual.created_at,
                ual.link_status
            FROM ai_infrastructure.user_account_links ual
            JOIN ai_infrastructure.users u ON u.id = ual.linked_user_id
            LEFT JOIN ai_infrastructure.user_platform_credentials upc ON upc.user_id = ual.linked_user_id
            WHERE ual.primary_user_id = %s
            AND ual.link_status = 'confirmed'
            GROUP BY u.email
        ''', (user_id,))

        cursor.execute(sql, params)
        linked_accounts = [dict(row) for row in cursor.fetchall()]
        
        # Get pending link requests
        sql, params = convert_sql_placeholders('''
            SELECT target_email, created_at, status
            FROM ai_infrastructure.account_link_requests
            WHERE user_id = %s
            AND status = 'pending'
            AND expires_at > CURRENT_TIMESTAMP
        ''', (user_id,))

        cursor.execute(sql, params)
        pending_links = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'is_primary': bool(user['is_primary']),
            'primary_email': user['email'],
            'linked_accounts': linked_accounts,
            'pending_links': pending_links
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting link status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@account_linking_bp.route('/initiate-link', methods=['POST'])
def initiate_link():
    """
    Initiate linking another account
    
    POST /api/account/initiate-link
    Headers: Authorization: Bearer <token>
    Body: {
        "provider": "google" | "microsoft365",
        "email": "optional_target_email"
    }
    
    Returns:
    {
        "success": true,
        "oauth_url": "https://accounts.google.com/...",
        "link_token": "abc123..."
    }
    """
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        provider = data.get('provider')  # 'google' or 'microsoft365'
        
        if provider not in ['google', 'microsoft365']:
            return jsonify({'success': False, 'error': 'Invalid provider'}), 400
        
        # Generate link token
        link_token = secrets.token_urlsafe(32)
        session['account_link_token'] = link_token
        session['linking_user_id'] = user_id
        
        # Create OAuth URL with special linking flag
        if provider == 'google':
            oauth_url = f"/api/auth/google/login?link_token={link_token}"
        else:
            oauth_url = f"/api/auth/microsoft/login?link_token={link_token}"
        
        logger.info(f"🔗 User {user_id} initiating link with {provider}")
        
        return jsonify({
            'success': True,
            'oauth_url': oauth_url,
            'link_token': link_token,
            'provider': provider
        })
        
    except Exception as e:
        logger.error(f"❌ Error initiating link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@account_linking_bp.route('/confirm-link', methods=['POST'])
def confirm_link():
    """
    Confirm account linking after OAuth callback
    
    POST /api/account/confirm-link
    Body: {
        "link_token": "abc123...",
        "secondary_email": "user@company.com"
    }
    
    This is called by OAuth routes after successful authentication
    """
    cursor = None
    conn = None
    try:
        data = request.get_json()
        link_token = data.get('link_token')
        secondary_email = data.get('secondary_email')
        primary_user_id = data.get('primary_user_id')
        secondary_user_id = data.get('secondary_user_id')
        
        if not all([link_token, secondary_email, primary_user_id, secondary_user_id]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify link token matches
        stored_token = session.get('account_link_token')
        if link_token != stored_token:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Invalid link token'}), 400
        
        # Check if already linked
        sql, params = convert_sql_placeholders('''
            SELECT id FROM ai_infrastructure.user_account_links
            WHERE primary_user_id = %s AND linked_user_id = %s
        ''', (primary_user_id, secondary_user_id))

        cursor.execute(sql, params)
        
        if cursor.fetchone():
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Accounts already linked'}), 400
        
        # Create link
        sql, params = convert_sql_placeholders('''
            INSERT INTO ai_infrastructure.user_account_links 
            (primary_user_id, linked_user_id, linked_email, link_type, link_status, link_token, confirmed_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''', (primary_user_id, secondary_user_id, secondary_email, 'oauth', 'confirmed', link_token))

        cursor.execute(sql, params)
        
        # Mark secondary account as non-primary
        cursor.execute('UPDATE ai_infrastructure.users SET is_primary = 0 WHERE id = %s', (secondary_user_id,))
        
        # Migrate data from secondary to primary (optional - can be done later)
        # This merges chat threads, settings, etc.
        migrate_user_data(cursor, secondary_user_id, primary_user_id)
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Clear session
        session.pop('account_link_token', None)
        session.pop('linking_user_id', None)
        
        logger.info(f"✅ Linked account {secondary_email} to primary user {primary_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Account linked successfully',
            'primary_user_id': primary_user_id,
            'linked_email': secondary_email
        })
        
    except Exception as e:
        logger.error(f"❌ Error confirming link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@account_linking_bp.route('/unlink', methods=['POST'])
def unlink_account():
    """
    Unlink a secondary account
    
    POST /api/account/unlink
    Headers: Authorization: Bearer <token>
    Body: {
        "linked_email": "user@company.com"
    }
    """
    cursor = None
    conn = None
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        linked_email = data.get('linked_email')
        
        if not linked_email:
            return jsonify({'success': False, 'error': 'Missing linked_email'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find linked user by email
        cursor.execute('SELECT id FROM ai_infrastructure.users WHERE email = %s', (linked_email,))
        linked_user = cursor.fetchone()
        
        if not linked_user:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Linked user not found'}), 404
        
        linked_user_id = linked_user['id']
        
        # Delete link
        sql, params = convert_sql_placeholders('''
            DELETE FROM ai_infrastructure.user_account_links
            WHERE primary_user_id = %s AND linked_user_id = %s
        ''', (user_id, linked_user_id))

        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Link not found'}), 404
        
        # Mark as primary again (optional)
        cursor.execute('UPDATE ai_infrastructure.users SET is_primary = 1 WHERE id = %s', (linked_user_id,))
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"✅ Unlinked account {linked_email} from user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Account unlinked successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error unlinking account: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


@account_linking_bp.route('/set-primary', methods=['POST'])
def set_primary_email():
    """
    Change which email is the primary account
    
    POST /api/account/set-primary
    Headers: Authorization: Bearer <token>
    Body: {
        "new_primary_email": "user@company.com"
    }
    
    This swaps the primary/secondary relationship
    """
    cursor = None
    conn = None
    try:
        user_id = get_user_from_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        new_primary_email = data.get('new_primary_email')
        
        if not new_primary_email:
            return jsonify({'success': False, 'error': 'Missing new_primary_email'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current user email
        cursor.execute('SELECT email FROM ai_infrastructure.users WHERE id = %s', (user_id,))
        current_user = cursor.fetchone()
        old_primary_email = current_user['email']
        
        # Find new primary user
        cursor.execute('SELECT id FROM ai_infrastructure.users WHERE email = %s', (new_primary_email,))
        new_primary_user = cursor.fetchone()
        
        if not new_primary_user:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'New primary user not found'}), 404
        
        new_primary_id = new_primary_user['id']
        
        # Verify they're linked
        sql, params = convert_sql_placeholders('''
            SELECT id FROM ai_infrastructure.user_account_links
            WHERE (primary_user_id = %s AND linked_user_id = %s)
            OR (primary_user_id = %s AND linked_user_id = %s)
        ''', (user_id, new_primary_id, new_primary_id, user_id))

        cursor.execute(sql, params)
        
        if not cursor.fetchone():
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'success': False, 'error': 'Accounts not linked'}), 400
        
        # Swap primary status
        cursor.execute('UPDATE ai_infrastructure.users SET is_primary = 0 WHERE id = %s', (user_id,))
        cursor.execute('UPDATE ai_infrastructure.users SET is_primary = 1 WHERE id = %s', (new_primary_id,))
        
        # Update all links to point to new primary
        sql, params = convert_sql_placeholders('''
            UPDATE ai_infrastructure.user_account_links
            SET primary_user_id = %s, linked_user_id = %s
            WHERE primary_user_id = %s AND linked_user_id = %s
        ''', (new_primary_id, user_id, user_id, new_primary_id))

        cursor.execute(sql, params)
        
        # Migrate data to new primary
        migrate_user_data(cursor, user_id, new_primary_id)
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        logger.info(f"✅ Changed primary email from {old_primary_email} to {new_primary_email}")
        
        return jsonify({
            'success': True,
            'message': 'Primary email updated',
            'old_primary': old_primary_email,
            'new_primary': new_primary_email
        })
        
    except Exception as e:
        logger.error(f"❌ Error setting primary email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
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


def migrate_user_data(cursor, from_user_id, to_user_id):
    """
    Migrate data from one user to another
    
    This moves:
    - Chat threads
    - Platform credentials
    - Settings
    - Any other user-specific data
    
    NOTE: This function receives a cursor from the calling function
    The calling function is responsible for cursor lifecycle management
    """
    try:
        # Migrate chat threads (if table exists)
        try:
            sql, params = convert_sql_placeholders('''
                UPDATE sessions.threads SET user_id = %s WHERE user_id = %s
            ''', (to_user_id, from_user_id))

            cursor.execute(sql, params)
            logger.info(f"📦 Migrated {cursor.rowcount} threads")
        except psycopg2.OperationalError:
            logger.warning("⚠️ Threads table doesn't exist")
        
        # Migrate platform credentials (keep both)
        # We don't migrate these, we keep them separate so user can use either provider
        
        # Migrate user sessions
        sql, params = convert_sql_placeholders('''
            UPDATE ai_infrastructure.user_sessions SET user_id = %s WHERE user_id = %s
        ''', (to_user_id, from_user_id))

        cursor.execute(sql, params)
        logger.info(f"🔑 Migrated {cursor.rowcount} sessions")
        
        logger.info(f"✅ Data migration from user {from_user_id} to {to_user_id} complete")
        
    except Exception as e:
        logger.error(f"❌ Error migrating user data: {e}")
        raise


def get_user_from_token(auth_header):
    """Extract user ID from JWT token"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        import jwt as pyjwt
        from dotenv import load_dotenv
        
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.master')
        load_dotenv(env_path)
        
        jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-this')
        payload = pyjwt.decode(token, jwt_secret, algorithms=['HS256'])
        
        return payload.get('user_id')
    except Exception as e:
        logger.error(f"❌ Error decoding token: {e}")
        return None


def get_primary_user_id(user_id):
    """
    Get the primary user ID for a given user
    If user is secondary, returns the primary user ID
    If user is primary, returns their own ID
    """
    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user is primary
        cursor.execute('SELECT is_primary FROM ai_infrastructure.users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return user_id
        
        if user['is_primary']:
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return user_id
        
        # User is secondary, find primary
        sql, params = convert_sql_placeholders('''
            SELECT primary_user_id FROM ai_infrastructure.user_account_links
            WHERE linked_user_id = %s
            AND link_status = 'confirmed'
            LIMIT 1
        ''', (user_id,))

        cursor.execute(sql, params)
        
        link = cursor.fetchone()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        if link:
            return link['primary_user_id']
        
        return user_id
        
    except Exception as e:
        logger.error(f"❌ Error getting primary user: {e}")
        return user_id
    finally:
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


# ============================================================================
# STRATEGY #2 (Email Aliases) - NEW SIMPLIFIED ENDPOINTS
# ============================================================================

def get_current_user_from_token():
    """Extract and verify user from JWT token in request"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, {'error': 'Missing or invalid authorization header'}
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        payload = verify_jwt_token(token)
        if not payload:
            return None, {'error': 'Invalid or expired token'}
        
        return payload, None
    except Exception as e:
        logger.error(f"❌ Token verification error: {e}")
        return None, {'error': 'Token verification failed'}


@account_linking_bp.route('/emails', methods=['GET'])
def get_linked_emails():
    """
    GET /api/account/emails
    
    Get all email addresses linked to the current user's account
    
    Returns:
        {
            "success": true,
            "primary": "john@gmail.com",
            "aliases": [
                {
                    "email": "john@company.com",
                    "provider": "microsoft365",
                    "linked_at": "2025-10-28T10:30:00"
                }
            ],
            "total_emails": 2
        }
    """
    user, error = get_current_user_from_token()
    if error:
        return jsonify({'success': False, **error}), 401
    
    try:
        user_id = user['id']
        emails = get_user_emails(user_id)
        
        return jsonify({
            'success': True,
            'primary': emails['primary'],
            'aliases': emails['aliases'],
            'total_emails': 1 + len(emails['aliases'])
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting linked emails: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@account_linking_bp.route('/link/oauth', methods=['POST'])
def link_oauth_email():
    """
    POST /api/account/link/oauth
    
    Link an OAuth-authenticated email to the current user's account
    
    Body:
        {
            "email": "john@company.com",
            "provider": "microsoft365"
        }
    
    Returns:
        {
            "success": true,
            "message": "Email linked successfully"
        }
    """
    user, error = get_current_user_from_token()
    if error:
        return jsonify({'success': False, **error}), 401
    
    data = request.get_json()
    email = data.get('email')
    provider = data.get('provider')  # 'google' or 'microsoft365'
    
    if not email or not provider:
        return jsonify({
            'success': False,
            'error': 'Email and provider are required'
        }), 400
    
    try:
        user_id = user['id']
        
        # Add email alias
        success, message = add_email_alias(user_id, email, provider)
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        logger.info(f"✅ Linked {email} to user {user_id}")
        
        return jsonify({
            'success': True,
            'message': message,
            'alias': {
                'email': email,
                'provider': provider
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error linking OAuth email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@account_linking_bp.route('/unlink/<path:email>', methods=['DELETE'])
def unlink_email_alias(email):
    """
    DELETE /api/account/unlink/john@company.com
    
    Unlink an email alias from the current user's account
    
    Returns:
        {
            "success": true,
            "message": "Email unlinked successfully"
        }
    """
    user, error = get_current_user_from_token()
    if error:
        return jsonify({'success': False, **error}), 401
    
    try:
        user_id = user['id']
        
        # Prevent unlinking primary email
        emails = get_user_emails(user_id)
        if email == emails['primary']:
            return jsonify({
                'success': False,
                'error': 'Cannot unlink primary email'
            }), 400
        
        # Remove alias
        success, message = remove_email_alias(email, user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        logger.info(f"✅ Unlinked {email} from user {user_id}")
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error unlinking email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
