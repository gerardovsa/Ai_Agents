"""
FILE: AI_infrastructure/auth/user_auth.py
PURPOSE: User authentication, profile management, and JWT token handling for multi-tenant system

DEPENDENCIES:
- sqlite3 (built-in) - Database access for user data
- bcrypt - Password hashing and verification
- jwt (PyJWT) - JSON Web Token generation and validation
- dotenv - Load credentials from .env.master file
- flask - Request/response handling and decorators

EXPORTS:
- UserAuthManager class:
  * register_user(email, password, name) -> dict - Create new user account
  * authenticate_user(email, password) -> dict - Verify credentials and generate JWT
  * verify_jwt_token(token: str) -> dict - Validate and decode JWT token
  * get_user_profile(user_id: int) -> dict - Retrieve user information
  * update_user_profile(user_id: int, **kwargs) -> bool - Update user settings
  * get_all_users() -> list - Admin function to list all users
  * require_auth(f) - Flask decorator for protected routes

USED BY:
- AI_infrastructure/routes/auth_routes.py - Authentication endpoints
- AI_infrastructure/routes/agent_routes_v4.py - Protected agent endpoints
- AI_infrastructure/core/agent_worker.py - User identification for tool execution
- AI_infrastructure/auth/credential_injector.py - User credential retrieval

RELATED FILES:
- AI_infrastructure/auth/credential_injector.py - Injects user OAuth tokens into tools
- data/ai_infrastructure.db - User database (users, oauth_tokens tables)
- .env.master - JWT secret key and database configuration

NOTES:
- SECURITY: Loads JWT_SECRET from .env.master file (3 levels up from this file)
- SECURITY: Passwords hashed with bcrypt (cost factor 12)
- SECURITY: JWT tokens expire after 24 hours by default
- DATABASE: Uses data/ai_infrastructure.db (users table)
- ISOLATION: Multi-tenant system - each user has isolated workspace
- OAUTH: User OAuth tokens stored in oauth_tokens table (platform, access_token, refresh_token)
- DECORATOR: @require_auth adds user_id to Flask request context

LAST MODIFIED: 2025-11-02 - Added oauth_tokens table support for credential injection
"""

import os
import sqlite3
from pathlib import Path
from dotenv import dotenv_values

# Setup logging
from utils.logger_config import setup_logger, log_db
logger = setup_logger('auth.user_auth')

# Load credentials from .env.master (in root folder, 3 levels up)
_ENV_MASTER_PATH = Path(__file__).parent.parent.parent / '.env.master'
_config = dotenv_values(_ENV_MASTER_PATH)
import json
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from flask import request, jsonify
from functools import wraps


class UserAuthManager:
    """Manages user authentication, profiles, and workspace isolation"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        self.db_path = str(db_path)
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        self._init_tables()
    
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
        
        print(f"📧 Loaded {len(accounts)} Gmail accounts from .env:")
        for acc in accounts:
            print(f"   - {acc['email']} ({acc['display_name']})")
        
        return accounts
    
    def _init_tables(self):
        """Initialize user authentication tables with retry logic for multi-worker startup"""
        import time
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                    cursor = conn.cursor()
                    
                    # Enhanced users table
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
                            metadata TEXT
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
                    
                    # NEW: Platform credentials table (stores API keys/tokens per user per platform)
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS user_platform_credentials (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            platform TEXT NOT NULL,
                            credential_type TEXT NOT NULL,
                            credential_key TEXT NOT NULL,
                            credential_value TEXT NOT NULL,
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
                    
                    conn.commit()
                    log_db(logger, "User authentication tables initialized")
                    break  # Success - exit retry loop
                    
            except sqlite3.OperationalError as e:
                if ("database is locked" in str(e) or "disk I/O error" in str(e)) and attempt < max_retries - 1:
                    # Another worker is initializing - wait and retry
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    print(f"⚠ [DB] Table creation retry {attempt + 1}/{max_retries}: {e}")
                    continue
                else:
                    # Either not a recoverable error, or we've exhausted retries
                    print(f"❌ [DB] Failed to initialize tables after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                # Catch any other unexpected errors
                print(f"❌ [DB] Unexpected error during table initialization: {e}")
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
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create user
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, primary_gmail, role, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, primary_gmail or email, role, json.dumps({})))
                
                user_id = cursor.lastrowid
                
                # Create default workspace
                cursor.execute('''
                    INSERT INTO workspaces (user_id, name, description, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, f"{username}'s Workspace", "Default workspace", json.dumps({})))
                
                workspace_id = cursor.lastrowid
                
                # AUTO-LINK ALL .ENV GMAIL ACCOUNTS FOR MASTER/ADMIN USERS
                if role == 'admin':
                    gmail_accounts = self._load_env_gmail_accounts()
                    for gmail_data in gmail_accounts:
                        cursor.execute('''
                            INSERT INTO user_gmail_accounts 
                            (user_id, gmail_address, display_name, is_primary)
                            VALUES (?, ?, ?, ?)
                        ''', (user_id, gmail_data['email'], gmail_data['display_name'], gmail_data['is_primary']))
                    
                    print(f"Auto-linked {len(gmail_accounts)} Gmail accounts from .env.master")
                
                conn.commit()
                
                print(f"User registered: {username} (ID: {user_id}, Role: {role}, Workspace: {workspace_id})")
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'workspace_id': workspace_id,
                    'username': username,
                    'email': email,
                    'role': role
                }
                
        except sqlite3.IntegrityError as e:
            print(f" Registration failed: {e}")
            return {
                'success': False,
                'error': 'Username or email already exists'
            }
        except Exception as e:
            print(f" Registration error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_jwt(self, user_data: Dict) -> str:
        """
        Generate JWT token for a user (used for OAuth and dev mode)
        
        Args:
            user_data: Dict with user info (id, username, email, role)
        
        Returns:
            JWT token string
        """
        token_payload = {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'role': user_data.get('role', 'user'),
            'exp': int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        
        token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
        
        # Store session in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_sessions (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_data.get('id'), token, token_payload['exp']))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not store session: {e}")
        
        return token
    
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find user by username or email
                cursor.execute('''
                    SELECT id, username, email, password_hash, role, primary_gmail
                    FROM users
                    WHERE username = ? OR email = ?
                ''', (username, username))
                
                row = cursor.fetchone()
                
                if not row:
                    return {'success': False, 'error': 'Invalid credentials'}
                
                user_id, username, email, password_hash, role, primary_gmail = row
                
                # Verify password
                if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    return {'success': False, 'error': 'Invalid credentials'}
                
                # Get user's workspaces
                cursor.execute('''
                    SELECT id, name FROM workspaces WHERE user_id = ?
                ''', (user_id,))
                workspaces = [{'id': w[0], 'name': w[1]} for w in cursor.fetchall()]
                
                # Get linked Gmail accounts
                cursor.execute('''
                    SELECT gmail_address, display_name, is_primary
                    FROM user_gmail_accounts
                    WHERE user_id = ?
                ''', (user_id,))
                gmail_accounts = [
                    {
                        'email': g[0],
                        'display_name': g[1] or g[0],
                        'is_primary': bool(g[2])
                    }
                    for g in cursor.fetchall()
                ]
                
                # Generate JWT token
                exp_time = datetime.utcnow() + timedelta(days=30)  # 30-day expiry (1 month)
                exp_timestamp = int(exp_time.timestamp())
                
                token_payload = {
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'exp': exp_timestamp
                }
                
                token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
                
                # Store session
                cursor.execute('''
                    INSERT INTO user_sessions (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_id, token, exp_time.strftime('%Y-%m-%d %H:%M:%S')))
                
                # Update last active
                cursor.execute('''
                    UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user_id,))
                
                conn.commit()
                
                print(f"User logged in: {username}")
                
                return {
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'role': role,
                        'primary_gmail': primary_gmail,
                        'workspaces': workspaces,
                        'gmail_accounts': gmail_accounts
                    }
                }
                
        except Exception as e:
            print(f" Login error: {e}")
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
        print(f"   Database: {self.db_path}")
        
        # DEVELOPMENT MODE: Accept dev-mode token ONLY in development (localhost)
        # SECURITY: This bypass is DISABLED in production (Render.com)
        import os
        is_development = os.getenv('FLASK_ENV') == 'development' or os.getenv('DEBUG', 'False').lower() == 'true'
        
        if token == 'dev-mode-token-12345' and is_development:
            print(f"\n🔧 [DEV MODE] Dev token detected - bypassing authentication")
            print(f"   Environment: DEVELOPMENT (bypass allowed)")
            print(f"   Returning default test user (id=1)")
            print("\nSTAGE 2 COMPLETE (DEV MODE): Dev user authenticated")
            print("="*60 + "\n")
            return {
                'user_id': 1,
                'email': 'printing@inhouseprint.com.au',
                'username': 'printing@inhouseprint.com.au',
                'auth_platform': 'local_dev'
            }
        elif token == 'dev-mode-token-12345' and not is_development:
            print(f"\n⚠️ [SECURITY] Dev token rejected in production environment")
            print("="*60 + "\n")
            return None
        
        try:
            print(f"\n📊 STAGE 2.1: JWT Signature Validation")
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            print(f"   JWT signature valid")
            print(f"   User ID: {payload.get('user_id')}")
            print(f"   Email: {payload.get('email')}")
            print(f"   Username: {payload.get('username')}")
            
            print(f"\n📊 STAGE 2.2: Database Token Lookup")
            # Check if token exists in sessions and hasn't expired
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check total sessions in database
                cursor.execute('SELECT COUNT(*) FROM user_sessions')
                total_sessions = cursor.fetchone()[0]
                print(f"   Total sessions in DB: {total_sessions}")
                
                cursor.execute('''
                    SELECT user_id, expires_at FROM user_sessions
                    WHERE token = ?
                ''', (token,))
                
                result = cursor.fetchone()
                if not result:
                    print(f"    Token NOT found in database")
                    print(f"   Checking sessions for user_id={payload.get('user_id')}...")
                    cursor.execute('SELECT COUNT(*) FROM user_sessions WHERE user_id = ?', (payload.get('user_id'),))
                    user_sessions = cursor.fetchone()[0]
                    print(f"   User has {user_sessions} session(s) in DB")
                    print("\n STAGE 2 FAILED: Token not in database")
                    print("="*60 + "\n")
                    return None
                
                print(f"   Token found in database")
                user_id, expires_at = result
                print(f"   User ID from DB: {user_id}")
                print(f"   Expires at: {expires_at}")
                
                print(f"\n📊 STAGE 2.3: Expiry Check")
                # Check expiry manually
                cursor.execute("SELECT datetime('now')")
                current_time = cursor.fetchone()[0]
                print(f"   Current time: {current_time}")
                print(f"   Token expires: {expires_at}")
                
                if expires_at <= current_time:
                    print(f"    Token EXPIRED: {expires_at} <= {current_time}")
                    print("\n STAGE 2 FAILED: Token expired")
                    print("="*60 + "\n")
                    return None
                
                print(f"   Token is valid (not expired)")
            
            print(f"\nSTAGE 2 COMPLETE: Token verified successfully")
            print("="*60 + "\n")
            return payload
            
        except jwt.ExpiredSignatureError:
            print(f"\n STAGE 2 FAILED: Token expired (JWT signature)")
            print("="*60 + "\n")
            return None
        except jwt.InvalidTokenError as e:
            print(f"\n STAGE 2 FAILED: Invalid token (JWT): {e}")
            print("="*60 + "\n")
            return None
        except Exception as e:
            print(f"\n STAGE 2 FAILED: Token verification error: {e}")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")
            return None
    
    def link_gmail_account(self, user_id: int, gmail_address: str, display_name: str = None,
                          access_token: str = None, refresh_token: str = None,
                          is_primary: bool = False) -> Dict:
        """
        Link Gmail account to user profile
        
        Args:
            user_id: User ID
            gmail_address: Gmail address
            display_name: Display name (e.g., "MiniVet Marketing")
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            is_primary: Set as primary account
        
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # If setting as primary, unset other primary accounts
                if is_primary:
                    cursor.execute('''
                        UPDATE user_gmail_accounts
                        SET is_primary = 0
                        WHERE user_id = ?
                    ''', (user_id,))
                
                # Insert or update Gmail account
                cursor.execute('''
                    INSERT INTO user_gmail_accounts 
                    (user_id, gmail_address, display_name, access_token, refresh_token, is_primary)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, gmail_address) DO UPDATE SET
                        display_name = excluded.display_name,
                        access_token = excluded.access_token,
                        refresh_token = excluded.refresh_token,
                        is_primary = excluded.is_primary
                ''', (user_id, gmail_address, display_name, access_token, refresh_token, is_primary))
                
                conn.commit()
                
                print(f"Gmail linked: {gmail_address} → User {user_id}")
                
                return {'success': True, 'gmail': gmail_address}
                
        except Exception as e:
            print(f" Gmail link error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_gmail_accounts(self, user_id: int) -> List[Dict]:
        """Get all Gmail accounts linked to user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT gmail_address, display_name, is_primary, created_at
                FROM user_gmail_accounts
                WHERE user_id = ?
                ORDER BY is_primary DESC, created_at ASC
            ''', (user_id,))
            
            return [
                {
                    'email': row[0],
                    'display_name': row[1] or row[0],
                    'is_primary': bool(row[2]),
                    'created_at': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def get_user_workspace(self, user_id: int) -> Optional[int]:
        """Get user's default workspace ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM workspaces WHERE user_id = ? LIMIT 1
            ''', (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    # ==================== PLATFORM CREDENTIALS MANAGEMENT ====================
    
    def store_platform_credential(self, user_id: int, platform: str, 
                                  credential_type: str, credential_key: str, 
                                  credential_value: str, metadata: Dict = None) -> Dict:
        """
        Store platform API key/token for user
        
        Args:
            user_id: User ID
            platform: Platform name (gmail, slack, woocommerce, etc.)
            credential_type: Type (api_key, oauth_token, app_password, etc.)
            credential_key: Credential identifier (API_KEY, ACCESS_TOKEN, etc.)
            credential_value: The actual credential value
            metadata: Additional metadata (JSON)
        
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                # ⚠️ DEPRECATED: user_platform_credentials table is deprecated
                # Use oauth_tokens table instead
                print("⚠️ WARNING: store_platform_credential() uses deprecated table")
                print("   Use oauth_tokens table instead (via OAuth routes)")
                
                # Upsert (insert or update) - STILL USING OLD TABLE FOR BACKWARD COMPATIBILITY
                # TODO: Migrate all callers to use oauth_tokens directly
                cursor.execute('''
                    INSERT INTO user_platform_credentials 
                    (user_id, platform, credential_type, credential_key, credential_value, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, platform, credential_key) 
                    DO UPDATE SET 
                        credential_value = excluded.credential_value,
                        credential_type = excluded.credential_type,
                        metadata = excluded.metadata,
                        updated_at = CURRENT_TIMESTAMP
                ''', (user_id, platform, credential_type, credential_key, credential_value, metadata_json))
                
                conn.commit()
                
                print(f"Stored {platform} credential for user {user_id}: {credential_key}")
                
                return {'success': True}
                
        except Exception as e:
            print(f" Store credential error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_platform_credentials(self, user_id: int, platform: str) -> Dict[str, str]:
        """
        Get all credentials for a platform for this user
        
        Args:
            user_id: User ID
            platform: Platform name
        
        Returns:
            Dict of credential_key -> credential_value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try oauth_tokens table first (NEW schema)
            cursor.execute('''
                SELECT 'access_token' as credential_key, access_token as credential_value
                FROM oauth_tokens
                WHERE user_id = ? AND platform = ? AND is_active = 1
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (user_id, platform))
            
            oauth_tokens = {row[0]: row[1] for row in cursor.fetchall()}
            
            if oauth_tokens:
                return oauth_tokens
            
            # Fallback to old table (DEPRECATED)
            cursor.execute('''
                SELECT credential_key, credential_value
                FROM user_platform_credentials
                WHERE user_id = ? AND platform = ? AND is_active = 1
            ''', (user_id, platform))
            
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def get_user_credential(self, user_id: int, platform: str, credential_key: str) -> Optional[str]:
        """
        Get specific credential for user
        
        Args:
            user_id: User ID
            platform: Platform name
            credential_key: Credential key
        
        Returns:
            Credential value or None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try oauth_tokens table first (NEW schema)
            if credential_key == 'access_token':
                cursor.execute('''
                    SELECT access_token
                    FROM oauth_tokens
                    WHERE user_id = ? AND platform = ? AND is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT 1
                ''', (user_id, platform))
                
                row = cursor.fetchone()
                if row:
                    return row[0]
            
            # Fallback to old table (DEPRECATED)
            cursor.execute('''
                SELECT credential_value
                FROM user_platform_credentials
                WHERE user_id = ? AND platform = ? AND credential_key = ? AND is_active = 1
            ''', (user_id, platform, credential_key))
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    def list_user_platforms(self, user_id: int) -> List[str]:
        """
        List all platforms user has credentials for
        
        Returns:
            List of platform names
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get platforms from oauth_tokens table (NEW schema)
            cursor.execute('''
                SELECT DISTINCT platform
                FROM oauth_tokens
                WHERE user_id = ? AND is_active = 1
                
                UNION
                
                SELECT DISTINCT platform
                FROM user_platform_credentials
                WHERE user_id = ? AND is_active = 1
                
                ORDER BY platform
            ''', (user_id, user_id))
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_user_google_oauth_credentials(self, user_id: int) -> Optional[Dict]:
        """
        Get Google OAuth credentials for user from oauth_tokens table
        
        Returns dict with:
        - access_token: Current access token
        - refresh_token: Refresh token (if available)
        - token_uri: Google token endpoint
        - client_id: OAuth client ID
        - client_secret: OAuth client secret
        - scopes: List of authorized scopes
        - expires_at: Token expiry timestamp
        
        Returns None if user doesn't have Google OAuth credentials
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get OAuth tokens from oauth_tokens table (NEW V2_FIXED schema)
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
                    FROM oauth_tokens
                    WHERE user_id = ? AND platform = 'google'
                    AND is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT 1
                ''', (user_id,))
                
                token_row = cursor.fetchone()
                if not token_row:
                    print(f"⚠️ No Google OAuth credentials found for user {user_id} in oauth_tokens table")
                    return None
                
                access_token = token_row['access_token']
                refresh_token = token_row['refresh_token']
                expires_at = token_row['expires_at']
                scope = token_row['scope'] or token_row['granted_scopes'] or ''
                metadata = json.loads(token_row['metadata']) if token_row['metadata'] else {}
                
                # Get OAuth config from .env.master
                client_id = _config.get('GOOGLE_OAUTH_CLIENT_ID') or _config.get('GOOGLE_CLIENT_ID')
                client_secret = _config.get('GOOGLE_OAUTH_CLIENT_SECRET') or _config.get('GOOGLE_CLIENT_SECRET')
                
                if not client_id or not client_secret:
                    print("❌ Google OAuth config not found in environment (.env.master)")
                    return None
                
                # Parse scopes from space-separated string
                if scope:
                    scopes = scope.split(' ') if isinstance(scope, str) else scope
                else:
                    # Default scopes if none stored
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
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'scopes': scopes,
                    'expires_at': expires_at,
                    'user_id': user_id,
                    'metadata': metadata
                }
                
                print(f"✅ Retrieved Google OAuth credentials for user {user_id} from oauth_tokens table")
                return credentials
                
        except Exception as e:
            print(f"❌ Error retrieving Google OAuth credentials: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_microsoft_oauth_credentials(self, user_id: int) -> Optional[Dict]:
        """
        Get Microsoft 365 OAuth credentials for user from oauth_tokens table
        
        Returns dict with:
        - access_token: Current access token
        - refresh_token: Refresh token (if available)
        - token_uri: Microsoft token endpoint
        - client_id: OAuth client ID
        - client_secret: OAuth client secret
        - scopes: List of authorized scopes
        - expires_at: Token expiry timestamp
        
        Returns None if user doesn't have Microsoft OAuth credentials
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get OAuth tokens from oauth_tokens table
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
                    FROM oauth_tokens
                    WHERE user_id = ? AND platform = 'microsoft'
                    AND is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT 1
                ''', (user_id,))
                
                token_row = cursor.fetchone()
                if not token_row:
                    print(f"⚠️ No Microsoft OAuth credentials found for user {user_id} in oauth_tokens table")
                    return None
                
                access_token = token_row['access_token']
                refresh_token = token_row['refresh_token']
                expires_at = token_row['expires_at']
                scope = token_row['scope'] or token_row['granted_scopes'] or ''
                metadata = json.loads(token_row['metadata']) if token_row['metadata'] else {}
                
                # Get OAuth config from .env.master
                client_id = _config.get('MICROSOFT_CLIENT_ID')
                client_secret = _config.get('MICROSOFT_CLIENT_SECRET')
                tenant_id = _config.get('MICROSOFT_TENANT_ID', 'common')
                
                if not client_id or not client_secret:
                    print("❌ Microsoft OAuth config not found in environment (.env.master)")
                    return None
                
                # Parse scopes from space-separated string
                if scope:
                    scopes = scope.split(' ') if isinstance(scope, str) else scope
                else:
                    # Default scopes if none stored
                    scopes = [
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
                
                print(f"✅ Retrieved Microsoft OAuth credentials for user {user_id} from oauth_tokens table")
                return credentials
                
        except Exception as e:
            print(f"❌ Error retrieving Microsoft OAuth credentials: {e}")
            import traceback
            traceback.print_exc()
            return None


# Flask decorator for protected routes
def require_auth(f):
    """Decorator to require authentication for routes (handles CORS preflight + CLI bypass)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("\n" + "="*60)
        print(f"🔧 STAGE 3: API REQUEST AUTHENTICATION")
        print("="*60)
        print(f"   Endpoint: {request.method} {request.path}")
        print(f"   Remote IP: {request.remote_addr}")
        
        # Allow OPTIONS requests for CORS preflight
        if request.method == 'OPTIONS':
            print("   ℹ️  OPTIONS request (CORS preflight) - allowing")
            response = jsonify({'status': 'ok'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response, 200
        
        # Get token from Authorization header (for both UI and CLI requests)
        auth_header = request.headers.get('Authorization')
        request_data = request.get_json(silent=True) or {}
        source = request_data.get('source', 'ui')
        
        print(f"\n📊 STAGE 3.1: Authorization Header Check")
        print(f"   Source: {source}")
        print(f"   Auth header present: {auth_header is not None}")
        if auth_header:
            print(f"   Auth header starts with 'Bearer ': {auth_header.startswith('Bearer ')}")
        
        # Require token for ALL requests (no bypass for CLI)
        if not auth_header or not auth_header.startswith('Bearer '):
            print(f"    No valid authorization header")
            print("\n STAGE 3 FAILED: Missing authorization token")
            print("="*60 + "\n")
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        print(f"   Token extracted from header")
        print(f"   Token length: {len(token)}")
        print(f"   First 20 chars: {token[:20]}...")
        
        # Verify token
        print(f"\n📊 STAGE 3.2: Calling Token Verification")
        auth_manager = UserAuthManager()
        user_data = auth_manager.verify_token(token)
        
        if not user_data:
            print(f"\n STAGE 3 FAILED: Token verification failed")
            print("="*60 + "\n")
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user data to request context
        request.user = user_data
        
        # Log authenticated user
        print(f"\nSTAGE 3 COMPLETE: Authentication successful")
        print(f"   User: {user_data.get('username')}")
        print(f"   ID: {user_data.get('user_id')}")
        print(f"   Email: {user_data.get('email')}")
        print("="*60 + "\n")
        
        return f(*args, **kwargs)
    
    return decorated_function


    # ==================== MICROSOFT 365 OAUTH SUPPORT ====================
    
    def store_microsoft_tokens(self, user_id: int, access_token: str, refresh_token: str, 
                               expires_at: str, microsoft_id: str = None, microsoft_email: str = None):
        """
        Store Microsoft OAuth tokens for a user
        
        Args:
            user_id: User ID
            access_token: Microsoft access token
            refresh_token: Microsoft refresh token
            expires_at: Token expiration timestamp (ISO format)
            microsoft_id: Microsoft user ID
            microsoft_email: Microsoft email address
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Store or update Microsoft tokens in oauth_tokens table (NEW schema)
                cursor.execute('''
                    INSERT INTO oauth_tokens
                    (user_id, platform, access_token, refresh_token, expires_at, 
                     metadata, account_identifier, account_name, is_active, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id, platform) DO UPDATE SET
                        access_token = excluded.access_token,
                        refresh_token = excluded.refresh_token,
                        expires_at = excluded.expires_at,
                        metadata = excluded.metadata,
                        account_identifier = excluded.account_identifier,
                        account_name = excluded.account_name,
                        updated_at = CURRENT_TIMESTAMP
                ''', (
                    user_id,
                    'microsoft',  # Platform name: 'microsoft' (not 'microsoft365')
                    access_token,
                    refresh_token,
                    expires_at,
                    json.dumps({
                        'microsoft_id': microsoft_id,
                        'microsoft_email': microsoft_email
                    }),
                    microsoft_email,  # account_identifier
                    microsoft_email   # account_name
                ))
                
                conn.commit()
                print(f"Stored Microsoft tokens for user {user_id}")
                
        except Exception as e:
            print(f" Failed to store Microsoft tokens: {e}")
    
    def get_microsoft_tokens(self, user_id: int) -> Optional[Dict]:
        """
        Get Microsoft OAuth tokens for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with Microsoft tokens or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Query oauth_tokens table (NEW schema)
                cursor.execute('''
                    SELECT access_token, refresh_token, expires_at, metadata, created_at
                    FROM oauth_tokens
                    WHERE user_id = ? AND platform = 'microsoft'
                    AND is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT 1
                ''', (user_id,))
                
                row = cursor.fetchone()
                
                if row:
                    access_token = row[0]
                    refresh_token = row[1]
                    expires_at = row[2]
                    metadata_json = row[3]
                    created_at = row[4]
                    
                    # Parse metadata
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'expires_at': expires_at,
                        'refresh_token': metadata.get('refresh_token'),
                        'expires_at': metadata.get('expires_at'),
                        'microsoft_id': metadata.get('microsoft_id'),
                        'microsoft_email': metadata.get('microsoft_email'),
                        'display_name': metadata.get('display_name'),  # ADDED
                        'created_at': created_at
                    }
                
                return None
                
        except Exception as e:
            print(f" Failed to get Microsoft tokens: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email address
        
        Args:
            email: User email
        
        Returns:
            User dict or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, role, primary_gmail, created_at
                    FROM users
                    WHERE email = ?
                ''', (email,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'role': row[3],
                        'primary_gmail': row[4],
                        'created_at': row[5]
                    }
                
                return None
                
        except Exception as e:
            print(f" Failed to get user by email: {e}")
            return None
    
    def register(self, username: str, email: str, password: Optional[str] = None, 
                primary_gmail: str = None, role: str = 'user', auth_provider: str = 'local',
                microsoft_id: str = None, full_name: str = None) -> Dict:
        """
        Register new user (supports local and OAuth registration)
        
        Args:
            username: Unique username
            email: User email
            password: Plain text password (None for OAuth)
            primary_gmail: Optional primary Gmail
            role: 'admin' or 'user'
            auth_provider: 'local', 'google', or 'microsoft'
            microsoft_id: Microsoft user ID (for Microsoft login)
            full_name: Full name from OAuth provider
        
        Returns:
            Dict with user info and success status
        """
        try:
            # Hash password or use placeholder for OAuth
            if password:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            else:
                # OAuth users don't have password - use secure random placeholder
                password_hash = bcrypt.hashpw(os.urandom(32), bcrypt.gensalt()).decode('utf-8')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create user with metadata
                metadata = {
                    'auth_provider': auth_provider,
                    'full_name': full_name
                }
                
                if microsoft_id:
                    metadata['microsoft_id'] = microsoft_id
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, primary_gmail, role, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, primary_gmail or email, role, json.dumps(metadata)))
                
                user_id = cursor.lastrowid
                
                # Create default workspace
                cursor.execute('''
                    INSERT INTO workspaces (user_id, name, description, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, f"{username}'s Workspace", "Default workspace", json.dumps({})))
                
                workspace_id = cursor.lastrowid
                
                conn.commit()
                
                print(f"User registered: {username} (ID: {user_id}, Provider: {auth_provider})")
                
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
                
        except sqlite3.IntegrityError as e:
            print(f" Registration failed: {e}")
            return {
                'success': False,
                'error': 'Username or email already exists'
            }
        except Exception as e:
            print(f" Registration error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_session(self, user_id: int) -> str:
        """
        Create JWT session for user
        
        Args:
            user_id: User ID
        
        Returns:
            JWT token string
        """
        # Get user info
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, email, role FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            
            if not row:
                raise Exception(f"User {user_id} not found")
            
            username, email, role = row
        
        # Create JWT token
        expiry = datetime.utcnow() + timedelta(hours=24)
        
        # Convert expiry to Unix timestamp for JWT
        exp_timestamp = int(expiry.timestamp()) if isinstance(expiry, datetime) else expiry
        
        payload = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'role': role,
            'exp': exp_timestamp
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # Store session
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, token, expiry.isoformat()))
            conn.commit()
        
        print(f"Created session for user {user_id}")
        return token
    
    def verify_session(self, token: str) -> Optional[Dict]:
        """
        Verify JWT session token
        
        Args:
            token: JWT token
        
        Returns:
            User dict or None
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check session exists in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id FROM user_sessions
                    WHERE token = ? AND expires_at > CURRENT_TIMESTAMP
                ''', (token,))
                
                if not cursor.fetchone():
                    return None
            
            return {
                'id': payload['user_id'],
                'username': payload['username'],
                'email': payload['email'],
                'role': payload['role']
            }
            
        except jwt.ExpiredSignatureError:
            print(" Token expired")
            return None
        except jwt.InvalidTokenError:
            print(" Invalid token")
            return None
        except Exception as e:
            print(f" Session verification failed: {e}")
            return None


# Global instance
user_auth_manager = UserAuthManager()
