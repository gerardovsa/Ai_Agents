"""
User Manager
============

Manage users and their credentials in the AI Agents system.
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class UserManager:
    """Manage users and authentication"""
    
    def __init__(self, db_path: str = "ai_infrastructure.db"):
        """Initialize user manager"""
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_user(self, username: str, email: str, 
                   role: str = "user", password: Optional[str] = None) -> int:
        """
        Create a new user
        
        Args:
            username: Unique username
            email: User's email
            role: User role (default: 'user')
            password: Optional password (will be hashed)
        
        Returns:
            User ID of created user
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Hash password if provided
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, created_at, last_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, password_hash, role, datetime.now(), datetime.now()))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        
        except sqlite3.IntegrityError as e:
            print(f" Error: {e}")
            return -1
        finally:
            conn.close()
    
    def get_user(self, user_id: Optional[int] = None, 
                 email: Optional[str] = None,
                 username: Optional[str] = None) -> Optional[Dict]:
        """
        Get user by ID, email, or username
        
        Args:
            user_id: User ID
            email: User email
            username: Username
        
        Returns:
            User dict or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("SELECT * FROM ai_infrastructure.users WHERE id = %s", (user_id,))
        elif email:
            cursor.execute("SELECT * FROM ai_infrastructure.users WHERE email = %s", (email,))
        elif username:
            cursor.execute("SELECT * FROM ai_infrastructure.users WHERE username = %s", (username,))
        else:
            conn.close()
            return None
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3],
                'role': row[4],
                'primary_gmail': row[5],
                'created_at': row[6],
                'last_active': row[7],
                'metadata': row[8],
                'is_primary': row[9]
            }
        
        return None
    
    def list_users(self, role: Optional[str] = None) -> List[Dict]:
        """
        List all users
        
        Args:
            role: Filter by role (optional)
        
        Returns:
            List of user dicts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if role:
            cursor.execute("SELECT * FROM ai_infrastructure.users WHERE role = %s ORDER BY created_at DESC", (role,))
        else:
            cursor.execute("SELECT * FROM ai_infrastructure.users ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[4],
                'primary_gmail': row[5],
                'created_at': row[6],
                'last_active': row[7],
                'is_primary': row[9]
            })
        
        return users
    
    def update_last_active(self, user_id: int):
        """Update user's last active timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET last_active = %s 
            WHERE id = %s
        """, (datetime.now(), user_id))
        conn.commit()
        conn.close()
    
    def add_platform_credential(self, user_id: int, platform: str,
                               credential_type: str, credential_value: str,
                               credential_key: Optional[str] = None) -> bool:
        """
        Add platform credentials for user
        
        Args:
            user_id: User ID
            platform: Platform name (e.g., 'google', 'microsoft')
            credential_type: Type (e.g., 'oauth_token', 'api_key')
            credential_value: The credential value
            credential_key: Optional key for key-value credentials
        
        Returns:
            True if successful
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO user_platform_credentials 
                (user_id, platform, credential_type, credential_key, credential_value, 
                 is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, 1, %s, %s)
            """, (user_id, platform, credential_type, credential_key, credential_value,
                  datetime.now(), datetime.now()))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f" Error adding credential: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_credentials(self, user_id: int, platform: Optional[str] = None) -> List[Dict]:
        """
        Get user's platform credentials
        
        Args:
            user_id: User ID
            platform: Filter by platform (optional)
        
        Returns:
            List of credential dicts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if platform:
            cursor.execute("""
                SELECT * FROM user_platform_credentials 
                WHERE user_id = %s AND platform = %s AND is_active = 1
            """, (user_id, platform))
        else:
            cursor.execute("""
                SELECT * FROM user_platform_credentials 
                WHERE user_id = %s AND is_active = 1
            """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        credentials = []
        for row in rows:
            credentials.append({
                'id': row[0],
                'user_id': row[1],
                'platform': row[2],
                'credential_type': row[3],
                'credential_key': row[4],
                'credential_value': row[5],
                'is_active': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        return credentials
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and all associated data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM ai_infrastructure.users WHERE id = %s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f" Error deleting user: {e}")
            return False
        finally:
            conn.close()
    
    def print_user_list(self, users=None):
        """Print formatted user list"""
        if users is None:
            users = self.list_users()
        
        print("=" * 70)
        print("USER LIST")
        print("=" * 70)
        print(f"Total Users: {len(users)}")
        print()
        
        for user in users:
            print(f"  👤 {user['username']} (ID: {user['id']})")
            print(f"     Email: {user['email']}")
            print(f"     Role: {user['role']}")
            if user['primary_gmail']:
                print(f"     Gmail: {user['primary_gmail']}")
            print(f"     Created: {user['created_at']}")
            print(f"     Last Active: {user['last_active']}")
            print()
        
        print("=" * 70)


if __name__ == "__main__":
    # Test user manager
    manager = UserManager()
    manager.print_user_list()
