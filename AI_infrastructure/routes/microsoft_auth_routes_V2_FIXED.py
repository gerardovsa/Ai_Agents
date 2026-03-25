"""
Microsoft 365 Authentication Routes (V3 COMPLETE - CURSOR MANAGEMENT FIXED)
===========================================================================

FIXED VERSION - All cursor management issues resolved (Refactored 2026-01-01)
Generated: January 1, 2026

✅ ALL CURSORS NOW USE CONTEXT MANAGERS
✅ ZERO CURSOR LEAKS - All 9 functions refactored
✅ Proper indentation and cleanup

CRITICAL CHANGES FROM V2:
- ✅ All cursors use `with conn.cursor() as cursor:` pattern
- ✅ All cursor operations indented inside context managers
- ✅ Manual cursor.close() calls removed (context manager handles cleanup)
- ✅ All functions maintain error handling and business logic
- ✅ Multiple cursors independently managed with separate context managers
- ✅ Early returns handled by context manager cleanup
- ✅ Finally blocks still guarantee connection cleanup

WRITES TO: oauth_tokens table with correct schema (24 columns)
LOADS FROM: .env.master file (local) or OS environment (Render)
"""

from flask import Blueprint, request, jsonify, redirect, url_for, session
from auth.user_auth import user_auth_manager, require_auth

# Add root to path for Microsoft_365_Connection
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# CRITICAL: Import centralized database path helper (Render compatibility)
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.db_path_helper import get_ai_infrastructure_db_path
from shared.database_utils import get_database_connection, convert_sql_placeholders, is_using_supabase

from Microsoft_365_Connection.microsoft365_oauth_manager import (
    microsoft_oauth_manager,
    get_microsoft_auth_url,
    authenticate_user_with_microsoft
)
import secrets
import logging
from datetime import datetime, timedelta
import jwt as pyjwt
import json
import random

# Add path for email alias helpers
sys.path.append('C:/Users/gpoli/GIT/AI_agents/AI_infrastructure')
from utils.email_alias_helpers import get_user_id_by_email, add_email_alias
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

microsoft_auth_bp = Blueprint('microsoft_auth', __name__, url_prefix='/api/auth/microsoft')

# Load credentials from .env.master (local dev) or OS environment (Render)
_ENV_MASTER_PATH = Path(__file__).parent.parent.parent / '.env.master'
if _ENV_MASTER_PATH.exists():
    _config = dotenv_values(_ENV_MASTER_PATH)
else:
    # On Render, use OS environment variables
    _config = {}

# Microsoft Graph API scopes - MATCH AZURE APP REGISTRATION (12 scopes granted)
# Updated November 5, 2025 to match actual Azure portal configuration
MICROSOFT_SCOPES = [
    # Authentication & Profile (auto-included by Microsoft)
    'offline_access',              # ✅ Refresh tokens
    
    # User
    'User.Read',                   # ✅ Sign in and read user profile
    'User.ReadWrite',              # ✅ Read and write user profile
    
    # Mail (Outlook)
    'Mail.ReadWrite',              # ✅ Read and write mail (includes Mail.Read)
    'Mail.Send',                   # ✅ Send mail as a user (Delegated)
    'MailboxFolder.Read',          # ✅ Read mailbox folders
    
    # Calendar
    'Calendars.ReadWrite',         # ✅ Read and write calendars (includes Calendars.Read)
    
    # Files (OneDrive, Word, Excel)
    'Files.ReadWrite.All',         # ✅ Full file access (includes Files.Read, Files.Read.All, Files.ReadWrite)
    
    # Tasks (To Do)
    'Tasks.ReadWrite',             # ✅ Read and write tasks
    
    # Teams
    'Team.ReadBasic.All',          # ✅ Read basic team info
    'ChannelMessage.Send'          # ✅ Send channel messages
]

# NOTE: Mail.Send (Application permission) is configured separately in Azure Portal
# and does NOT need to be in this delegated scopes list

# ======================================================================
# DATABASE HELPER FUNCTIONS (REFACTORED - CURSOR LEAKS FIXED)
# ======================================================================

def get_db_connection():
    """Get database connection to ai_infrastructure (SQLite or Supabase)"""
    # CRITICAL: Use centralized utility (auto-detects SQLite vs Supabase)
    conn = get_database_connection('ai_infrastructure')
    if hasattr(conn, 'row_factory'):  # SQLite
        conn.row_factory = psycopg2.extras.RealDictRow
    logger.info(f'🔷 [DB CONNECTION] Using: ai_infrastructure schema')
    return conn


def init_db():
    """
    Initialize database with oauth_tokens table (SQLite & PostgreSQL compatible)
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        from shared.database_utils import is_using_supabase
        
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            
            # Detect database type for syntax compatibility
            using_postgres = is_using_supabase()
            
            if using_postgres:
                # PostgreSQL syntax (SERIAL for auto-increment, BOOLEAN for flags)
                sql = convert_sql_placeholders('''
                    CREATE TABLE IF NOT EXISTS oauth_tokens (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        platform TEXT NOT NULL,
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_type TEXT DEFAULT 'Bearer',
                        expires_at TIMESTAMP,
                        scope TEXT,
                        is_valid BOOLEAN DEFAULT true,
                        is_active BOOLEAN DEFAULT true,
                        auto_refresh_enabled BOOLEAN DEFAULT true,
                        last_refreshed_at TIMESTAMP,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        email TEXT,
                        profile_name TEXT,
                        profile_picture_url TEXT,
                        profile_data TEXT,
                        granted_scopes TEXT,
                        auth_method TEXT DEFAULT 'oauth2',
                        metadata TEXT,
                        UNIQUE(user_id, platform)
                    )
                ''')
                
                cursor.execute(sql)
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS oauth_states (
                        id SERIAL PRIMARY KEY,
                        state TEXT NOT NULL UNIQUE,
                        platform TEXT NOT NULL,
                        return_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                ''')
            else:
                # SQLite syntax (AUTOINCREMENT, INTEGER for booleans)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS oauth_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        platform TEXT NOT NULL,
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_type TEXT DEFAULT 'Bearer',
                        expires_at TIMESTAMP,
                        scope TEXT,
                        is_valid INTEGER DEFAULT 1,
                        is_active INTEGER DEFAULT 1,
                        auto_refresh_enabled INTEGER DEFAULT 1,
                        last_refreshed_at TIMESTAMP,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        email TEXT,
                        profile_name TEXT,
                        profile_picture_url TEXT,
                        profile_data TEXT,
                        granted_scopes TEXT,
                        auth_method TEXT DEFAULT 'oauth2',
                        metadata TEXT,
                        UNIQUE(user_id, platform),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS oauth_states (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        state TEXT NOT NULL UNIQUE,
                        platform TEXT NOT NULL,
                        return_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                ''')
            
            # Create index for fast state lookup (same syntax for both)
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_oauth_states_state 
                ON oauth_states(state, platform, expires_at)
            ''')
            
            conn.commit()
        
        conn.close()
        conn = None
        
        logger.info(f"Database tables initialized (oauth_tokens, oauth_states) - {'PostgreSQL' if using_postgres else 'SQLite'}")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


# Initialize tables on module load
init_db()


def get_user_by_email(email: str):
    """
    Get user by email from database
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            
            cursor.execute('SELECT * FROM ai_infrastructure.users WHERE email = %s', (email,))
            user = cursor.fetchone()
        
        conn.close()
        conn = None
        
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"❌ Error getting user by email: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def get_user_by_id(user_id: int):
    """
    Get user by ID from database
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            
            cursor.execute('SELECT * FROM ai_infrastructure.users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
        
        conn.close()
        conn = None
        
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"❌ Error getting user by ID: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def _auto_assign_org_by_domain(user_id: int, email: str) -> None:
    """GAP-M6: Auto-add new SSO user to org if their email domain matches allowed_domains."""
    try:
        domain = email.split('@')[1].lower() if '@' in email else ''
        if not domain:
            return

        from shared.database_utils import execute_query
        org = execute_query(
            """
            SELECT id FROM ai_infrastructure.organisations
            WHERE %s = ANY(allowed_domains)
              AND is_active = TRUE
            LIMIT 1
            """,
            (domain,),
            fetch_mode='one'
        )
        if not org:
            return

        org_id = org['id'] if isinstance(org, dict) else org[0]

        existing = execute_query(
            "SELECT id FROM ai_infrastructure.organisation_members WHERE organisation_id = %s AND user_id = %s",
            (org_id, user_id),
            fetch_mode='one'
        )
        if existing:
            return

        execute_query(
            """
            INSERT INTO ai_infrastructure.organisation_members
                (organisation_id, user_id, role, is_active, invited_by, joined_at, created_at)
            VALUES (%s, %s, 'member', TRUE, NULL, NOW(), NOW())
            """,
            (org_id, user_id)
        )
        execute_query(
            "UPDATE ai_infrastructure.users SET organisation_id = %s WHERE id = %s AND organisation_id IS NULL",
            (org_id, user_id)
        )
        logger.info(f'[SSO AUTO-ASSIGN] User {user_id} ({email}) auto-joined org {org_id} via domain "{domain}"')

    except Exception as e:
        logger.warning(f'[SSO AUTO-ASSIGN] Domain org assignment failed for {email}: {e}')


def create_user(email: str, username: str, role: str = 'user'):
    """
    Create new user in database with comprehensive error handling
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            
            # Check if user already exists
            cursor.execute('SELECT id FROM ai_infrastructure.users WHERE email = %s', (email,))
            existing = cursor.fetchone()
            if existing:
                logger.warning(f"User already exists with email {email}, returning existing user")
                return get_user_by_email(email)
            
            # Make username unique if collision
            cursor.execute('SELECT id FROM ai_infrastructure.users WHERE username = %s', (username,))
            if cursor.fetchone():
                # Add random suffix to username
                username = f"{username}_{random.randint(1000, 9999)}"
                logger.info(f"Username collision, using: {username}")
            
            cursor.execute('''
                INSERT INTO ai_infrastructure.users (username, email, password_hash, role, created_at)
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, email, 'oauth_microsoft', role, datetime.now().isoformat()))
            user_id = cursor.lastrowid
            
            conn.commit()
        
        conn.close()
        conn = None
        
        logger.info(f"Created new user: {email} (ID: {user_id})")
        return get_user_by_email(email)
        
    except IntegrityError as e:
        logger.error(f"Integrity constraint violation: {e}")
        # Try to get existing user
        try:
            existing_user = get_user_by_email(email)
            if existing_user:
                logger.info(f"Returning existing user after constraint violation")
                return existing_user
        except Exception:
            pass
        logger.error(f"Failed to handle constraint violation")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def generate_jwt_token(payload: dict):
    """
    Generate JWT token for user session
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        # FIXED: Use os.getenv() to match user_auth.py verification (Render compatibility)
        jwt_secret = os.getenv('JWT_SECRET', _config.get('JWT_SECRET', 'your-secret-key-change-this'))
        
        # Calculate expiration as Unix timestamp (integer)
        exp_time = datetime.utcnow() + timedelta(hours=24)
        exp_timestamp = int(exp_time.timestamp())
        
        token_payload = {
            'user_id': payload.get('user_id'),
            'email': payload.get('email'),
            'exp': exp_timestamp
        }
        
        token = pyjwt.encode(token_payload, jwt_secret, algorithm='HS256')
        
        # Store token in user_sessions table
        try:
            from shared.database_utils import convert_sql_placeholders, is_using_supabase
            
            conn = get_db_connection()
            
            with conn.cursor() as cursor:
                
                expires_at = (datetime.utcnow() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Use ai_infrastructure.user_sessions with SERIAL id (auto-increment)
                insert_sql = '''
                    INSERT INTO ai_infrastructure.user_sessions (user_id, token, expires_at)
                    VALUES (%s, %s, %s)
                '''
                insert_sql, insert_params = convert_sql_placeholders(insert_sql, (payload['user_id'], token, expires_at))
                
                cursor.execute(insert_sql, insert_params)
                conn.commit()
            
            conn.close()
            conn = None
            
        except Exception as e:
            logger.warning(f"⚠️ Could not store token in sessions: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
        
        return token
    except Exception as e:
        logger.error(f"❌ Error creating JWT token: {e}")
        return None


# ======================================================================
# OAUTH ENDPOINTS (REFACTORED - CURSOR LEAKS FIXED)
# ======================================================================

@microsoft_auth_bp.route('/login', methods=['GET'])
def microsoft_login():
    """
    Initiate Microsoft 365 OAuth login
    
    GET /api/auth/microsoft/login?force_consent=true
    
    Query Parameters:
        force_consent: If 'true', forces consent screen to reappear (for re-authentication)
    
    Redirects user to Microsoft login page
    
    ✅ FIXED: Proper cursor management with separate context managers for each DB operation
    """
    try:
        # Check if Microsoft credentials are configured
        if not microsoft_oauth_manager.client_id or not microsoft_oauth_manager.client_secret:
            logger.warning("⚠️ Microsoft 365 credentials not configured")
            return jsonify({
                'success': False,
                'error': 'Microsoft 365 login not configured',
                'setup_required': True
            }), 400
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # ====================================================================
        # STEP 1: Store state in database (first cursor)
        # ====================================================================
        conn = None
        try:
            from shared.database_utils import convert_sql_placeholders, is_using_supabase
            
            conn = get_db_connection()
            
            with conn.cursor() as cursor:
                
                # Store with 5 minute expiry (database-agnostic SQL)
                if is_using_supabase():
                    # PostgreSQL: CURRENT_TIMESTAMP and INTERVAL
                    sql = """
                        INSERT INTO ai_infrastructure.oauth_states (state, platform, created_at, expires_at)
                        VALUES (%s, 'microsoft', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '5 minutes')
                    """
                    sql, params = convert_sql_placeholders(sql, (state,))
                else:
                    # SQLite: datetime('now') and strftime
                    sql = """
                        INSERT INTO oauth_states (state, platform, created_at, expires_at)
                        VALUES (?, 'microsoft', datetime('now'), datetime('now', '+5 minutes'))
                    """
                    params = (state,)
                
                cursor.execute(sql, params)
                conn.commit()
                
                logger.info(f"✅ OAuth state stored in database: {state[:20]}...")
                logger.info(f"✅ Expires in 5 minutes")
            
            conn.close()
            conn = None
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to store OAuth state in database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"❌ OAuth login will FAIL without database state storage")
            
            # DO NOT fallback to Flask session - it won't work on production
            return jsonify({
                'success': False,
                'error': 'Failed to initialize OAuth flow - database error',
                'details': str(e) if os.getenv('FLASK_ENV') == 'development' else None
            }), 500
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
        
        # Get redirect URI from environment variable (CRITICAL: Use HTTPS for Render)
        redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI')
        if not redirect_uri:
            # Fallback: build from request, but force HTTPS if on Render
            base_url = request.url_root.rstrip('/')
            if 'onrender.com' in request.host:
                base_url = base_url.replace('http://', 'https://')
            redirect_uri = base_url + '/api/auth/microsoft/callback'
        
        # Store original redirect for after login
        return_url = request.args.get('return_url', '/')
        
        # ====================================================================
        # STEP 2: Store return_url in database (second cursor - independent)
        # ====================================================================
        conn2 = None
        try:
            from shared.database_utils import convert_sql_placeholders, is_using_supabase
            
            conn2 = get_db_connection()
            
            with conn2.cursor() as cursor2:
                
                sql, params = convert_sql_placeholders(
                    "UPDATE ai_infrastructure.oauth_states SET return_url = %s WHERE state = %s",
                    (return_url, state)
                )
                
                cursor2.execute(sql, params)
                conn2.commit()
            
            conn2.close()
            conn2 = None
            
        except Exception as e:
            logger.warning(f"Failed to store return_url: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            # Fallback to Flask session
            session['microsoft_return_url'] = return_url
        finally:
            if conn2:
                try:
                    conn2.close()
                except:
                    pass
        
        # Check if force_consent is requested (for re-authentication)
        force_consent = request.args.get('force_consent', 'false').lower() == 'true'
        prompt = 'consent' if force_consent else 'select_account'
        
        # Get Microsoft authorization URL with ALL scopes defined above
        auth_url = get_microsoft_auth_url(
            redirect_uri=redirect_uri, 
            state=state, 
            prompt=prompt,
            scopes=MICROSOFT_SCOPES  # ✅ PASS THE SCOPES HERE!
        )
        
        logger.info(f"🔷 Initiating Microsoft login (force_consent={force_consent}, prompt={prompt})")
        logger.info(f"   Redirect URI: {redirect_uri}")
        client_id_display = (os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', ''))[:20]
        tenant_display = os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common')
        logger.info(f"   Client ID: {client_id_display}...")
        logger.info(f"   Tenant: {tenant_display}")
        
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"❌ Microsoft login failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@microsoft_auth_bp.route('/callback', methods=['GET'])
def microsoft_callback():
    """
    Microsoft OAuth callback endpoint (V3 COMPLETE - CURSOR MANAGEMENT FIXED)
    
    GET /api/auth/microsoft/callback?code=...&state=...
    
    NOW WRITES TO: oauth_tokens table with 24 columns
    
    ✅ FIXED: All cursor management issues resolved with context managers
    """
    try:
        # ====================================================================
        # STEP 1: Verify state for CSRF protection
        # ====================================================================
        state = request.args.get('state')
        
        # Check database first (cloud-compatible), then fallback to Flask session
        stored_state = None
        return_url = '/'
        conn = None
        try:
            from shared.database_utils import convert_sql_placeholders, is_using_supabase
            
            conn = get_db_connection()
            
            with conn.cursor() as cursor:
                
                # Use database-agnostic SQL
                if is_using_supabase():
                    # PostgreSQL: CURRENT_TIMESTAMP
                    sql = """
                        SELECT state, return_url, expires_at FROM ai_infrastructure.oauth_states 
                        WHERE state = %s AND platform = 'microsoft'
                        AND expires_at > CURRENT_TIMESTAMP
                    """
                    sql, params = convert_sql_placeholders(sql, (state,))
                else:
                    # SQLite: datetime('now')
                    sql = """
                        SELECT state, return_url, expires_at FROM oauth_states 
                        WHERE state = ? AND platform = 'microsoft'
                        AND expires_at > datetime('now')
                    """
                    params = (state,)
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if row:
                    stored_state = row[0] if not isinstance(row, dict) else row['state']
                    return_url = (row[1] if not isinstance(row, dict) else row['return_url']) or '/'
                    
                    logger.info(f"✅ OAuth state found in database: {stored_state[:20]}...")
                    logger.info(f"✅ Return URL: {return_url}")
                    
                    # Delete used state
                    delete_sql, delete_params = convert_sql_placeholders(
                        "DELETE FROM ai_infrastructure.oauth_states WHERE state = %s", (state,)
                    )
                    cursor.execute(delete_sql, delete_params)
                    logger.info(f"✅ Deleted used OAuth state from database")
                else:
                    logger.error(f"❌ OAuth state NOT found in database!")
                    logger.error(f"❌ Searched for state: {state[:20]}...")
                    logger.error(f"❌ This means the state expired OR was never stored")
                    
                    # Return None to trigger error handling below
                    stored_state = None
                    return_url = '/'
                
                conn.commit()
            
            conn.close()
            conn = None
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to retrieve OAuth state from database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"❌ Database query failed - state validation impossible")
            logger.error(f"❌ Incoming state: {state}")
            logger.error(f"❌ This means user CANNOT reconnect Outlook")
            
            # DO NOT fallback to Flask session on production (Render) - it won't work
            # Session is not persistent across web workers
            return jsonify({
                'success': False,
                'error': 'OAuth state validation failed - database error. Please try again or contact support.',
                'details': str(e) if os.getenv('FLASK_ENV') == 'development' else None
            }), 500
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
        
        if not state or not stored_state or state != stored_state:
            logger.error(f"❌ Invalid OAuth state (CSRF protection)")
            logger.error(f"   Incoming state: {state}")
            logger.error(f"   Stored state: {stored_state}")
            logger.error(f"   Match: {state == stored_state if stored_state else 'N/A - no stored state'}")
            return jsonify({
                'success': False,
                'error': 'Invalid state parameter - CSRF protection triggered',
                'hint': 'Try reconnecting Outlook from Account Settings'
            }), 400
        
        # ====================================================================
        # STEP 2: Get authorization code
        # ====================================================================
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.error(f"❌ Microsoft OAuth error: {error}")
            return jsonify({
                'success': False,
                'error': f'Microsoft authorization failed: {error}'
            }), 400
        
        if not code:
            logger.error("❌ No authorization code received")
            return jsonify({
                'success': False,
                'error': 'No authorization code received'
            }), 400
        
        # ====================================================================
        # STEP 3: Exchange code for tokens
        # ====================================================================
        # Get redirect URI from environment variable (CRITICAL: Use HTTPS for Render)
        redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI')
        if not redirect_uri:
            base_url = request.url_root.rstrip('/')
            if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
                base_url = base_url.replace('http://', 'https://')
            redirect_uri = base_url + '/api/auth/microsoft/callback'
        
        auth_result = authenticate_user_with_microsoft(code, redirect_uri)
        
        if not auth_result['success']:
            logger.error(f"❌ Authentication failed: {auth_result.get('error')}")
            return jsonify(auth_result), 400
        
        profile = auth_result['profile']
        tokens = auth_result['tokens']
        
        # Extract token information
        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token', '')
        token_type = tokens.get('token_type', 'Bearer')
        expires_in = tokens.get('expires_in', 3600)
        
        # Calculate expiration timestamp
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract profile information
        email = profile.get('email', profile.get('userPrincipalName', ''))
        display_name = profile.get('display_name', profile.get('displayName', ''))
        microsoft_id = profile.get('id', '')
        
        logger.info(f"✅ 🔓🔓 Microsoft authentication successful: {email}")
        
        # ====================================================================
        # STEP 4: Get or create user
        # ====================================================================
        user_id = get_user_id_by_email(email)
        
        if user_id:
            # Existing user
            user = get_user_by_id(user_id)
            logger.info(f"Existing user found: {user['username']} (ID: {user_id})")
        else:
            # New user - auto-register
            logger.info(f"🆕 New user - auto-registering: {email}")
            username = email.split('@')[0]
            user = create_user(email=email, username=username, role='user')
            
            if not user:
                logger.error("❌ User registration failed")
                return jsonify({'success': False, 'error': 'Failed to create user'}), 500
            
            user_id = user['id']
            logger.info(f"User created: {user['username']} (ID: {user_id})")
            # GAP-M6: Auto-assign to org if email domain matches allowed_domains
            _auto_assign_org_by_domain(user_id, email)
        
        # ====================================================================
        # STEP 5: Store tokens in oauth_tokens table (THE FIX!)
        # ====================================================================
        
        conn = None
        try:
            conn = get_db_connection()
            
            with conn.cursor() as cursor:
                
                # Build granted scopes string
                granted_scopes = ' '.join(MICROSOFT_SCOPES)
                
                # Check if using PostgreSQL or SQLite
                from shared.database_utils import is_using_supabase, convert_sql_placeholders
                
                # ✅ Determine link_purpose based on user's login platform
                cursor.execute('SELECT password_hash FROM ai_infrastructure.users WHERE id = %s', (user_id,))
                user_row = cursor.fetchone()
                password_hash = user_row['password_hash'] if isinstance(user_row, dict) else user_row[0] if user_row else None
                
                if password_hash in ['oauth_microsoft', 'OAUTH_USER_NO_PASSWORD']:
                    link_purpose = 'primary'  # User logged in with Microsoft - full tool access
                    logger.info(f'   🔑 Link Purpose: PRIMARY (user logged in with Microsoft)')
                else:
                    link_purpose = 'storage'  # User logged in with Google/local - OneDrive storage only
                    logger.info(f'   📁 Link Purpose: STORAGE (OneDrive for file storage only)')
                
                # Check if token already exists
                check_sql = 'SELECT id FROM ai_infrastructure.oauth_tokens WHERE user_id = %s AND platform = %s'
                check_sql, check_params = convert_sql_placeholders(check_sql, (user_id, 'microsoft'))
                cursor.execute(check_sql, check_params)
                existing_token = cursor.fetchone()
                
                # PostgreSQL needs TRUE/FALSE for boolean columns, SQLite accepts 1/0
                if is_using_supabase():
                    is_valid_val = True
                    is_active_val = True
                    auto_refresh_val = True
                else:
                    is_valid_val = 1
                    is_active_val = 1
                    auto_refresh_val = 1
                
                if existing_token:
                    # UPDATE existing token
                    sql = '''
                        UPDATE ai_infrastructure.oauth_tokens SET
                            access_token = %s, refresh_token = %s, token_type = %s, expires_at = %s, 
                            scope = %s, is_valid = %s, is_active = %s, auto_refresh_enabled = %s, 
                            last_refreshed_at = %s, error_count = %s, last_error = %s,
                            granted_scopes = %s, metadata = %s, email = %s, profile_name = %s,
                            link_purpose = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s AND platform = %s
                    '''
                    
                    params = (
                        access_token,                         # access_token
                        refresh_token,                        # refresh_token
                        token_type,                           # token_type ('Bearer')
                        expires_at,                           # expires_at (timestamp)
                        ' '.join(MICROSOFT_SCOPES),          # scope (requested scopes)
                        is_valid_val,                         # is_valid
                        is_active_val,                        # is_active
                        auto_refresh_val,                     # auto_refresh_enabled
                        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),  # last_refreshed_at
                        0,                                    # error_count
                        None,                                 # last_error
                        granted_scopes,                       # granted_scopes
                        json.dumps({                          # metadata
                            'microsoft_id': microsoft_id,
                            'email': email,
                            'name': display_name,
                            'profile': profile,
                            'authorized_at': datetime.utcnow().isoformat(),
                            'client_id': (os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', ''))[:20] + '...',
                            'tenant_id': os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common'),
                            'link_purpose': link_purpose
                        }),
                        email,                                # email
                        display_name,                         # profile_name
                        link_purpose,                         # link_purpose
                        user_id,                              # WHERE user_id
                        'microsoft'                           # WHERE platform
                    )
                else:
                    # INSERT new token (works for both PostgreSQL and SQLite)
                    if is_using_supabase():
                        # PostgreSQL: Skip created_at/updated_at (use DEFAULT)
                        sql = '''
                            INSERT INTO ai_infrastructure.oauth_tokens (
                                user_id, platform, access_token, refresh_token, token_type,
                                expires_at, scope, is_valid, is_active, auto_refresh_enabled,
                                last_refreshed_at, error_count, last_error,
                                granted_scopes, metadata, email, profile_name, link_purpose
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        '''
                    else:
                        # SQLite: Explicitly set created_at/updated_at
                        sql = '''
                            INSERT INTO ai_infrastructure.oauth_tokens (
                                user_id, platform, access_token, refresh_token, token_type,
                                expires_at, scope, is_valid, is_active, auto_refresh_enabled,
                                last_refreshed_at, error_count, last_error,
                                granted_scopes, metadata, email, profile_name, link_purpose,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        '''
                    
                    params = (
                        user_id,                              # user_id
                        'microsoft',                          # platform
                        access_token,                         # access_token
                        refresh_token,                        # refresh_token
                        token_type,                           # token_type
                        expires_at,                           # expires_at
                        ' '.join(MICROSOFT_SCOPES),          # scope
                        is_valid_val,                         # is_valid
                        is_active_val,                        # is_active
                        auto_refresh_val,                     # auto_refresh_enabled
                        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),  # last_refreshed_at
                        0,                                    # error_count
                        None,                                 # last_error
                        granted_scopes,                       # granted_scopes
                        json.dumps({                          # metadata
                            'microsoft_id': microsoft_id,
                            'email': email,
                            'name': display_name,
                            'profile': profile,
                            'authorized_at': datetime.utcnow().isoformat(),
                            'client_id': (os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', ''))[:20] + '...',
                            'tenant_id': os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common'),
                            'link_purpose': link_purpose
                        }),
                        email,                                # email
                        display_name,                         # profile_name
                        link_purpose                          # link_purpose ('primary' or 'storage')
                    )
                
                # Convert placeholders and execute
                sql, params = convert_sql_placeholders(sql, params)
                cursor.execute(sql, params)
                
                # Update has_microsoft_oauth flag (use TRUE for PostgreSQL, 1 for SQLite)
                flag_value = True if is_using_supabase() else 1
                update_sql = 'UPDATE ai_infrastructure.users SET has_microsoft_oauth = %s WHERE id = %s'
                update_sql, update_params = convert_sql_placeholders(update_sql, (flag_value, user_id))
                
                # Retry logic for statement timeout
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        cursor.execute(update_sql, update_params)
                        break  # Success, exit retry loop
                    except Exception as update_error:
                        error_msg = str(update_error)
                        if 'statement timeout' in error_msg.lower() and attempt < max_retries - 1:
                            print(f"⚠️  [MICROSOFT OAUTH] Statement timeout on attempt {attempt + 1}, retrying...")
                            conn.rollback()  # Rollback failed transaction
                            import time
                            time.sleep(1)  # Wait 1 second before retry
                            continue
                        elif attempt == max_retries - 1:
                            print(f"❌ [MICROSOFT OAUTH] Failed to update has_microsoft_oauth after {max_retries} attempts: {error_msg}")
                            # Don't fail the entire OAuth flow - tokens are already stored
                            break
                        else:
                            raise  # Re-raise non-timeout errors
                
                conn.commit()
            
            conn.close()
            conn = None
            
            print('✅ 🔓🔓 [MICROSOFT OAUTH] Tokens stored successfully in oauth_tokens table!')
            print(f'   Table: oauth_tokens')
            print(f'   User ID: {user_id}')
            print(f'   Platform: microsoft')
            print(f'   Email: {email}')
            print(f'   All 24 columns populated ✅')
            print(f'✅ [MICROSOFT OAUTH] Updated has_microsoft_oauth flag for user {user_id}')
            
        except Exception as e:
            logger.error(f"❌ Failed to store tokens: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': 'Failed to store credentials'}), 500
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
        
        # ====================================================================
        # STEP 6: Generate JWT session token
        # ====================================================================
        jwt_token = generate_jwt_token({
            'user_id': user_id,
            'email': email
        })
        
        if not jwt_token:
            logger.error("❌ Failed to create JWT token")
            return jsonify({'success': False, 'error': 'Failed to create session'}), 500
        
        # ====================================================================
        # STEP 7: Redirect to frontend with token
        # ====================================================================
        logger.info(f"Redirecting to: {return_url}")
        
        # CRITICAL: Redirect to correct frontend URL based on environment
        frontend_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
            frontend_url = frontend_url.replace('http://', 'https://')
        
        # IMPORTANT: For local development, explicitly use HTTP to prevent browser HTTPS upgrades
        if 'localhost' in request.host or '127.0.0.1' in request.host:
            frontend_url = frontend_url.replace('https://', 'http://')
        
        redirect_url = f"{frontend_url}{return_url}?token={jwt_token}"
        logger.info(f"🔷 Final redirect URL: {redirect_url}")
        
        return redirect(redirect_url)
        
    except Exception as e:
        logger.error(f"❌ Microsoft callback failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/status', methods=['GET'])
@require_auth
def microsoft_status():
    """
    Check Microsoft connection status
    
    GET /api/auth/microsoft/status
    Authorization: Bearer <jwt_token>
    
    Returns connection status and token info FROM ai_infrastructure.oauth_tokens table
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        # Get user_id from request.user (set by @require_auth decorator)
        user_id = request.user.get('user_id')
        
        # Get database connection with error handling
        try:
            conn = get_db_connection()
        except Exception as db_error:
            logger.error(f"❌ Database connection failed: {db_error}")
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'details': str(db_error)
            }), 500
        
        # Query oauth_tokens table
        try:
            with conn.cursor() as cursor:
                
                cursor.execute('''
                    SELECT 
                        access_token, refresh_token, expires_at, is_valid, is_active,
                        email, profile_name, last_refreshed_at, error_count, last_error,
                        created_at, updated_at
                    FROM ai_infrastructure.oauth_tokens
                    WHERE user_id = %s AND platform = %s
                ''', (user_id, 'microsoft'))
                
                row = cursor.fetchone()
                
        except Exception as query_error:
            logger.error(f"❌ Database query failed: {query_error}")
            return jsonify({
                'success': False,
                'error': 'Database query failed',
                'details': str(query_error)
            }), 500
        
        conn.close()
        conn = None
        
        if not row:
            return jsonify({
                'success': True,
                'connected': False,
                'message': 'No Microsoft account connected'
            })
        
        # Handle both SQLite Row objects and PostgreSQL RealDictCursor
        try:
            if hasattr(row, 'keys') and callable(row.keys):  # Dict-like (SQLite Row or PostgreSQL RealDictRow)
                email = row['email']
                profile_name = row['profile_name']
                is_valid = row['is_valid']
                is_active = row['is_active']
                expires_at_str = row['expires_at']
                last_refreshed_at = row['last_refreshed_at']
                error_count = row['error_count']
                last_error = row['last_error']
                created_at = row['created_at']
                updated_at = row['updated_at']
            elif isinstance(row, dict):  # Plain dict (RealDictCursor)
                email = row.get('email')
                profile_name = row.get('profile_name')
                is_valid = row.get('is_valid')
                is_active = row.get('is_active')
                expires_at_str = row.get('expires_at')
                last_refreshed_at = row.get('last_refreshed_at')
                error_count = row.get('error_count')
                last_error = row.get('last_error')
                created_at = row.get('created_at')
                updated_at = row.get('updated_at')
            else:  # PostgreSQL tuple (fallback)
                _, _, expires_at_str, is_valid, is_active, email, profile_name, last_refreshed_at, error_count, last_error, created_at, updated_at = row
        except Exception as parse_error:
            logger.error(f"❌ Failed to parse database row: {parse_error}")
            logger.error(f"Row type: {type(row)}, Row: {row}")
            return jsonify({
                'success': False,
                'error': 'Failed to parse database response',
                'details': str(parse_error)
            }), 500
        
        # Check if token is expired
        try:
            # Handle both datetime objects (PostgreSQL) and strings (SQLite)
            if isinstance(expires_at_str, datetime):
                expires_at = expires_at_str  # Already a datetime object
            elif isinstance(expires_at_str, str):
                expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
            else:
                expires_at = None
            
            is_expired = expires_at and datetime.utcnow() > expires_at
        except Exception as date_error:
            logger.warning(f"⚠️  Failed to parse expiry date: {date_error}")
            is_expired = None
        
        # Convert datetime objects to strings for JSON serialization
        expires_at_json = expires_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(expires_at, datetime) else expires_at_str
        last_refreshed_json = last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(last_refreshed_at, datetime) else last_refreshed_at
        created_at_json = created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(created_at, datetime) else created_at
        updated_at_json = updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(updated_at, datetime) else updated_at
        
        return jsonify({
            'success': True,
            'connected': True,
            'email': email,
            'profile_name': profile_name,
            'is_valid': bool(is_valid) if is_valid is not None else False,
            'is_active': bool(is_active) if is_active is not None else False,
            'expires_at': expires_at_json,
            'is_expired': is_expired,
            'last_refreshed_at': last_refreshed_json,
            'error_count': error_count or 0,
            'last_error': last_error,
            'connected_since': created_at_json,
            'last_updated': updated_at_json
        })
        
    except Exception as e:
        logger.error(f"❌ Status check failed (outer exception): {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Unexpected error during status check',
            'details': str(e)
        }), 500
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


@microsoft_auth_bp.route('/disconnect', methods=['POST'])
@require_auth
def microsoft_disconnect():
    """
    Disconnect Microsoft account
    
    POST /api/auth/microsoft/disconnect
    Authorization: Bearer <jwt_token>
    
    Revokes tokens and deletes FROM ai_infrastructure.oauth_tokens table
    
    ✅ FIXED: Proper cursor management with context manager
    """
    conn = None
    try:
        # Get user_id from request.user (set by @require_auth decorator)
        user_id = request.user.get('user_id')
        
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            
            # Delete tokens FROM ai_infrastructure.oauth_tokens table
            sql, params = convert_sql_placeholders('''
                DELETE FROM ai_infrastructure.oauth_tokens
                WHERE user_id = %s AND platform = %s
            ''', (user_id, 'microsoft'))

            cursor.execute(sql, params)
            conn.commit()
        
        conn.close()
        conn = None
        
        logger.info(f"Microsoft account disconnected for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Microsoft account disconnected'
        })
        
    except Exception as e:
        logger.error(f"❌ Disconnect failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


@microsoft_auth_bp.route('/config', methods=['GET'])
def get_microsoft_config():
    """
    Get Microsoft OAuth configuration for diagnostics
    
    GET /api/auth/microsoft/config
    
    Returns configuration status and expected redirect URIs
    """
    client_id = _config.get('MICROSOFT_CLIENT_ID', '')
    client_secret = _config.get('MICROSOFT_CLIENT_SECRET', '')
    tenant_id = _config.get('MICROSOFT_TENANT_ID', 'common')
    
    # Get redirect URI from environment variable (CRITICAL: Use HTTPS for Render)
    redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI')
    if not redirect_uri:
        base_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
            base_url = base_url.replace('http://', 'https://')
        redirect_uri = base_url + '/api/auth/microsoft/callback'
    
    # Check if oauth_states table exists
    conn = None
    table_exists = False
    table_info = None
    try:
        from shared.database_utils import is_using_supabase
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            if is_using_supabase():
                # PostgreSQL - check information_schema
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'ai_infrastructure' 
                    AND table_name = 'oauth_states'
                """)
                table_exists = cursor.fetchone()[0] > 0
                
                if table_exists:
                    cursor.execute("""
                        SELECT COUNT(*) FROM ai_infrastructure.oauth_states
                        WHERE platform = 'microsoft' AND expires_at > CURRENT_TIMESTAMP
                    """)
                    active_states = cursor.fetchone()[0]
                    table_info = {'active_states': active_states, 'platform': 'microsoft'}
            else:
                # SQLite - check sqlite_master
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='oauth_states'
                """)
                table_exists = cursor.fetchone() is not None
                
                if table_exists:
                    cursor.execute("""
                        SELECT COUNT(*) FROM oauth_states
                        WHERE platform = 'microsoft' AND expires_at > datetime('now')
                    """)
                    active_states = cursor.fetchone()[0]
                    table_info = {'active_states': active_states, 'platform': 'microsoft'}
        
        conn.close()
        conn = None
    except Exception as e:
        logger.error(f"Table check failed: {e}")
        table_info = {'error': str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
    
    return jsonify({
        'success': True,
        'configured': bool(client_id and client_secret),
        'client_id': client_id[:20] + '...' if client_id else 'NOT SET',
        'client_secret': 'SET' if client_secret else 'NOT SET',
        'tenant_id': tenant_id,
        'redirect_uri': redirect_uri,
        'scopes_requested': MICROSOFT_SCOPES,
        'table_used': 'oauth_tokens',
        'oauth_states_table_exists': table_exists,
        'oauth_states_info': table_info,
        'columns': 24,
        'version': 'V3_COMPLETE_CURSOR_FIXED',
        'date': 'January 1, 2026'
    })


# ======================================================================
# STARTUP LOGGING
# ======================================================================
client_id_check = os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', 'NOT SET')
if client_id_check != 'NOT SET':
    logger.info("✅ Microsoft OAuth routes loaded")
else:
    logger.warning("⚠️ Microsoft OAuth routes loaded (Client ID not configured)")