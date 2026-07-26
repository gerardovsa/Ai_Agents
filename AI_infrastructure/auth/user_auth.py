"""
FILE: AI_infrastructure/auth/user_auth.py
PURPOSE: User authentication, profile management, and JWT token handling for multi-tenant system

DEPENDENCIES:
- bcrypt - Password hashing and verification
- jwt (PyJWT) - JSON Web Token generation and validation
- dotenv - Load credentials from .env.master file
- flask - Request/response handling and decorators

EXPORTS:
- UserAuthManager class - Complete authentication system
- require_auth - Flask decorator for protected routes
- user_auth_manager - Global instance

LAST MODIFIED: 2025-01-08 - COMPLETE CURSOR LEAK REFACTOR - All 25 methods fixed
CURSOR AUDIT: ✅ FULLY REFACTORED - All cursor patterns converted to context managers
"""

import os
from pathlib import Path
from dotenv import dotenv_values
import sys

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup paths for imports
ai_infrastructure_path = Path(__file__).parent.parent
if str(ai_infrastructure_path) not in sys.path:
    sys.path.insert(0, str(ai_infrastructure_path))

# Setup logging
from utils.logger_config import setup_logger, log_db

# Import centralized database connection (Supabase PostgreSQL)
from shared.database_utils import get_database_connection
from shared.db_connection_wrapper import get_connection

logger = setup_logger('auth.user_auth')

# Load credentials from .env.master (in root folder, 3 levels up)
_ENV_MASTER_PATH = Path(__file__).parent.parent.parent / '.env.master'
_config = dotenv_values(_ENV_MASTER_PATH)

import json
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from flask import request, jsonify, g
from functools import wraps


