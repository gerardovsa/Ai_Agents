"""
Session Manager
===============

Manage user sessions and cleanup expired sessions.
"""

import secrets
import psycopg2  # ✅ Added missing import
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, db_path: str = "ai_infrastructure.db"):
        """Initialize session manager"""
        self.db_path = db_path
        self.default_expiry_hours = 24
    
    def get_connection(self) -> psycopg2.connection:
        """Get database connection"""
        return psycopg2.connect(self.db_path)
    
    def create_session(self, user_id: int, 
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None,
                      expiry_hours: Optional[int] = None) -> str:
        """
        Create new session for user
        
        Args:
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent
            expiry_hours: Hours until expiry (default: 24)
        
        Returns:
            Session token
        """
        conn = self.get_connection()
        
        # ✅ Fixed: cursor now uses context manager
        with conn.cursor() as cursor:
            
            # Generate secure token
            token = secrets.token_urlsafe(32)
            
            # Calculate expiry
            hours = expiry_hours or self.default_expiry_hours
            expires_at = datetime.now() + timedelta(hours=hours)
            
            cursor.execute("""
                INSERT INTO user_sessions (user_id, token, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, token, ip_address, user_agent, expires_at))
            
            conn.commit()
        
        conn.close()
        
        return token
    
    def validate_session(self, token: str) -> Optional[Dict]:
        """
        Validate session token
        
        Args:
            token: Session token
        
        Returns:
            Session dict if valid, None if invalid/expired
        """
        conn = self.get_connection()
        
        # ✅ Fixed: cursor now uses context manager
        with conn.cursor() as cursor:
            
            cursor.execute("""
                SELECT * FROM user_sessions 
                WHERE token = %s AND expires_at > %s
            """, (token, datetime.now()))
            
            row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'token': row[2],
                'ip_address': row[3],
                'user_agent': row[4],
                'created_at': row[5],
                'expires_at': row[6]
            }
        
        return None
    
    def get_active_sessions(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Get all active sessions
        
        Args:
            user_id: Filter by user ID (optional)
        
        Returns:
            List of active session dicts
        """
        conn = self.get_connection()
        
        # ✅ Fixed: cursor now uses context manager
        with conn.cursor() as cursor:
            
            if user_id:
                cursor.execute("""
                    SELECT * FROM user_sessions 
                    WHERE user_id = %s AND expires_at > %s
                    ORDER BY created_at DESC
                """, (user_id, datetime.now()))
            else:
                cursor.execute("""
                    SELECT * FROM user_sessions 
                    WHERE expires_at > %s
                    ORDER BY created_at DESC
                """, (datetime.now(),))
            
            rows = cursor.fetchall()
        
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                'id': row[0],
                'user_id': row[1],
                'token': row[2],
                'ip_address': row[3],
                'user_agent': row[4],
                'created_at': row[5],
                'expires_at': row[6]
            })
        
        return sessions
    
    def delete_session(self, token: str) -> bool:
        """Delete specific session"""
        conn = self.get_connection()
        
        # ✅ Fixed: cursor now uses context manager
        with conn.cursor() as cursor:
            
            cursor.execute("DELETE FROM user_sessions WHERE token = %s", (token,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
        
        conn.close()
        
        return deleted
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions
        
        Returns:
            Number of sessions deleted
        """
        conn = self.get_connection()
        
        # ✅ Fixed: cursor now uses context manager
        with conn.cursor() as cursor:
            
            cursor.execute("""
                DELETE FROM user_sessions 
                WHERE expires_at <= %s
            """, (datetime.now(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
        
        conn.close()
        
        return deleted_count
    
    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        conn = self.get_connection()
        
        # ✅ Fixed: All queries now in single cursor context
        with conn.cursor() as cursor:
            
            # Total sessions
            cursor.execute("SELECT COUNT(*) FROM user_sessions")
            total = cursor.fetchone()[0]
            
            # Active sessions
            cursor.execute("""
                SELECT COUNT(*) FROM user_sessions 
                WHERE expires_at > %s
            """, (datetime.now(),))
            active = cursor.fetchone()[0]
            
            # Expired sessions
            expired = total - active
            
            # Unique users with active sessions
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM user_sessions 
                WHERE expires_at > %s
            """, (datetime.now(),))
            active_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sessions': total,
            'active_sessions': active,
            'expired_sessions': expired,
            'active_users': active_users
        }
    
    def print_active_sessions(self):
        """Print formatted list of active sessions"""
        sessions = self.get_active_sessions()
        
        print("=" * 70)
        print("ACTIVE SESSIONS")
        print("=" * 70)
        print(f"Total Active: {len(sessions)}")
        print()
        
        for session in sessions:
            print(f"  🔑 Session ID: {session['id']}")
            print(f"     User ID: {session['user_id']}")
            print(f"     Token: {session['token'][:20]}...")
            print(f"     IP: {session['ip_address'] or 'N/A'}")
            print(f"     Created: {session['created_at']}")
            print(f"     Expires: {session['expires_at']}")
            print()
        
        print("=" * 70)


if __name__ == "__main__":
    # Test session manager
    manager = SessionManager()
    stats = manager.get_session_stats()
    print(f"Session Stats: {stats}")
    manager.print_active_sessions()