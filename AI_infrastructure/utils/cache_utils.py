"""
Performance Caching Utilities
Provides safe caching wrappers with Redis fallback

Created: December 17, 2025
Author: Performance Optimization Agent
"""
import json
import logging
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def get_cached_or_fetch(
    cache_key: str,
    fetch_function: Callable,
    ttl: int = 300,
    redis_manager=None
) -> Any:
    """
    Generic cache wrapper - tries Redis cache first, falls back to fetch function
    
    Args:
        cache_key: Redis cache key
        fetch_function: Function to call on cache miss (should return dict/list)
        ttl: Cache TTL in seconds (default: 5 minutes)
        redis_manager: RedisManager instance (optional, will import if None)
    
    Returns:
        Cached or freshly fetched data
    
    Example:
        def expensive_db_query():
            return db.query("SELECT * FROM users")
        
        users = get_cached_or_fetch(
            cache_key='users:all',
            fetch_function=expensive_db_query,
            ttl=600  # 10 minutes
        )
    """
    # Import Redis manager if not provided
    if redis_manager is None:
        try:
            from AI_infrastructure.redis_manager import get_redis_manager
            redis_manager = get_redis_manager()
        except Exception as e:
            logger.warning(f"[CACHE] Redis not available: {e}")
            # No caching - directly call fetch function
            return fetch_function()
    
    # Try cache first
    if redis_manager and redis_manager.connected:
        try:
            cached = redis_manager.cache_get(cache_key)
            if cached:
                logger.debug(f"[CACHE HIT] {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"[CACHE ERROR] Failed to get {cache_key}: {e}")
    
    # Cache miss or Redis unavailable - fetch fresh data
    logger.debug(f"[CACHE MISS] {cache_key} - fetching...")
    data = fetch_function()
    
    # Store in cache for next time
    if redis_manager and redis_manager.connected:
        try:
            redis_manager.cache_set(cache_key, json.dumps(data), ttl)
            logger.debug(f"[CACHE SET] {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"[CACHE ERROR] Failed to set {cache_key}: {e}")
    
    return data


def invalidate_cache(cache_key: str, redis_manager=None) -> bool:
    """
    Invalidate (delete) a cache key
    
    Args:
        cache_key: Redis cache key to delete
        redis_manager: RedisManager instance (optional)
    
    Returns:
        True if deleted, False otherwise
    
    Example:
        # After updating user
        invalidate_cache('user:123')
    """
    if redis_manager is None:
        try:
            from AI_infrastructure.redis_manager import get_redis_manager
            redis_manager = get_redis_manager()
        except:
            return False
    
    if redis_manager and redis_manager.connected:
        try:
            result = redis_manager.cache_delete(cache_key)
            if result:
                logger.debug(f"[CACHE INVALIDATE] {cache_key}")
            return result
        except Exception as e:
            logger.warning(f"[CACHE ERROR] Failed to invalidate {cache_key}: {e}")
    
    return False


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key (default: function name)
    
    Example:
        @cached(ttl=600, key_prefix='user')
        def get_user_profile(user_id: int):
            return db.query("SELECT * FROM users WHERE id = %s", user_id)
        
        # First call: fetches from DB, caches result
        profile = get_user_profile(123)  # Cache key: 'user:get_user_profile:123'
        
        # Second call: returns from cache
        profile = get_user_profile(123)  # Fast!
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            func_name = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            
            # Simple key generation (args only, kwargs ignored for simplicity)
            arg_str = ':'.join(str(arg) for arg in args)
            cache_key = f"{func_name}:{arg_str}" if arg_str else func_name
            
            # Use generic cache wrapper
            return get_cached_or_fetch(
                cache_key=cache_key,
                fetch_function=lambda: func(*args, **kwargs),
                ttl=ttl
            )
        
        return wrapper
    return decorator


# Example usage patterns:

def cache_tool_registry(registry_data: dict, ttl: int = 3600) -> bool:
    """Cache tool registry (1 hour TTL by default)"""
    try:
        from AI_infrastructure.redis_manager import get_redis_manager
        redis_manager = get_redis_manager()
        
        if redis_manager and redis_manager.connected:
            return redis_manager.cache_set('tool:registry:v3', json.dumps(registry_data), ttl)
    except:
        pass
    return False


def get_cached_tool_registry() -> Optional[dict]:
    """Get cached tool registry"""
    try:
        from AI_infrastructure.redis_manager import get_redis_manager
        redis_manager = get_redis_manager()
        
        if redis_manager and redis_manager.connected:
            cached = redis_manager.cache_get('tool:registry:v3')
            if cached:
                return json.loads(cached)
    except:
        pass
    return None


def cache_platform_credentials(user_id: int, platform: str, credentials: dict, ttl: int = 600) -> bool:
    """Cache platform credentials (10 minutes TTL by default)"""
    try:
        from AI_infrastructure.redis_manager import get_redis_manager
        redis_manager = get_redis_manager()
        
        if redis_manager and redis_manager.connected:
            cache_key = f"creds:{user_id}:{platform}"
            return redis_manager.cache_set(cache_key, json.dumps(credentials), ttl)
    except:
        pass
    return False


def get_cached_platform_credentials(user_id: int, platform: str) -> Optional[dict]:
    """Get cached platform credentials"""
    try:
        from AI_infrastructure.redis_manager import get_redis_manager
        redis_manager = get_redis_manager()
        
        if redis_manager and redis_manager.connected:
            cache_key = f"creds:{user_id}:{platform}"
            cached = redis_manager.cache_get(cache_key)
            if cached:
                return json.loads(cached)
    except:
        pass
    return None


def invalidate_platform_credentials(user_id: int, platform: str) -> bool:
    """Invalidate cached credentials (call when credentials are updated)"""
    try:
        from AI_infrastructure.redis_manager import get_redis_manager
        redis_manager = get_redis_manager()
        
        if redis_manager and redis_manager.connected:
            cache_key = f"creds:{user_id}:{platform}"
            return redis_manager.cache_delete(cache_key)
    except:
        pass
    return False