class UserAuthManager:
    """Manages user authentication, profiles, and workspace isolation"""
    
    # Class-level flag to track if tables have been checked (prevents repeated logs)
    _tables_initialized = False
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            from utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        self.db_path = str(db_path)
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        self._init_tables()
    
    def _get_db_connection(self):
        """
        Get database connection using centralized utility
        Automatically uses Supabase PostgreSQL
        
        Returns:
            Database connection (psycopg2.Connection)
        """
        return get_database_connection('ai_infrastructure')
    
    def _load_env_gmail_accounts(self) -> List[Dict]:
        """
        Load all Gmail accounts from .env.master for master/admin users
        
        Returns:
            List of Gmail account dicts with email, display_name, is_primary
        """
        accounts = []
        
        # Primary work account
        work_email = os.getenv('WORK_EMAIL')
        if work_email:
            accounts.append({
                'email': work_email,
                'display_name': 'Vet Success Academy',
                'is_primary': True,
                'app_password': os.getenv('WORK_EMAIL_APP_PASSWORD')
            })
        
        # Personal account
        personal_email = os.getenv('PERSONAL_EMAIL')
        if personal_email:
            accounts.append({
                'email': personal_email,
                'display_name': 'Personal',
                'is_primary': False,
                'app_password': os.getenv('PERSONAL_EMAIL_APP_PASSWORD')
            })
        
        # MiniVet Guide - Gerardo
        gerardo_mvg = os.getenv('GERARDO_MVG_EMAIL')
        if gerardo_mvg:
            accounts.append({
                'email': gerardo_mvg,
                'display_name': 'MiniVet Guide - Gerardo',
                'is_primary': False,
                'app_password': None
            })
        
        # MiniVet Guide - Main
        mvg_email = os.getenv('MVG_EMAIL')
        if mvg_email:
            accounts.append({
                'email': mvg_email,
                'display_name': 'MiniVet Guide',
                'is_primary': False,
                'app_password': os.getenv('MVG_EMAIL_APP_PASSWORD')
            })
        
        # MiniVet Guide - Marketing
        mvg_marketing = os.getenv('MVG_MARKETING_EMAIL')
        if mvg_marketing:
            accounts.append({
                'email': mvg_marketing,
                'display_name': 'MiniVet Guide - Marketing',
                'is_primary': False,
                'app_password': None
            })
        
        print(f"[EMAIL] Loaded {len(accounts)} Gmail accounts from .env:")
        for acc in accounts:
            print(f"   - {acc['email']} ({acc['display_name']})")
        
        return accounts
    
    def _init_tables(self):
        """Initialize user authentication tables with retry logic for multi-worker startup"""
        import time
        from shared.database_utils import is_using_supabase
        
        # Skip table creation on Supabase - tables already exist with correct PostgreSQL schema
        if is_using_supabase():
            # Only log once per application lifetime (not per UserAuthManager instance)
            if not UserAuthManager._tables_initialized:
                print("[USER AUTH] Using Supabase - tables verified")
                UserAuthManager._tables_initialized = True
            return
        
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                with get_connection('ai_infrastructure') as conn:
                    with conn.cursor() as cursor:
                        
                        # Enhanced users table - EXACT MATCH to existing schema
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                email TEXT UNIQUE NOT NULL,
                                password_hash TEXT NOT NULL,
                                role TEXT DEFAULT 'user',
                                primary_gmail TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata TEXT,
                                is_primary BOOLEAN DEFAULT 0,
                                allowed_dashboards TEXT,
                                has_google_oauth BOOLEAN DEFAULT 0,
                                has_microsoft_oauth BOOLEAN DEFAULT 0,
                                is_active BOOLEAN DEFAULT 1,
                                parent_user_id INTEGER,
                                is_sub_user BOOLEAN DEFAULT 0,
                                permissions TEXT,
                                allowed_tools TEXT,
                                allowed_agents TEXT,
                                data_access_scope TEXT DEFAULT 'own',
                                usage_limit_daily INTEGER DEFAULT 1000,
                                access_start_time TEXT,
                                access_end_time TEXT,
                                account_expires_at TIMESTAMP
                            )
                        ''')
                        
                        # Gmail accounts linked to users
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS user_gmail_accounts (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                gmail_address TEXT NOT NULL,
                                display_name TEXT,
                                access_token TEXT,
                                refresh_token TEXT,
                                token_expiry TIMESTAMP,
                                is_primary BOOLEAN DEFAULT 0,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                UNIQUE(user_id, gmail_address)
                            )
                        ''')
                        
                        # User sessions (JWT tokens)
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS user_sessions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                token TEXT UNIQUE NOT NULL,
                                ip_address TEXT,
                                user_agent TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                expires_at TIMESTAMP NOT NULL,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                            )
                        ''')
                        
                        # Platform credentials table
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS user_platform_credentials (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                platform TEXT NOT NULL,
                                credential_type TEXT NOT NULL,
                                credential_key TEXT NOT NULL,
                                credential_value TEXT NOT NULL,
                                credentials TEXT,
                                settings TEXT,
                                credential_hash TEXT,
                                rotation_due_at TIMESTAMP,
                                rotation_reminder_sent BOOLEAN DEFAULT 0,
                                validation_status TEXT DEFAULT 'unvalidated',
                                last_validated_at TIMESTAMP,
                                is_active BOOLEAN DEFAULT 1,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata TEXT,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                UNIQUE(user_id, platform, credential_key)
                            )
                        ''')
                        
                        # Update workspaces table to link to users
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS workspaces (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                name TEXT NOT NULL,
                                description TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata TEXT,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                            )
                        ''')
                        
                        # OAuth tokens table
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
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                last_refreshed_at TIMESTAMP,
                                metadata TEXT,
                                account_identifier TEXT,
                                account_name TEXT,
                                is_primary_account BOOLEAN DEFAULT 0,
                                is_valid BOOLEAN DEFAULT 1,
                                is_active BOOLEAN DEFAULT 1,
                                refresh_attempts INTEGER DEFAULT 0,
                                last_refresh_error TEXT,
                                auto_refresh_enabled BOOLEAN DEFAULT 1,
                                granted_scopes TEXT,
                                issued_at TIMESTAMP,
                                revoked_at TIMESTAMP,
                                ip_address_granted TEXT,
                                email TEXT,
                                profile_name TEXT,
                                error_count INTEGER DEFAULT 0,
                                last_error TEXT,
                                profile_picture_url TEXT,
                                profile_data TEXT,
                                link_purpose TEXT DEFAULT 'primary',
                                UNIQUE(user_id, platform),
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                            )
                        ''')
                        
                        # Credential audit log table
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS credential_audit_log (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                platform TEXT NOT NULL,
                                tool_name TEXT,
                                access_type TEXT DEFAULT 'read',
                                query_executed TEXT,
                                ip_address TEXT,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                success BOOLEAN DEFAULT 1,
                                error_message TEXT,
                                session_id TEXT,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                            )
                        ''')
                        
                        # Create indexes for audit log queries
                        cursor.execute('''
                            CREATE INDEX IF NOT EXISTS idx_audit_user_platform 
                            ON credential_audit_log(user_id, platform)
                        ''')
                        cursor.execute('''
                            CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                            ON credential_audit_log(timestamp DESC)
                        ''')
                    
                    conn.commit()
                    log_db(logger, "User authentication tables initialized")
                    break  # Success - exit retry loop
                    
            except Exception as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                    print(f"⚠ [DB] Table creation retry {attempt + 1}/{max_retries}")
                    continue
                else:
                    print(f"❌ [DB] Failed to initialize tables: {e}")
                    raise
    
    def register_user(self, username: str, email: str, password: str, primary_gmail: str = None, role: str = 'user') -> Dict:
        """
        Register new user
        
        Args:
            username: Unique username
            email: User email (can be Gmail)
            password: Plain text password (will be hashed)
            primary_gmail: Optional primary Gmail for OAuth
            role: 'admin' (master account) or 'user' (regular user)
        
        Returns:
            Dict with user_id and success status
        """
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # Create user
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.users (username, email, password_hash, primary_gmail, role, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (username, email, password_hash, primary_gmail or email, role, json.dumps({})))
                    
                    user_id = cursor.lastrowid
                    
                    # Create default workspace
                    cursor.execute('''
                        INSERT INTO workspaces (user_id, name, description, metadata)
                        VALUES (%s, %s, %s, %s)
                    ''', (user_id, f"{username}'s Workspace", "Default workspace", json.dumps({})))
                    
                    workspace_id = cursor.lastrowid
                    
                    # AUTO-LINK ALL .ENV GMAIL ACCOUNTS FOR MASTER/ADMIN USERS
                    if role == 'admin':
                        gmail_accounts = self._load_env_gmail_accounts()
                        for gmail_data in gmail_accounts:
                            cursor.execute('''
                                INSERT INTO user_gmail_accounts 
                                (user_id, gmail_address, display_name, is_primary)
                                VALUES (%s, %s, %s, %s)
                            ''', (user_id, gmail_data['email'], gmail_data['display_name'], gmail_data['is_primary']))
                        
                        print(f"✅ Auto-linked {len(gmail_accounts)} Gmail accounts from .env.master")

                    # CREATE PERSONAL ORG — ensures every user has organisation_id set
                    # so credential resolution uses their own org vault (Tier 2) rather
                    # than falling through to shared env vars (Tier 3).
                    # create_personal_org() is idempotent — safe even if org already exists.
                    personal_org_id = None
                    try:
                        cursor.execute(
                            "SELECT ai_infrastructure.create_personal_org(%s, %s, %s) AS personal_org_id",
                            (user_id, username, username + "'s Workspace")
                        )
                        row = cursor.fetchone()
                        personal_org_id = row['personal_org_id'] if row else None
                        print(f"✅ Personal org created for user {username} (org_id: {personal_org_id})")
                    except Exception as org_err:
                        # Non-fatal: user is still created; org can be backfilled via migration
                        print(f"⚠️ Personal org creation failed for {username}: {org_err}")
                
                conn.commit()
                
                print(f"✅ User registered: {username} (ID: {user_id}, Role: {role}, Workspace: {workspace_id})")
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'workspace_id': workspace_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'organisation_id': personal_org_id,
                    'org_role': 'owner' if personal_org_id else None,
                }
                
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return {
                'success': False,
                'error': 'Username or email already exists' if 'UNIQUE' in str(e) else str(e)
            }
    
    def _refresh_login_location(self, user_id: int, ip_address: Optional[str]) -> None:
        """Best-effort login-time location refresh; authentication never depends on it."""
        if not user_id or not ip_address:
            return

        try:
            from AI_infrastructure.core.ip_location import get_location_from_ip

            location = get_location_from_ip(ip_address)
            if not location or not location.get('resolved_from_ip'):
                return

            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.user_preferences
                            (user_id, detected_country, detected_city,
                             detected_timezone, detected_ip_address,
                             detected_latitude, detected_longitude,
                             last_location_check, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,
                                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO UPDATE SET
                            detected_country = EXCLUDED.detected_country,
                            detected_city = EXCLUDED.detected_city,
                            detected_timezone = EXCLUDED.detected_timezone,
                            detected_ip_address = EXCLUDED.detected_ip_address,
                            detected_latitude = EXCLUDED.detected_latitude,
                            detected_longitude = EXCLUDED.detected_longitude,
                            last_location_check = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (
                        user_id,
                        location.get('country_name') or location.get('country'),
                        location.get('city'),
                        location.get('timezone'),
                        location.get('ip') or ip_address,
                        location.get('latitude'),
                        location.get('longitude'),
                    ))
                conn.commit()
        except Exception as e:
            print(f"[AUTH] Login location refresh skipped: {e}")

    def generate_jwt(self, user_data: Dict) -> str:
        """
        Generate JWT token for a user (used for OAuth and dev mode)
        
        Args:
            user_data: Dict with user info (id, username, email, role)
        
        Returns:
            JWT token string
        """
        try:
            token_payload = {
                'user_id': user_data.get('id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'role': user_data.get('role', 'user'),
                'exp': int((datetime.utcnow() + timedelta(days=30)).timestamp())
            }
            
            token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
            
            # Capture device info from Flask request context
            device_info = {}
            ip_address = None
            user_agent = None
            
            try:
                from flask import request
                if request:
                    forwarded_for = request.headers.get('X-Forwarded-For', '')
                    ip_address = forwarded_for.split(',')[0].strip() or request.remote_addr
                    user_agent = request.headers.get('User-Agent', '')
                    device_info = self.parse_user_agent(user_agent)
            except (ImportError, RuntimeError):
                pass
            
            # Store session in database with device info
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.user_sessions (user_id, token, expires_at, ip_address, user_agent, device_info)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (user_data.get('id'), token, token_payload['exp'], ip_address, user_agent, json.dumps(device_info) if device_info else '{}'))
                
                conn.commit()
                print(f"✅ Session created for user {user_data.get('id')} from {device_info.get('browser', 'Unknown')} on {device_info.get('os', 'Unknown')}")

            self._refresh_login_location(user_data.get('id'), ip_address)
            return token
            
        except Exception as e:
            print(f"⚠️ Could not store session: {e}")
            # Return token anyway (session storage is optional)
            return token if 'token' in locals() else ''
    
    def login(self, username: str, password: str) -> Dict:
        """
        Authenticate user and generate JWT token
        
        Args:
            username: Username or email
            password: Plain text password
        
        Returns:
            Dict with token and user info
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    
                    # Find user by username or email
                    # GAP-L1 FIX: JOIN organisations to include plan_tier in JWT
                    cursor.execute('''
                        SELECT u.id, u.username, u.email, u.password_hash, u.role, u.primary_gmail,
                               u.organisation_id, u.org_role, COALESCE(u.jwt_version, 1) AS jwt_version,
                               COALESCE(o.plan_tier, 'starter') AS plan_tier
                        FROM ai_infrastructure.users u
                        LEFT JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
                        WHERE u.username = %s OR u.email = %s
                    ''', (username, username))
                    
                    row = cursor.fetchone()
                    
                    if not row:
                        return {'success': False, 'error': 'Invalid credentials'}
                    
                    user_id = row['id'] if isinstance(row, dict) else row[0]
                    username = row['username'] if isinstance(row, dict) else row[1]
                    email = row['email'] if isinstance(row, dict) else row[2]
                    password_hash = row['password_hash'] if isinstance(row, dict) else row[3]
                    role = row['role'] if isinstance(row, dict) else row[4]
                    primary_gmail = row['primary_gmail'] if isinstance(row, dict) else row[5]
                    organisation_id = row['organisation_id'] if isinstance(row, dict) else row[6]
                    org_role = row['org_role'] if isinstance(row, dict) else row[7]
                    jwt_version = int(row['jwt_version'] if isinstance(row, dict) else row[8])
                    plan_tier = row['plan_tier'] if isinstance(row, dict) else row[9]
                    
                    # Verify password
                    if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                        return {'success': False, 'error': 'Invalid credentials'}
                    
                    # Get user's workspaces
                    cursor.execute('''
                        SELECT id, name FROM workspaces WHERE user_id = %s
                    ''', (user_id,))
                    workspaces = [
                        {
                            'id': w['id'] if isinstance(w, dict) else w[0],
                            'name': w['name'] if isinstance(w, dict) else w[1]
                        }
                        for w in cursor.fetchall()
                    ]
                    
                    # Get linked Gmail accounts
                    cursor.execute('''
                        SELECT gmail_address, display_name, is_primary
                        FROM user_gmail_accounts
                        WHERE user_id = %s
                    ''', (user_id,))
                    gmail_accounts = [
                        {
                            'email': g['gmail_address'] if isinstance(g, dict) else g[0],
                            'display_name': (g['display_name'] if isinstance(g, dict) else g[1]) or (g['gmail_address'] if isinstance(g, dict) else g[0]),
                            'is_primary': bool(g['is_primary'] if isinstance(g, dict) else g[2])
                        }
                        for g in cursor.fetchall()
                    ]
                    
                    # Generate JWT token
                    exp_time = datetime.utcnow() + timedelta(days=30)
                    exp_timestamp = int(exp_time.timestamp())
                    
                    token_payload = {
                        'user_id': user_id,
                        'username': username,
                        'email': email,
                        'role': role,
                        'organisation_id': organisation_id,
                        'org_role': org_role,
                        'jwt_version': jwt_version,  # GAP-C4: version counter for instant revocation
                        'plan_tier': plan_tier,       # GAP-L1: avoids extra DB hit per request
                        'exp': exp_timestamp
                    }
                    
                    token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
                    
                    # Capture device info from Flask request context
                    device_info = {}
                    ip_address = None
                    user_agent = None
                    
                    try:
                        from flask import request
                        if request:
                            ip_address = request.remote_addr
                            user_agent = request.headers.get('User-Agent', '')
                            device_info = self.parse_user_agent(user_agent)
                    except (ImportError, RuntimeError):
                        pass
                    
                    # Store session with device info
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.user_sessions (user_id, token, expires_at, ip_address, user_agent, device_info)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (user_id, token, exp_time.strftime('%Y-%m-%d %H:%M:%S'), ip_address, user_agent, json.dumps(device_info) if device_info else '{}'))
                    
                    # Update last active
                    cursor.execute('''
                        UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = %s
                    ''', (user_id,))
                
                conn.commit()
                
                self._refresh_login_location(user_id, ip_address)
                print(f"✅ User logged in: {username}")
                
                return {
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'role': role,
                        'organisation_id': organisation_id,
                        'org_role': org_role,
                        'primary_gmail': primary_gmail,
                        'workspaces': workspaces,
                        'gmail_accounts': gmail_accounts
                    }
                }
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token and return user info
        
        Args:
            token: JWT token string
        
        Returns:
            User data dict or None if invalid
        """
        print("\n" + "="*60)
        print("🔧 STAGE 2: TOKEN VERIFICATION STARTED")
        print("="*60)
        print(f"   Token length: {len(token)} characters")
        print(f"   First 20 chars: {token[:20]}...")
        print(f"   Database: ai_infrastructure schema")
        
        try:
            print(f"\n📊 STAGE 2.1: JWT Signature Validation")
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            print(f"   ✅ JWT signature valid")
            print(f"   User ID: {payload.get('user_id')}")
            print(f"   Email: {payload.get('email')}")
            print(f"   Username: {payload.get('username')}")
            
            print(f"\n📊 STAGE 2.2: Database Token Lookup")
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    
                    # First check total sessions in database
                    cursor.execute('SELECT COUNT(*) FROM ai_infrastructure.user_sessions')
                    result = cursor.fetchone()
                    total_sessions = result['count'] if isinstance(result, dict) else result[0]
                    print(f"   Total sessions in DB: {total_sessions}")
                    
                    cursor.execute('''
                        SELECT user_id, expires_at FROM ai_infrastructure.user_sessions
                        WHERE token = %s
                    ''', (token,))
                    
                    result = cursor.fetchone()
                    if not result:
                        print(f"   ❌ Token NOT found in database")
                        print(f"\n❌ STAGE 2 FAILED: Token not in database")
                        print("="*60 + "\n")
                        return None
                    
                    print(f"   ✅ Token found in database")
                    user_id = result['user_id'] if isinstance(result, dict) else result[0]
                    expires_at = result['expires_at'] if isinstance(result, dict) else result[1]
                    print(f"   User ID from DB: {user_id}")
                    print(f"   Expires at: {expires_at}")
                    
                    print(f"\n📊 STAGE 2.3: Expiry Check")
                    from AI_infrastructure.shared.database_utils import is_using_supabase
                    from datetime import datetime
                    
                    if is_using_supabase():
                        cursor.execute("SELECT NOW() as current_time")
                    else:
                        cursor.execute("SELECT CURRENT_TIMESTAMP as current_time")
                    
                    time_result = cursor.fetchone()
                    current_time = time_result['current_time'] if isinstance(time_result, dict) else time_result[0]
                    
                    # Convert to comparable datetime objects
                    if isinstance(current_time, str):
                        current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                    if isinstance(expires_at, str):
                        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    
                    # Remove timezone info for comparison if needed
                    if current_time.tzinfo is not None and expires_at.tzinfo is None:
                        current_time = current_time.replace(tzinfo=None)
                    elif current_time.tzinfo is None and expires_at.tzinfo is not None:
                        expires_at = expires_at.replace(tzinfo=None)
                    
                    print(f"   Current time: {current_time}")
                    print(f"   Token expires: {expires_at}")
                    
                    if expires_at <= current_time:
                        print(f"   ❌ Token EXPIRED")
                        print("\n❌ STAGE 2 FAILED: Token expired")
                        print("="*60 + "\n")
                        return None
                    
                    print(f"   ✅ Token is valid (not expired)")
                
                print(f"\n✅ STAGE 2 COMPLETE: Token verified successfully")
                print("="*60 + "\n")
                return payload
            
        except jwt.ExpiredSignatureError:
            print(f"\n❌ STAGE 2 FAILED: Token expired (JWT signature)")
            print("="*60 + "\n")
            return None
        except jwt.InvalidTokenError as e:
            print(f"\n❌ STAGE 2 FAILED: Invalid token (JWT): {e}")
            print("="*60 + "\n")
            return None
        except Exception as e:
            print(f"\n❌ STAGE 2 FAILED: Token verification error: {e}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
            return None
    
    def link_gmail_account(self, user_id: int, gmail_address: str, display_name: str = None,
                          access_token: str = None, refresh_token: str = None,
                          is_primary: bool = False) -> Dict:
        """Link Gmail account to user profile"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # If setting as primary, unset other primary accounts
                    if is_primary:
                        cursor.execute('''
                            UPDATE user_gmail_accounts
                            SET is_primary = 0
                            WHERE user_id = %s
                        ''', (user_id,))
                    
                    # Insert or update Gmail account
                    cursor.execute('''
                        INSERT INTO user_gmail_accounts 
                        (user_id, gmail_address, display_name, access_token, refresh_token, is_primary)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT(user_id, gmail_address) DO UPDATE SET
                            display_name = excluded.display_name,
                            access_token = excluded.access_token,
                            refresh_token = excluded.refresh_token,
                            is_primary = excluded.is_primary
                    ''', (user_id, gmail_address, display_name, access_token, refresh_token, is_primary))
                
                conn.commit()
                
                print(f"✅ Gmail linked: {gmail_address} → User {user_id}")
                
                return {'success': True, 'gmail': gmail_address}
                
        except Exception as e:
            print(f"❌ Gmail link error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_gmail_accounts(self, user_id: int) -> List[Dict]:
        """Get all Gmail accounts linked to user"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT gmail_address, display_name, is_primary, created_at
                        FROM user_gmail_accounts
                        WHERE user_id = %s
                        ORDER BY is_primary DESC, created_at ASC
                    ''', (user_id,))
                    
                    rows = cursor.fetchall()
                    
                    return [
                        {
                            'email': row[0] if not isinstance(row, dict) else row['gmail_address'],
                            'display_name': (row[1] if not isinstance(row, dict) else row['display_name']) or (row[0] if not isinstance(row, dict) else row['gmail_address']),
                            'is_primary': bool(row[2] if not isinstance(row, dict) else row['is_primary']),
                            'created_at': row[3] if not isinstance(row, dict) else row['created_at']
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting Gmail accounts: {e}")
            return []
    
    def get_user_workspace(self, user_id: int) -> Optional[int]:
        """Get user's default workspace ID"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT id FROM workspaces WHERE user_id = %s LIMIT 1
                    ''', (user_id,))
                    row = cursor.fetchone()
                    
                    return (row[0] if not isinstance(row, dict) else row['id']) if row else None
        except Exception as e:
            print(f"❌ Error getting workspace: {e}")
            return None
    
    # ==================== PLATFORM CREDENTIALS MANAGEMENT ====================
    
    def store_platform_credential(self, user_id: int, platform: str, 
                                  credentials_dict: Dict, 
                                  settings_dict: Dict = None,
                                  credential_type: str = 'api_key',
                                  validate_schema: bool = True) -> Dict:
        """Store platform credentials for user with flexible schema validation"""
        try:
            # Validate against platform schema
            if validate_schema:
                try:
                    from AI_infrastructure.auth.platform_credential_schemas import validate_platform_credentials
                    validated_creds = validate_platform_credentials(platform, credentials_dict)
                    credentials_dict = validated_creds
                    print(f"✅ Schema validation passed for {platform}")
                except ImportError:
                    print(f"⚠️ Schema validation skipped (platform_credential_schemas.py not found)")
                except ValueError as ve:
                    return {
                        'success': False, 
                        'error': f'Schema validation failed: {str(ve)}',
                        'validation_errors': str(ve)
                    }
            
            # SECURITY: Encrypt credentials before storage
            from AI_infrastructure.auth.credential_encryptor import get_encryptor
            encryptor = get_encryptor()
            encrypted_credentials = encryptor.encrypt_dict(credentials_dict)
            print(f"🔐 Encrypted {len(encrypted_credentials)} credential fields for {platform}")
            
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # Use encrypted credentials for storage
                    credentials_json = json.dumps(encrypted_credentials)
                    settings_json = json.dumps(settings_dict) if settings_dict else '{}'
                    
                    # Calculate credential hash for change detection (SHA256)
                    import hashlib
                    cred_hash = hashlib.sha256(credentials_json.encode()).hexdigest()
                    
                    # Calculate rotation due date (90 days for API keys, 24h for OAuth)
                    from datetime import datetime, timedelta
                    if credential_type == 'oauth_token':
                        rotation_due = datetime.now() + timedelta(hours=24)
                    else:
                        rotation_due = datetime.now() + timedelta(days=90)
                    
                    # Check if credential already exists
                    cursor.execute('''
                        SELECT id, credential_hash FROM user_platform_credentials
                        WHERE user_id = %s AND platform = %s
                    ''', (user_id, platform))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        existing_id = existing['id'] if isinstance(existing, dict) else existing[0]
                        existing_hash = existing['credential_hash'] if isinstance(existing, dict) else (existing[1] if len(existing) > 1 else None)
                        
                        if existing_hash == cred_hash:
                            print(f"ℹ️ {platform} credentials unchanged for user {user_id}")
                            return {'success': True, 'changed': False, 'message': 'Credentials unchanged'}
                        
                        # Update existing credential
                        cursor.execute('''
                            UPDATE user_platform_credentials
                            SET credentials = %s::jsonb,
                                settings = %s::jsonb,
                                credential_type = %s,
                                credential_hash = %s,
                                rotation_due_at = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        ''', (credentials_json, settings_json, credential_type, cred_hash, rotation_due, existing_id))
                        print(f"✅ Updated {platform} credentials for user {user_id}")
                    else:
                        # Insert new credential
                        cursor.execute('''
                            INSERT INTO ai_infrastructure.user_platform_credentials 
                            (user_id, platform, credential_type, credential_key, credential_value, 
                             credentials, settings, credential_hash, rotation_due_at)
                            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s)
                        ''', (user_id, platform, credential_type, f'{platform.upper()}_CREDENTIALS', '', 
                              credentials_json, settings_json, cred_hash, rotation_due))
                        print(f"✅ Inserted {platform} credentials for user {user_id}")
                
                conn.commit()
                
                return {
                    'success': True, 
                    'changed': True,
                    'platform': platform,
                    'rotation_due': rotation_due.isoformat()
                }
                
        except Exception as e:
            print(f"❌ Store credential error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def log_credential_access(self, user_id: int, platform: str, tool_name: str = None,
                              access_type: str = 'read', query: str = None,
                              success: bool = True, error_message: str = None):
        """
        Log credential access for audit trail
        
        Args:
            user_id: User ID accessing credentials
            platform: Platform being accessed (google, microsoft, inhouse_print, etc.)
            tool_name: Tool/function name requesting credentials
            access_type: Type of access (read, write, delete)
            query: SQL query or API endpoint (truncated to 500 chars)
            success: Whether access was successful
            error_message: Error message if access failed
        """
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # Get IP address from Flask request context (if available)
                    ip_address = None
                    try:
                        from flask import request
                        ip_address = request.remote_addr if request else None
                    except (ImportError, RuntimeError):
                        pass
                    
                    # Truncate long queries
                    if query and len(query) > 500:
                        query = query[:500] + '... [truncated]'
                    
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.credential_audit_log 
                        (user_id, platform, tool_name, access_type, query_executed, 
                         ip_address, success, error_message)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        user_id, platform, tool_name, access_type, query,
                        ip_address, success, error_message
                    ))
                
                conn.commit()
                
        except Exception as e:
            # Don't fail the main operation if logging fails
            logger.warning(f'Failed to log credential access: {e}')
    
    def get_platform_credentials(self, user_id: int, platform: str, 
                             include_settings: bool = False,
                             include_metadata: bool = False) -> Dict[str, str]:
        """
        Get all credentials for a platform for this user with flexible schema support
        
        Args:
            user_id: User ID
            platform: Platform name
            include_settings: Include settings dict in response (default: False)
            include_metadata: Include validation/rotation metadata (default: False)
        
        Returns:
            Dict of credentials from JSONB column or oauth_tokens table
        """
        result = {}
        
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # Platform name aliases for OAuth
                    platform_aliases = {
                        'google_workspace': 'google',
                        'gmail': 'google',
                        'google_docs': 'google',
                        'google_sheets': 'google',
                        'microsoft_365': 'microsoft',
                        'outlook': 'microsoft',
                        'onedrive': 'microsoft'
                    }
                    
                    oauth_platform = platform_aliases.get(platform.lower(), platform.lower())
                    
                    # Try oauth_tokens table first (for OAuth platforms)
                    try:
                        cursor.execute('''
                            SELECT access_token
                            FROM ai_infrastructure.oauth_tokens
                            WHERE user_id = %s AND platform = %s AND is_active = TRUE
                            ORDER BY updated_at DESC
                            LIMIT 1
                        ''', (user_id, oauth_platform))
                        
                        oauth_row = cursor.fetchone()
                        
                        if oauth_row:
                            access_token = oauth_row['access_token'] if isinstance(oauth_row, dict) else oauth_row[0]
                            logger.debug(f"Found OAuth credentials for user {user_id}, platform {oauth_platform}")
                            result = {'access_token': access_token}
                            
                    except Exception as e:
                        print(f"⚠️ OAuth token lookup failed: {e}")
                        # Continue to try platform credentials
                    
                    # If OAuth didn't find anything, try user_platform_credentials
                    if not result:
                        try:
                            # Two-tier credential lookup with fallback to platform user (user_id = 1)
                            # 1. Check user-specific credentials first
                            cursor.execute('''
                                SELECT credential_key, credential_value, credentials, metadata
                                FROM ai_infrastructure.user_platform_credentials
                                WHERE user_id = %s AND platform = %s AND is_active = TRUE
                            ''', (user_id, platform))
                            
                            rows = cursor.fetchall()
                            
                            # 2. If no user-specific credentials, fall back to platform global credentials (user_id = 1)
                            if not rows and user_id != 1:
                                print(f"[CREDENTIALS] No {platform} credentials for user {user_id}, checking platform global (user_id=1)...")
                                cursor.execute('''
                                    SELECT credential_key, credential_value, credentials, metadata
                                    FROM ai_infrastructure.user_platform_credentials
                                    WHERE user_id = 1 AND platform = %s AND is_active = TRUE
                                ''', (platform,))
                                
                                rows = cursor.fetchall()
                                if rows:
                                    print(f"✅ [CREDENTIALS] Using platform global {platform} credentials for user {user_id}")
                            
                            if rows:
                                result = {}
                                
                                # First, add all key-value pairs from credential_key/credential_value columns
                                for row in rows:
                                    key = row['credential_key'] if isinstance(row, dict) else row[0]
                                    value = row['credential_value'] if isinstance(row, dict) else row[1]
                                    result[key] = value
                                
                                # Then, merge in the credentials JSONB object (preferred source)
                                for row in rows:
                                    credentials_json = row.get('credentials') if isinstance(row, dict) else (row[2] if len(row) > 2 else None)
                                    if credentials_json and isinstance(credentials_json, dict):
                                        result.update(credentials_json)
                                        break
                                
                                # Also merge metadata if needed
                                for row in rows:
                                    metadata_json = row.get('metadata') if isinstance(row, dict) else (row[3] if len(row) > 3 else None)
                                    if metadata_json and isinstance(metadata_json, dict):
                                        for meta_key, meta_value in metadata_json.items():
                                            if meta_key not in result:
                                                result[meta_key] = meta_value
                                        break
                                
                        except Exception as e:
                            print(f"⚠️ Platform credentials lookup failed: {e}")
                            result = {}
            
            # SECURITY: Auto-decrypt credentials before returning
            if result:
                from AI_infrastructure.auth.credential_encryptor import get_encryptor
                encryptor = get_encryptor()
                result = encryptor.decrypt_dict(result)
                print(f"🔓 Decrypted {len(result)} credential fields for {platform}")
            
            # Log successful credential access with audit trail
            if result:
                self.log_credential_access(
                    user_id=user_id,
                    platform=platform,
                    tool_name='get_platform_credentials',
                    access_type='read',
                    success=True
                )
            
            return result
            
        except Exception as e:
            print(f"❌ get_platform_credentials error: {e}")
            # Log failed access
            self.log_credential_access(
                user_id=user_id,
                platform=platform,
                tool_name='get_platform_credentials',
                access_type='read',
                success=False,
                error_message=str(e)
            )
            return {}
    
    def get_user_credential(self, user_id: int, platform: str, credential_key: str) -> Optional[str]:
        """Get specific credential for user"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # Try oauth_tokens table first
                    if credential_key == 'access_token':
                        cursor.execute('''
                            SELECT access_token
                            FROM ai_infrastructure.oauth_tokens
                            WHERE user_id = %s AND platform = %s AND is_active = TRUE
                            ORDER BY updated_at DESC
                            LIMIT 1
                        ''', (user_id, platform))
                        
                        row = cursor.fetchone()
                        if row:
                            return row[0] if not isinstance(row, dict) else row['access_token']
                    
                    # Fallback to old table
                    cursor.execute('''
                        SELECT credential_value
                        FROM user_platform_credentials
                        WHERE user_id = %s AND platform = %s AND credential_key = %s AND is_active = TRUE
                    ''', (user_id, platform, credential_key))
                    
                    row = cursor.fetchone()
                    
                    return (row[0] if not isinstance(row, dict) else row['credential_value']) if row else None
                    
        except Exception as e:
            print(f"❌ Error getting credential: {e}")
            return None
    
    def list_user_platforms(self, user_id: int) -> List[str]:
        """List all platforms user has credentials for"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT DISTINCT platform
                        FROM ai_infrastructure.oauth_tokens
                        WHERE user_id = %s AND is_active = TRUE
                        
                        UNION
                        
                        SELECT DISTINCT platform
                        FROM ai_infrastructure.user_platform_credentials
                        WHERE user_id = %s AND is_active = TRUE
                        
                        ORDER BY platform
                    ''', (user_id, user_id))
                    
                    rows = cursor.fetchall()
                    
                    return [row[0] if not isinstance(row, dict) else row['platform'] for row in rows]
                    
        except Exception as e:
            print(f"❌ Error listing platforms: {e}")
            return []
    
    def store_platform_settings(self, user_id: int, platform: str, settings_dict: Dict) -> Dict:
        """Update platform settings without touching credentials"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    settings_json = json.dumps(settings_dict)
                    
                    cursor.execute('''
                        UPDATE user_platform_credentials
                        SET settings = %s::jsonb,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s AND platform = %s
                    ''', (settings_json, user_id, platform))
                    
                    rowcount = cursor.rowcount
                    
                    if rowcount == 0:
                        return {'success': False, 'error': f'No credentials found for {platform}'}
                
                conn.commit()
                print(f"✅ Updated settings for {platform} (user {user_id})")
                
                return {'success': True, 'platform': platform}
                
        except Exception as e:
            print(f"❌ Store settings error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_platform_credential(self, user_id: int, platform: str) -> Dict:
        """Test platform credential by making API call"""
        try:
            from datetime import datetime
            
            creds = self.get_platform_credentials(user_id, platform)
            if not creds:
                return {'success': False, 'error': 'No credentials found'}
            
            validation_status = 'unvalidated'
            error_message = None
            
            if platform == 'assemblyai':
                try:
                    import assemblyai as aai
                    aai.settings.api_key = creds.get('api_key')
                    transcriber = aai.Transcriber()
                    validation_status = 'valid'
                except Exception as e:
                    validation_status = 'invalid'
                    error_message = str(e)
            
            elif platform == 'twilio':
                try:
                    from twilio.rest import Client
                    client = Client(creds.get('account_sid'), creds.get('auth_token'))
                    account = client.api.accounts(creds.get('account_sid')).fetch()
                    validation_status = 'valid'
                except Exception as e:
                    validation_status = 'invalid'
                    error_message = str(e)
            
            elif platform == 'openai':
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=creds.get('api_key'))
                    models = client.models.list()
                    validation_status = 'valid'
                except Exception as e:
                    validation_status = 'invalid'
                    error_message = str(e)
            
            else:
                return {'success': False, 'error': f'Validation not implemented for {platform}'}
            
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        UPDATE user_platform_credentials
                        SET validation_status = %s,
                            last_validated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s AND platform = %s
                    ''', (validation_status, user_id, platform))
                
                conn.commit()
            
            result = {
                'success': True,
                'platform': platform,
                'validation_status': validation_status,
                'tested_at': datetime.now().isoformat()
            }
            
            if error_message:
                result['error_message'] = error_message
            
            return result
            
        except Exception as e:
            print(f"❌ Test credential error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def get_credentials_due_for_rotation(self, days_ahead: int = 7) -> List[Dict]:
        """Get list of credentials needing rotation soon"""
        try:
            from datetime import datetime, timedelta
            
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cutoff_date = datetime.now() + timedelta(days=days_ahead)
                    
                    cursor.execute('''
                        SELECT user_id, platform, rotation_due_at, credential_type,
                               last_validated_at, validation_status
                        FROM user_platform_credentials
                        WHERE is_active = TRUE
                          AND rotation_due_at IS NOT NULL
                          AND rotation_due_at <= %s
                          AND rotation_reminder_sent = FALSE
                        ORDER BY rotation_due_at ASC
                    ''', (cutoff_date,))
                    
                    rows = cursor.fetchall()
                    results = []
                    
                    for row in rows:
                        if isinstance(row, dict):
                            results.append({
                                'user_id': row['user_id'],
                                'platform': row['platform'],
                                'rotation_due_at': str(row['rotation_due_at']),
                                'credential_type': row['credential_type'],
                                'last_validated_at': str(row['last_validated_at']) if row.get('last_validated_at') else None,
                                'validation_status': row.get('validation_status', 'unvalidated')
                            })
                        else:
                            results.append({
                                'user_id': row[0],
                                'platform': row[1],
                                'rotation_due_at': str(row[2]),
                                'credential_type': row[3],
                                'last_validated_at': str(row[4]) if len(row) > 4 and row[4] else None,
                                'validation_status': row[5] if len(row) > 5 else 'unvalidated'
                            })
                    
                    return results
                    
        except Exception as e:
            print(f"❌ Get rotation list error: {e}")
            return []
    
    def mark_rotation_reminder_sent(self, user_id: int, platform: str) -> Dict:
        """Mark that rotation reminder was sent"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        UPDATE user_platform_credentials
                        SET rotation_reminder_sent = TRUE
                        WHERE user_id = %s AND platform = %s
                    ''', (user_id, platform))
                
                conn.commit()
                
                return {'success': True}
                
        except Exception as e:
            print(f"❌ Mark reminder sent error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_google_oauth_credentials(self, user_id: int) -> Optional[Dict]:
        """Get Google OAuth credentials for user from oauth_tokens table"""
        conn = None
        try:
            # 🔒 LEAK FIX: Defensive connection handling to prevent cascading failures
            try:
                conn = get_connection('ai_infrastructure')
            except Exception as conn_err:
                logger.warning(f"[AUTH] Connection pool exhausted for user {user_id} Google OAuth check: {conn_err}")
                return None
            
            with conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT
                            id,
                            access_token,
                            refresh_token,
                            token_type,
                            expires_at,
                            scope,
                            granted_scopes,
                            metadata,
                            is_valid,
                            is_active,
                            link_purpose,
                            account_identifier,
                            email
                        FROM ai_infrastructure.oauth_tokens
                        WHERE user_id = %s AND platform = 'google'
                        AND is_active = TRUE
                        ORDER BY updated_at DESC
                        LIMIT 1
                    ''', (user_id,))
                    
                    token_row = cursor.fetchone()
                    if not token_row:
                        print(f"⚠️ No Google OAuth credentials found for user {user_id}")
                        return None
                    
                    token_id = token_row['id'] if isinstance(token_row, dict) else token_row[0]
                    access_token = token_row['access_token'] if isinstance(token_row, dict) else token_row[1]
                    refresh_token = token_row['refresh_token'] if isinstance(token_row, dict) else token_row[2]
                    expires_at = token_row['expires_at'] if isinstance(token_row, dict) else token_row[4]
                    scope = (token_row['scope'] if isinstance(token_row, dict) else token_row[5]) or (token_row['granted_scopes'] if isinstance(token_row, dict) else token_row[6]) or ''
                    metadata_value = token_row['metadata'] if isinstance(token_row, dict) else token_row[7]
                    metadata = json.loads(metadata_value) if isinstance(metadata_value, str) and metadata_value else (metadata_value or {})
                    is_valid = token_row['is_valid'] if isinstance(token_row, dict) else token_row[8]
                    link_purpose = (token_row['link_purpose'] if isinstance(token_row, dict) else token_row[10]) or 'primary'
                    account_identifier = token_row['account_identifier'] if isinstance(token_row, dict) else token_row[11]
                    email = token_row['email'] if isinstance(token_row, dict) else token_row[12]

                    if not is_valid:
                        logger.warning(f"[AUTH] Google OAuth credentials are marked invalid for user {user_id}")
                        return None

                client_id = (os.getenv('GOOGLE_OAUTH_CLIENT_ID') or os.getenv('GOOGLE_CLIENT_ID') or
                            _config.get('GOOGLE_OAUTH_CLIENT_ID') or _config.get('GOOGLE_CLIENT_ID'))
                client_secret = (os.getenv('GOOGLE_OAUTH_CLIENT_SECRET') or os.getenv('GOOGLE_CLIENT_SECRET') or
                                _config.get('GOOGLE_OAUTH_CLIENT_SECRET') or _config.get('GOOGLE_CLIENT_SECRET'))
                
                if not client_id or not client_secret:
                    print(f"❌ Google OAuth config not found")
                    return None
                
                if isinstance(scope, list):
                    scopes = [str(item) for item in scope if item]
                elif isinstance(scope, str) and scope:
                    try:
                        parsed_scopes = json.loads(scope)
                    except (TypeError, json.JSONDecodeError):
                        parsed_scopes = None
                    scopes = parsed_scopes if isinstance(parsed_scopes, list) else scope.split()
                else:
                    scopes = [
                        'https://www.googleapis.com/auth/gmail.modify',
                        'https://www.googleapis.com/auth/calendar',
                        'https://www.googleapis.com/auth/tasks',
                        'https://www.googleapis.com/auth/forms.body',
                        'https://www.googleapis.com/auth/drive.file',
                        'https://www.googleapis.com/auth/documents',
                        'https://www.googleapis.com/auth/spreadsheets'
                    ]

                credentials = {
                    'token_id': token_id,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'scopes': scopes,
                    'expires_at': expires_at,
                    'user_id': user_id,
                    'metadata': metadata,
                    'link_purpose': link_purpose,
                    'account_identifier': account_identifier,
                    'email': email or account_identifier
                }
                
                return credentials
                
        except Exception as e:
            print(f"❌ Error retrieving Google OAuth credentials: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_microsoft_oauth_credentials(self, user_id: int) -> Optional[Dict]:
        """Get Microsoft 365 OAuth credentials for user from oauth_tokens table"""
        conn = None
        try:
            # 🔒 LEAK FIX: Defensive connection handling to prevent cascading failures
            try:
                conn = get_connection('ai_infrastructure')
            except Exception as conn_err:
                logger.warning(f"[AUTH] Connection pool exhausted for user {user_id} Microsoft OAuth check: {conn_err}")
                return None
            
            with conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT 
                            access_token,
                            refresh_token,
                            token_type,
                            expires_at,
                            scope,
                            granted_scopes,
                            metadata,
                            is_valid,
                            is_active
                        FROM ai_infrastructure.oauth_tokens
                        WHERE user_id = %s AND platform = 'microsoft'
                        AND is_active = TRUE
                        ORDER BY updated_at DESC
                        LIMIT 1
                    ''', (user_id,))
                    
                    token_row = cursor.fetchone()
                    if not token_row:
                        print(f"⚠️ No Microsoft OAuth credentials found for user {user_id}")
                        return None
                    
                    access_token = token_row['access_token'] if isinstance(token_row, dict) else token_row[0]
                    refresh_token = token_row['refresh_token'] if isinstance(token_row, dict) else token_row[1]
                    expires_at = token_row['expires_at'] if isinstance(token_row, dict) else token_row[3]
                    scope = (token_row['scope'] if isinstance(token_row, dict) else token_row[4]) or (token_row['granted_scopes'] if isinstance(token_row, dict) else token_row[5]) or ''
                    metadata = json.loads(token_row['metadata'] if isinstance(token_row, dict) else token_row[6]) if (token_row['metadata'] if isinstance(token_row, dict) else token_row[6]) else {}
                
                client_id = os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID')
                client_secret = os.getenv('MICROSOFT_CLIENT_SECRET') or _config.get('MICROSOFT_CLIENT_SECRET')
                tenant_id = os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common')
                
                if not client_id or not client_secret:
                    print(f"❌ Microsoft OAuth config not found")
                    return None
                
                scopes = scope.split(' ') if isinstance(scope, str) and scope else [
                    'User.Read',
                    'Mail.Read',
                    'Mail.Send',
                    'Calendars.ReadWrite',
                    'Tasks.ReadWrite',
                    'Files.ReadWrite.All'
                ]
                
                credentials = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_uri': f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'tenant_id': tenant_id,
                    'scopes': scopes,
                    'expires_at': expires_at,
                    'user_id': user_id,
                    'metadata': metadata
                }
                
                print(f"✅ Retrieved Microsoft OAuth credentials for user {user_id}")
                return credentials
                
        except Exception as e:
            print(f"❌ Error retrieving Microsoft OAuth credentials: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ==================== MICROSOFT 365 OAUTH SUPPORT ====================
    
    def store_microsoft_tokens(self, user_id: int, access_token: str, refresh_token: str, 
                               expires_at: str, microsoft_id: str = None, microsoft_email: str = None,
                               link_purpose: str = 'primary'):
        """
        Store Microsoft OAuth tokens for a user
        
        Args:
            user_id: User ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_at: Token expiration timestamp
            microsoft_id: Microsoft account ID
            microsoft_email: Microsoft account email
            link_purpose: 'primary' (full access) or 'storage' (OneDrive only)
        """
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        INSERT INTO oauth_tokens
                        (user_id, platform, access_token, refresh_token, expires_at, 
                         metadata, account_identifier, account_name, is_active, link_purpose, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT(user_id, platform) DO UPDATE SET
                            access_token = excluded.access_token,
                            refresh_token = excluded.refresh_token,
                            expires_at = excluded.expires_at,
                            metadata = excluded.metadata,
                            account_identifier = excluded.account_identifier,
                            account_name = excluded.account_name,
                            link_purpose = excluded.link_purpose,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (
                        user_id,
                        'microsoft',
                        access_token,
                        refresh_token,
                        expires_at,
                        json.dumps({
                            'microsoft_id': microsoft_id,
                            'microsoft_email': microsoft_email
                        }),
                        microsoft_email,
                        microsoft_email,
                        link_purpose
                    ))
                
                conn.commit()
                print(f"✅ Stored Microsoft tokens for user {user_id} (purpose: {link_purpose})")
                
        except Exception as e:
            print(f"❌ Failed to store Microsoft tokens: {e}")
    
    def get_microsoft_tokens(self, user_id: int) -> Optional[Dict]:
        """Get Microsoft OAuth tokens for a user"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT access_token, refresh_token, expires_at, metadata, created_at
                        FROM ai_infrastructure.oauth_tokens
                        WHERE user_id = %s AND platform = 'microsoft'
                        AND is_active = TRUE
                        ORDER BY updated_at DESC
                        LIMIT 1
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    
                    if row:
                        access_token = row['access_token'] if isinstance(row, dict) else row[0]
                        refresh_token = row['refresh_token'] if isinstance(row, dict) else row[1]
                        expires_at = row['expires_at'] if isinstance(row, dict) else row[2]
                        metadata_json = row['metadata'] if isinstance(row, dict) else row[3]
                        created_at = row['created_at'] if isinstance(row, dict) else row[4]
                        
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        
                        return {
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'expires_at': expires_at,
                            'microsoft_id': metadata.get('microsoft_id'),
                            'microsoft_email': metadata.get('microsoft_email'),
                            'display_name': metadata.get('display_name'),
                            'created_at': created_at
                        }
                    
                    return None
                    
        except Exception as e:
            print(f"❌ Failed to get Microsoft tokens: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        try:
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT id, username, email, role, primary_gmail, created_at
                        FROM ai_infrastructure.users
                        WHERE email = %s
                    ''', (email,))
                    
                    row = cursor.fetchone()
                    
                    if row:
                        return {
                            'id': row['id'] if isinstance(row, dict) else row[0],
                            'username': row['username'] if isinstance(row, dict) else row[1],
                            'email': row['email'] if isinstance(row, dict) else row[2],
                            'role': row['role'] if isinstance(row, dict) else row[3],
                            'primary_gmail': row['primary_gmail'] if isinstance(row, dict) else row[4],
                            'created_at': row['created_at'] if isinstance(row, dict) else row[5]
                        }
                    
                    return None
                    
        except Exception as e:
            print(f"❌ Failed to get user by email: {e}")
            return None
    
    def register(self, username: str, email: str, password: Optional[str] = None, 
                primary_gmail: str = None, role: str = 'user', auth_provider: str = 'local',
                microsoft_id: str = None, full_name: str = None) -> Dict:
        """Register new user (supports local and OAuth registration)"""
        try:
            if password:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            else:
                password_hash = bcrypt.hashpw(os.urandom(32), bcrypt.gensalt()).decode('utf-8')
            
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    metadata = {
                        'auth_provider': auth_provider,
                        'full_name': full_name
                    }
                    
                    if microsoft_id:
                        metadata['microsoft_id'] = microsoft_id
                    
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.users (username, email, password_hash, primary_gmail, role, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (username, email, password_hash, primary_gmail or email, role, json.dumps(metadata)))
                    
                    user_id = cursor.lastrowid
                    
                    cursor.execute('''
                        INSERT INTO workspaces (user_id, name, description, metadata)
                        VALUES (%s, %s, %s, %s)
                    ''', (user_id, f"{username}'s Workspace", "Default workspace", json.dumps({})))
                    
                    workspace_id = cursor.lastrowid
                
                conn.commit()
                
                print(f"✅ User registered: {username} (ID: {user_id}, Provider: {auth_provider})")
                
                return {
                    'success': True,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'role': role,
                        'workspace_id': workspace_id
                    }
                }
                
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return {
                'success': False,
                'error': 'Username or email already exists' if 'UNIQUE' in str(e) else str(e)
            }
    
    def parse_user_agent(self, user_agent: str) -> dict:
        """
        Parse user agent string to extract device info
        
        Args:
            user_agent: User agent string from request headers
        
        Returns:
            dict: {browser, browser_version, os, os_version, device_type}
        """
        if not user_agent:
            return {}
        
        ua_lower = user_agent.lower()
        device_info = {}
        
        # Detect browser
        if 'edg/' in ua_lower or 'edge/' in ua_lower:
            device_info['browser'] = 'Edge'
            if 'edg/' in ua_lower:
                device_info['browser_version'] = user_agent.split('Edg/')[1].split()[0] if 'Edg/' in user_agent else ''
        elif 'chrome/' in ua_lower and 'safari/' in ua_lower and 'edg/' not in ua_lower:
            device_info['browser'] = 'Chrome'
            device_info['browser_version'] = user_agent.split('Chrome/')[1].split()[0] if 'Chrome/' in user_agent else ''
        elif 'firefox/' in ua_lower:
            device_info['browser'] = 'Firefox'
            device_info['browser_version'] = user_agent.split('Firefox/')[1].split()[0] if 'Firefox/' in user_agent else ''
        elif 'safari/' in ua_lower and 'chrome/' not in ua_lower:
            device_info['browser'] = 'Safari'
            device_info['browser_version'] = user_agent.split('Version/')[1].split()[0] if 'Version/' in user_agent else ''
        else:
            device_info['browser'] = 'Unknown'
            device_info['browser_version'] = ''
        
        # Detect OS
        if 'windows nt 10.0' in ua_lower:
            device_info['os'] = 'Windows'
            device_info['os_version'] = '11' if 'windows nt 10.0' in ua_lower else '10'
        elif 'windows nt' in ua_lower:
            device_info['os'] = 'Windows'
            device_info['os_version'] = user_agent.split('Windows NT ')[1].split(';')[0] if 'Windows NT' in user_agent else ''
        elif 'mac os x' in ua_lower or 'macos' in ua_lower:
            device_info['os'] = 'MacOS'
            device_info['os_version'] = user_agent.split('Mac OS X ')[1].split(')')[0].replace('_', '.') if 'Mac OS X' in user_agent else ''
        elif 'linux' in ua_lower:
            device_info['os'] = 'Linux'
            device_info['os_version'] = ''
        elif 'android' in ua_lower:
            device_info['os'] = 'Android'
            device_info['os_version'] = user_agent.split('Android ')[1].split(';')[0] if 'Android ' in user_agent else ''
        elif 'iphone' in ua_lower or 'ipad' in ua_lower:
            device_info['os'] = 'iOS'
            device_info['os_version'] = user_agent.split('OS ')[1].split()[0].replace('_', '.') if ' OS ' in user_agent else ''
        else:
            device_info['os'] = 'Unknown'
            device_info['os_version'] = ''
        
        # Detect device type
        if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
            device_info['device_type'] = 'mobile'
        elif 'tablet' in ua_lower or 'ipad' in ua_lower:
            device_info['device_type'] = 'tablet'
        else:
            device_info['device_type'] = 'desktop'
        
        return device_info
    
    def create_session(self, user_id: int) -> str:
        """Create JWT session for user"""
        try:
            # First query - get user data
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('SELECT username, email, role FROM ai_infrastructure.users WHERE id = %s', (user_id,))
                    row = cursor.fetchone()
                    
                    if not row:
                        raise Exception(f"User {user_id} not found")
                    
                    username = row['username'] if isinstance(row, dict) else row[0]
                    email = row['email'] if isinstance(row, dict) else row[1]
                    role = row['role'] if isinstance(row, dict) else row[2]
            
            expiry = datetime.utcnow() + timedelta(hours=24)
            exp_timestamp = int(expiry.timestamp()) if isinstance(expiry, datetime) else expiry
            
            payload = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'exp': exp_timestamp
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            # Capture device info from Flask request context (if available)
            device_info = {}
            ip_address = None
            user_agent = None
            
            try:
                from flask import request
                if request:
                    forwarded_for = request.headers.get('X-Forwarded-For', '')
                    ip_address = forwarded_for.split(',')[0].strip() or request.remote_addr
                    user_agent = request.headers.get('User-Agent', '')
                    device_info = self.parse_user_agent(user_agent)
            except (ImportError, RuntimeError):
                pass
            
            # Second query - store session
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        INSERT INTO ai_infrastructure.user_sessions 
                        (user_id, token, expires_at, ip_address, user_agent, device_info)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (user_id, token, expiry.isoformat(), ip_address, user_agent, 
                          json.dumps(device_info) if device_info else '{}'))
                
                conn.commit()
            
            print(f"✅ Created session for user {user_id} from {device_info.get('browser', 'Unknown')} on {device_info.get('os', 'Unknown')}")
            return token
            
        except Exception as e:
            print(f"❌ Session creation failed: {e}")
            raise
    
    def verify_session(self, token: str) -> Optional[Dict]:
        """Verify JWT session token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            with get_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT user_id FROM ai_infrastructure.user_sessions
                        WHERE token = %s AND expires_at > CURRENT_TIMESTAMP
                    ''', (token,))
                    
                    result = cursor.fetchone()
                    
                    if not result:
                        return None
            
            return {
                'id': payload['user_id'],
                'username': payload['username'],
                'email': payload['email'],
                'role': payload['role']
            }
            
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return None
        except jwt.InvalidTokenError:
            print("❌ Invalid token")
            return None
        except Exception as e:
            print(f"❌ Session verification failed: {e}")
            return None


# Flask decorator for protected routes
def require_auth(f):
    """Decorator to require authentication for routes (handles CORS preflight)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("\n" + "="*60)
        print(f"🔧 STAGE 3: API REQUEST AUTHENTICATION")
        print("="*60)
        print(f"   Endpoint: {request.method} {request.path}")
        print(f"   Remote IP: {request.remote_addr}")
        
        # Allow OPTIONS requests for CORS preflight
        if request.method == 'OPTIONS':
            print("   ℹ️ OPTIONS request (CORS preflight) - allowing")
            response = jsonify({'status': 'ok'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response, 200
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        request_data = request.get_json(silent=True) or {}
        source = request_data.get('source', 'ui')
        
        print(f"\n📊 STAGE 3.1: Authorization Header Check")
        print(f"   Source: {source}")
        print(f"   Auth header present: {auth_header is not None}")
        if auth_header:
            print(f"   Auth header starts with 'Bearer ': {auth_header.startswith('Bearer ')}")
        
        # Require token for ALL requests
        if not auth_header or not auth_header.startswith('Bearer '):
            print(f"   ❌ No valid authorization header")
            print("\n❌ STAGE 3 FAILED: Missing authorization token")
            print("="*60 + "\n")
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        print(f"   ✅ Token extracted from header")
        print(f"   Token length: {len(token)}")
        print(f"   First 20 chars: {token[:20]}...")
        
        # Verify token
        print(f"\n📊 STAGE 3.2: Calling Token Verification")
        auth_manager = UserAuthManager()
        user_data = auth_manager.verify_token(token)
        
        if not user_data:
            print(f"\n❌ STAGE 3 FAILED: Token verification failed")
            print("="*60 + "\n")
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user data to request context
        request.user = user_data
        g.user_id = user_data.get('user_id')  # ← CRITICAL: Tools use g.user_id for credential resolution
        
        print(f"\n✅ STAGE 3 COMPLETE: Authentication successful")
        print(f"   User: {user_data.get('username')}")
        print(f"   ID: {user_data.get('user_id')}")
        print(f"   Email: {user_data.get('email')}")
        print("="*60 + "\n")
        
        return f(*args, **kwargs)
    
    return decorated_function


# Global instance
user_auth_manager = UserAuthManager()