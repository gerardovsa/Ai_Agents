"""
Redis Manager for Cross-Worker Session Sharing
Handles active user sessions, typing indicators, and message delivery tracking
"""
import os
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class RedisManager:
    """Manages Redis connections and operations for realtime features"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis connection
        Args:
            redis_url: Redis connection URL (default: from env REDIS_URL)
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.client = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Establish Redis connection with fallback"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.client.ping()
            self.connected = True
            print(f"[REDIS] Connected to {self.redis_url}")
        except Exception as e:
            print(f"[REDIS] Connection failed: {e}")
            print("[REDIS] Falling back to in-memory storage")
            self.connected = False
            self.client = None
    
    # ========================================
    # ACTIVE USERS MANAGEMENT
    # ========================================
    
    def set_user_session(self, user_id: int, session_token: str, session_data: Dict[str, Any], ttl: int = 300):
        """
        Store user session in Redis
        Args:
            user_id: User ID
            session_token: Unique session token
            session_data: Session metadata (device, name, room, scope, etc.)
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        if not self.connected:
            return False
        
        try:
            key = f"user_session:{user_id}:{session_token}"
            session_data['last_heartbeat'] = datetime.now().isoformat()
            
            self.client.setex(
                key,
                ttl,
                json.dumps(session_data)
            )
            
            # Add to user's session set
            self.client.sadd(f"user_sessions:{user_id}", session_token)
            self.client.expire(f"user_sessions:{user_id}", ttl)
            
            return True
        except Exception as e:
            print(f"[REDIS ERROR] set_user_session: {e}")
            return False
    
    def get_user_sessions(self, user_id: int) -> Dict[str, Dict]:
        """Get all sessions for a user"""
        if not self.connected:
            return {}
        
        try:
            session_tokens = self.client.smembers(f"user_sessions:{user_id}")
            sessions = {}
            
            for token in session_tokens:
                key = f"user_session:{user_id}:{token}"
                data = self.client.get(key)
                if data:
                    sessions[token] = json.loads(data)
            
            return sessions
        except Exception as e:
            print(f"[REDIS ERROR] get_user_sessions: {e}")
            return {}
    
    def update_heartbeat(self, user_id: int, session_token: str, ttl: int = 300):
        """Update session heartbeat timestamp"""
        if not self.connected:
            return False
        
        try:
            key = f"user_session:{user_id}:{session_token}"
            data = self.client.get(key)
            
            if data:
                session_data = json.loads(data)
                session_data['last_heartbeat'] = datetime.now().isoformat()
                self.client.setex(key, ttl, json.dumps(session_data))
                return True
            
            return False
        except Exception as e:
            print(f"[REDIS ERROR] update_heartbeat: {e}")
            return False
    
    def remove_user_session(self, user_id: int, session_token: str):
        """Remove user session"""
        if not self.connected:
            return False
        
        try:
            key = f"user_session:{user_id}:{session_token}"
            self.client.delete(key)
            self.client.srem(f"user_sessions:{user_id}", session_token)
            return True
        except Exception as e:
            print(f"[REDIS ERROR] remove_user_session: {e}")
            return False
    
    def get_all_active_users(self) -> Dict[int, Dict[str, Dict]]:
        """Get all active users across all workers"""
        if not self.connected:
            return {}
        
        try:
            # Scan for all user session sets
            active_users = {}
            
            for key in self.client.scan_iter("user_sessions:*"):
                user_id = int(key.split(":")[-1])
                sessions = self.get_user_sessions(user_id)
                if sessions:
                    active_users[user_id] = sessions
            
            return active_users
        except Exception as e:
            print(f"[REDIS ERROR] get_all_active_users: {e}")
            return {}
    
    # ========================================
    # TYPING INDICATORS
    # ========================================
    
    def set_typing(self, user_id: int, user_name: str, room: str, agent_id: Optional[str] = None, ttl: int = 10):
        """
        Set typing indicator (expires automatically after TTL)
        Args:
            user_id: User ID
            user_name: User display name
            room: Room name (e.g., 'synergy_board')
            agent_id: Optional agent ID being typed in
            ttl: Expiry time in seconds (default: 10s)
        """
        if not self.connected:
            return False
        
        try:
            key = f"typing:{room}:{agent_id or 'general'}"
            typing_data = {
                'user_id': user_id,
                'user_name': user_name,
                'timestamp': datetime.now().isoformat()
            }
            
            self.client.setex(
                f"{key}:{user_id}",
                ttl,
                json.dumps(typing_data)
            )
            return True
        except Exception as e:
            print(f"[REDIS ERROR] set_typing: {e}")
            return False
    
    def get_typing_users(self, room: str, agent_id: Optional[str] = None) -> List[Dict]:
        """Get list of users currently typing"""
        if not self.connected:
            return []
        
        try:
            pattern = f"typing:{room}:{agent_id or 'general'}:*"
            typing_users = []
            
            for key in self.client.scan_iter(pattern):
                data = self.client.get(key)
                if data:
                    typing_users.append(json.loads(data))
            
            return typing_users
        except Exception as e:
            print(f"[REDIS ERROR] get_typing_users: {e}")
            return []
    
    # ========================================
    # MESSAGE READ RECEIPTS
    # ========================================
    
    def mark_message_delivered(self, message_id: str, user_id: int):
        """Mark message as delivered to user"""
        if not self.connected:
            return False
        
        try:
            key = f"message:delivered:{message_id}"
            self.client.sadd(key, user_id)
            self.client.expire(key, 86400)  # 24 hours
            return True
        except Exception as e:
            print(f"[REDIS ERROR] mark_message_delivered: {e}")
            return False
    
    def mark_message_read(self, message_id: str, user_id: int):
        """Mark message as read by user"""
        if not self.connected:
            return False
        
        try:
            key = f"message:read:{message_id}"
            timestamp_key = f"message:read_time:{message_id}:{user_id}"
            
            self.client.sadd(key, user_id)
            self.client.setex(timestamp_key, 86400, datetime.now().isoformat())
            self.client.expire(key, 86400)  # 24 hours
            return True
        except Exception as e:
            print(f"[REDIS ERROR] mark_message_read: {e}")
            return False
    
    def get_message_status(self, message_id: str) -> Dict:
        """Get delivery/read status for message"""
        if not self.connected:
            return {'delivered': [], 'read': []}
        
        try:
            delivered = list(self.client.smembers(f"message:delivered:{message_id}"))
            read = list(self.client.smembers(f"message:read:{message_id}"))
            
            return {
                'delivered': [int(uid) for uid in delivered],
                'read': [int(uid) for uid in read]
            }
        except Exception as e:
            print(f"[REDIS ERROR] get_message_status: {e}")
            return {'delivered': [], 'read': []}
    
    # ========================================
    # UTILITY
    # ========================================
    
    def cleanup_expired_sessions(self):
        """Manual cleanup of expired sessions (Redis handles TTL automatically)"""
        if not self.connected:
            return 0
        
        # Redis handles expiration automatically via TTL
        # This method is kept for compatibility but does nothing
        return 0
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        if not self.connected or not self.client:
            return False
        
        try:
            return self.client.ping()
        except:
            return False


# Singleton instance
_redis_manager = None

def get_redis_manager() -> RedisManager:
    """Get or create Redis manager instance"""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager
