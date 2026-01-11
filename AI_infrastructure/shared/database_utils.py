
"""
FILE: AI_infrastructure/shared/database_utils.py
PURPOSE: Database connection utility for Supabase PostgreSQL

DEPENDENCIES:
- psycopg2 - Supabase PostgreSQL connections
- os - Environment variable detection
- pathlib - Path handling

EXPORTS:
- get_database_connection(db_name: str) -> Connection - Get Supabase DB connection
- get_supabase_schema_name(db_name: str) -> str - Convert DB name to PostgreSQL schema
- is_using_supabase() -> bool - Always returns True (legacy compatibility)

ENVIRONMENT VARIABLES:
- SUPABASE_DB_URL: PostgreSQL connection URL (REQUIRED)

NOTES:
- Uses Supabase PostgreSQL with schema separation
- Each database becomes a PostgreSQL schema (sessions, ai_infrastructure, etc.)
- Connection pooling for performance (1-3 connections per schema)
- Thread-safe connection management

LAST MODIFIED: 2025-11-20 - Removed SQLite support, Supabase only
"""

import os
import threading
import time
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

# Import colored print helper
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger_config import Colors

def cprint(text: str, color: str = Colors.RESET):
    """Print with color"""
    print(f"{color}{text}{Colors.RESET}")

# Load environment variables from project root
_root_dir = Path(__file__).parent.parent.parent
_env_file = _root_dir / '.env.master'
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()  # Try default .env

# CONNECTION POOLING - Thread-safe connection pools
_connection_pools = {}
_pool_lock = threading.Lock()
_pool_stats = {
    'pools_created': 0,
    'connections_acquired': 0,
    'connections_returned': 0,
    'pool_hits': 0,
    'pool_misses': 0,
    'total_wait_time': 0.0,
    'avg_wait_time': 0.0
}


def is_using_supabase() -> bool:
    """
    Check if application should use Supabase PostgreSQL
    
    Returns:
        bool: Always True (legacy compatibility function)
    
    Environment Variables:
        SUPABASE_DB_URL: Required PostgreSQL connection URL
    
    Note:
        This function exists for backward compatibility.
        Application now exclusively uses Supabase.
    """
    return True


def get_supabase_schema_name(db_name: str) -> str:
    """
    Convert database name to PostgreSQL schema name
    
    Args:
        db_name: Database name (e.g., 'ai_infrastructure', 'sessions')
    
    Returns:
        str: PostgreSQL schema name (same as db_name, lowercased)
    
    Examples:
        'ai_infrastructure' -> 'ai_infrastructure'
        'sessions' -> 'sessions'
        'synergy_sessions' -> 'synergy_sessions'
    """
    return db_name.lower().replace('.db', '')


def get_connection_pool(schema_name: str):
    """
    Get or create thread-safe connection pool for schema
    
    CONNECTION POOLING BENEFITS:
    - 10-100x faster connections (reuse instead of create)
    - Thread-safe for concurrent requests
    - Resource efficient (maintains 1-3 connections)
    - Automatic cleanup (connections returned to pool)
    
    Args:
        schema_name: PostgreSQL schema name
    
    Returns:
        psycopg2.pool.ThreadedConnectionPool
    
    Pool Configuration:
        - Min connections: 4 (ready for burst traffic)
        - Max connections: 12 (optimized for Supabase Micro tier - 60 connection limit)
        - Connection timeout: 30s
        - Statement timeout: 60s
    """
    global _connection_pools, _pool_stats
    
    with _pool_lock:
        if schema_name not in _connection_pools:
            try:
                import psycopg2
                from psycopg2 import pool
            except ImportError:
                raise ImportError(
                    "psycopg2 not installed. Run: pip install psycopg2-binary"
                )
            
            # CRITICAL: For Supabase Free Tier (Nano):
            # - Max database connections: 60
            # - Max pooler clients: 200
            # - Use TRANSACTION MODE pooler (port 6543) for Flask apps (default)
            # - SESSION MODE pooler (port 5432) as fallback for persistent connections
            # - Keep pool size SMALL (1-2 connections per schema)
            
            # Try Transaction Mode pooler first (optimal for Flask/serverless)
            db_url = os.getenv('SUPABASE_DB_URL_POOLER')
            connection_mode = 'Transaction Mode (port 6543)'
            
            if not db_url:
                # Fallback to Session Mode pooler
                db_url = os.getenv('SUPABASE_DB_URL_SESSION')
                connection_mode = 'Session Mode (port 5432) - FALLBACK'
                cprint(f"[WARNING] [POOL] Transaction pooler not configured, using Session Mode fallback", Colors.WARNING)
            
            if not db_url:
                # Final fallback to legacy SUPABASE_DB_URL variable (backward compatibility)
                db_url = os.getenv('SUPABASE_DB_URL')
                if db_url:
                    # Auto-detect port from URL to determine mode
                    if ':6543/' in db_url:
                        connection_mode = 'Legacy SUPABASE_DB_URL (Transaction Mode detected)'
                    elif ':5432/' in db_url:
                        connection_mode = 'Legacy SUPABASE_DB_URL (Session Mode detected)'
                    else:
                        connection_mode = 'Legacy SUPABASE_DB_URL (unknown port)'
                    cprint(f"[WARNING] [POOL] Using legacy SUPABASE_DB_URL variable - please migrate to SUPABASE_DB_URL_POOLER", Colors.WARNING)
            
            if not db_url:
                raise ValueError(
                    "No Supabase connection URL found. Set either:\n"
                    "  - SUPABASE_DB_URL_POOLER (Transaction Mode, port 6543) - RECOMMENDED\n"
                    "  - SUPABASE_DB_URL_SESSION (Session Mode, port 5432) - FALLBACK"
                )
            
            cprint(f" [POOL] Using {connection_mode} for '{schema_name}'", Colors.DB)
            
            # Create thread-safe connection pool
            # OPTIMIZED for Supabase Micro Plan (Jan 11, 2026):
            # - Transaction Mode pooler supports 200 concurrent CLIENT connections
            # - Backend limit is 60 connections (Supabase Micro plan limit)
            # - UI makes 10-15 concurrent requests on page load
            # - 3 schemas (ai_infrastructure, sessions, synergy_sessions)
            # - minconn=6: Keep 6 connections ready per schema (18 total baseline)
            # - maxconn=20: Allow up to 20 per schema during bursts (60 total = exactly at limit)
            # - Each connection is short-lived in transaction mode (seconds, not minutes)
            # - Pool auto-scales: 18 connections normally, up to 60 during traffic spikes
            _connection_pools[schema_name] = pool.ThreadedConnectionPool(
                minconn=6,      # Keep 6 connections ready (increased from 4)
                maxconn=20,     # Allow up to 20 concurrent connections (increased from 12 to use full Micro plan capacity)
                dsn=db_url,
                sslmode='require',
                connect_timeout=30,  # Increased from 10 to 30 seconds to handle network latency
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            
            _pool_stats['pools_created'] += 1
            _pool_stats['pool_misses'] += 1
            
            cprint(f" [POOL] Created connection pool for '{schema_name}' (6-20 connections)", Colors.SUCCESS)
            cprint(f" [POOL] Total pools: {_pool_stats['pools_created']}", Colors.INFO)
            cprint(f" [POOL] Total potential connections: {_pool_stats['pools_created'] * 20} (Supabase Micro limit: 60)", Colors.INFO)
            cprint(f" [POOL] Pool configuration: minconn=6, maxconn=20 (uses full Micro plan capacity)", Colors.INFO)
        else:
            _pool_stats['pool_hits'] += 1
        
        return _connection_pools[schema_name]


def get_pool_stats():
    """
    Get connection pool statistics
    
    Returns:
        dict: Pool stats including hits, misses, avg wait time
    """
    global _pool_stats
    
    if _pool_stats['connections_acquired'] > 0:
        _pool_stats['avg_wait_time'] = (
            _pool_stats['total_wait_time'] / _pool_stats['connections_acquired']
        )
    
    return dict(_pool_stats)


def get_all_pool_stats():
    """
    Get statistics for all connection pools by schema.
    
    Returns:
        dict: Schema name -> pool stats
    """
    global _connection_pools, _pool_stats
    
    all_stats = {}
    
    # Add global stats
    all_stats['_global'] = get_pool_stats()
    
    # Add per-pool stats if available
    for schema_name, pool in _connection_pools.items():
        # Get pool-specific stats (if tracked separately in future)
        # For now, just note which pools exist
        all_stats[schema_name] = {
            'pool_exists': True,
            'minconn': getattr(pool, 'minconn', 4),
            'maxconn': getattr(pool, 'maxconn', 12),
            'connections_acquired': _pool_stats['connections_acquired'],
            'connections_returned': _pool_stats['connections_returned'],
            'pool_hits': _pool_stats['pool_hits'],
            'pool_misses': _pool_stats['pool_misses']
        }
    
    return all_stats


def log_pool_usage():
    """
    Log current connection pool usage (for monitoring)
    """
    global _connection_pools, _pool_stats
    
    print(f"\n{'='*70}")
    print(f" [POOL] CONNECTION POOL USAGE REPORT")
    print(f"{'='*70}")
    
    with _pool_lock:
        for schema_name, pool_instance in _connection_pools.items():
            # Try to get pool statistics
            try:
                # psycopg2 pools expose _used and _pool attributes
                used = len(pool_instance._used) if hasattr(pool_instance, '_used') else '?'
                available = len(pool_instance._pool) if hasattr(pool_instance, '_pool') else '?'
                maxconn = pool_instance._maxconn if hasattr(pool_instance, '_maxconn') else '?'
                
                print(f"\nSchema: {schema_name}")
                print(f"  Active connections: {used}")
                print(f"  Available in pool: {available}")
                print(f"  Max connections: {maxconn}")
                print(f"  Status: {'OK' if used < maxconn else 'EXHAUSTED'}")
            except Exception as e:
                print(f"\nSchema: {schema_name}")
                print(f"  Error getting stats: {e}")
    
    print(f"\nGlobal Stats:")
    print(f"  Total pools: {_pool_stats['pools_created']}")
    print(f"  Connections acquired: {_pool_stats['connections_acquired']}")
    print(f"  Connections returned: {_pool_stats['connections_returned']}")
    print(f"  Leaked connections: {_pool_stats['connections_acquired'] - _pool_stats['connections_returned']}")
    print(f"  Pool hits: {_pool_stats['pool_hits']}")
    print(f"  Pool misses: {_pool_stats['pool_misses']}")
    
    if _pool_stats['connections_acquired'] > 0:
        avg_wait = _pool_stats['total_wait_time'] / _pool_stats['connections_acquired']
        print(f"  Avg wait time: {avg_wait*1000:.1f}ms")
    
    print(f"{'='*70}\n")


def close_all_pools():
    """
    Close all connection pools (for graceful shutdown)
    """
    global _connection_pools
    
    # Log final usage before closing
    log_pool_usage()
    
    with _pool_lock:
        for schema_name, pool_instance in _connection_pools.items():
            try:
                pool_instance.closeall()
                cprint(f" [POOL] Closed pool for '{schema_name}'", Colors.SUCCESS)
            except Exception as e:
                print(f" [POOL] Error closing pool '{schema_name}': {e}")
        
        _connection_pools.clear()
        cprint(f" [POOL] All pools closed", Colors.SUCCESS)


def reset_connection_pool(schema_name: str = None):
    """
    Reset connection pool(s) - useful when connections are leaked or network recovered
    
    Args:
        schema_name: Specific schema to reset, or None to reset all
    """
    global _connection_pools, _pool_stats
    
    with _pool_lock:
        if schema_name:
            # Reset specific pool
            if schema_name in _connection_pools:
                try:
                    pool = _connection_pools[schema_name]
                    pool.closeall()
                    del _connection_pools[schema_name]
                    cprint(f" [POOL] Reset pool for '{schema_name}'", Colors.SUCCESS)
                except Exception as e:
                    print(f" [POOL] Error resetting pool '{schema_name}': {e}")
        else:
            # Reset all pools
            for name, pool in _connection_pools.items():
                try:
                    pool.closeall()
                    cprint(f" [POOL] Reset pool for '{name}'", Colors.SUCCESS)
                except Exception as e:
                    print(f" [POOL] Error resetting pool '{name}': {e}")
            
            _connection_pools.clear()
            # Reset stats too
            _pool_stats['connections_acquired'] = 0
            _pool_stats['connections_returned'] = 0
            cprint(f" [POOL] All pools reset", Colors.SUCCESS)


def get_database_connection(db_name: str = 'ai_infrastructure'):
    """
    Get Supabase PostgreSQL database connection
    
    Args:
        db_name: Database name without extension
                 Examples: 'ai_infrastructure', 'sessions', 'synergy_sessions'
    
    Returns:
        DatabaseConnection: Wrapped psycopg2.Connection with auto-placeholder conversion
        
    Raises:
        ImportError: If psycopg2 not installed
        ValueError: If SUPABASE_DB_URL not set
        ConnectionError: If database connection fails
    
    Connection Pooling:
        - Uses connection pool for performance (10-100x faster)
        - Thread-safe for concurrent requests
        - Automatically returns connection to pool on close
    
    Examples:
        # Get connection to ai_infrastructure schema
        conn = get_database_connection('ai_infrastructure')
        
        # Get connection to sessions schema
        conn = get_database_connection('sessions')
        
        # Use with context manager (auto-close)
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM threads")
    """
    global _pool_stats
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        raise ImportError(
            "psycopg2 not installed. Run: pip install psycopg2-binary"
        )
    
    schema_name = get_supabase_schema_name(db_name)
    
    conn_acquired = False
    conn = None
    
    try:
        # GET CONNECTION FROM POOL (FAST - reuses existing connections)
        start_time = time.time()
        pool_instance = get_connection_pool(schema_name)
        
        # CRITICAL FIX: Add timeout to prevent infinite blocking
        # If pool is exhausted, fail fast instead of blocking forever
        import threading
        
        def _get_conn_with_timeout():
            nonlocal conn
            try:
                conn = pool_instance.getconn()
            except Exception as e:
                # Connection acquisition failed in thread
                print(f"❌ [POOL] getconn() failed in thread: {e}")
                conn = None
        
        thread = threading.Thread(target=_get_conn_with_timeout)
        thread.daemon = True
        thread.start()
        thread.join(timeout=5.0)  # Wait max 5 seconds
        
        if thread.is_alive() or conn is None:
            # Pool exhausted or connection failed - log leaked connections
            # ✅ FIX: Show both global and per-schema stats for better debugging
            pool_instance = _connection_pools.get(schema_name)
            pool_info = "N/A"
            if pool_instance:
                try:
                    # Get current pool state (private variables, may not always work)
                    pool_info = f"minconn={pool_instance.minconn}, maxconn={pool_instance.maxconn}"
                except:
                    pool_info = "Unable to get pool details"
            
            print(f"\n{'='*70}")
            cprint(f" [POOL] CONNECTION POOL EXHAUSTED FOR SCHEMA: {schema_name}", Colors.ERROR)
            print(f"{'='*70}")
            print(f"Schema: {schema_name}")
            print(f"Pool config: {pool_info}")
            print(f"\nGlobal stats (all schemas combined):")
            print(f"  Acquired: {_pool_stats['connections_acquired']}")
            print(f"  Returned: {_pool_stats['connections_returned']}")
            print(f"  LEAKED: {_pool_stats['connections_acquired'] - _pool_stats['connections_returned']}")
            print(f"\n⚠️  NOTE: These are GLOBAL stats across all schemas.")
            print(f"   Each schema has its own pool (maxconn=12).")
            print(f"   If global leaked=0 but pool exhausted, issue is:")
            print(f"     1. Too many CONCURRENT requests for this schema")
            print(f"     2. Slow queries holding connections too long")
            print(f"     3. Network latency to Supabase")
            print(f"\n SOLUTION:")
            print(f"  1. Restart service to reset pools: Render dashboard → Manual Deploy")
            print(f"  2. Optimize slow queries (check for 20+ second queries)")
            print(f"  3. Add query caching for frequently accessed data")
            print(f"  4. Consider increasing maxconn if legitimate high concurrency")
            print(f"{'='*70}\n")
            
            # If thread is still alive, it may have acquired connection - mark as leaked
            if thread.is_alive() and conn is not None:
                print(f"⚠️  [POOL] Thread still running - connection may be leaked")
                _pool_stats['connections_acquired'] += 1  # Count the leaked connection
            
            raise ConnectionError(
                f"Connection pool exhausted for '{schema_name}'. "
                f"Leaked connections: {_pool_stats['connections_acquired'] - _pool_stats['connections_returned']}. "
                f"Check code for missing conn.close() calls and network connectivity."
            )
        
        wait_time = time.time() - start_time
        
        # ✅ FIX 4: Track pool stats AFTER successful getconn()
        _pool_stats['connections_acquired'] += 1
        conn_acquired = True
        _pool_stats['total_wait_time'] += wait_time
        
        # ✅ FIX 5: Test if connection is alive before using it
        # Supabase may close idle connections - pool returns them but they're dead
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT 1")  # Quick liveness check
            cursor.close()
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as test_err:
            # Connection is dead - discard it and get a fresh one
            print(f" [POOL] Connection test failed, discarding dead connection: {test_err}")
            try:
                pool_instance.putconn(conn, close=True)  # Remove from pool
                _pool_stats['connections_returned'] += 1  # Manually track return since putconn succeeded
            except Exception as putconn_err:
                print(f" [POOL] Failed to remove dead connection (continuing): {putconn_err}")
                # ✅ CRITICAL FIX: If putconn fails, manually correct stats to prevent false leak detection
                # The connection was acquired (stats incremented) but couldn't be returned to pool
                # We need to mark it as "returned" to avoid permanent leak count inflation
                _pool_stats['connections_returned'] += 1
            # Recursively retry with new connection (max 2 retries to handle zombie cascade)
            if not hasattr(get_database_connection, '_retry_count'):
                get_database_connection._retry_count = 0
            if get_database_connection._retry_count < 2:  # Increased from 1 to 2
                get_database_connection._retry_count += 1
                print(f" [POOL] Retrying with fresh connection (attempt {get_database_connection._retry_count}/2)...")
                result = get_database_connection(db_name)
                get_database_connection._retry_count = 0
                return result
            else:
                get_database_connection._retry_count = 0
                raise ConnectionError(f"Failed to get live connection after 2 retries: {test_err}")
        
        # Set search_path and configure connection
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # ✅ FIX: Handle schema creation errors gracefully
        try:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            conn.commit()
        except psycopg2.Error as schema_err:
            # Schema may already exist (concurrent creation) or permission denied
            # Try to rollback and continue - connection is still usable
            try:
                conn.rollback()
                print(f" [POOL] Schema creation warning for '{schema_name}': {schema_err}")
            except Exception:
                # If rollback fails, connection is broken - close and get new one
                conn.close()
                raise
        
        cursor.execute(f"SET search_path TO {schema_name}, public")
        cursor.execute("SET statement_timeout = '60s'")
        cursor.close()
        conn.commit()
        
        print(f" [POOL] Got connection from pool for '{schema_name}' (wait: {wait_time*1000:.1f}ms)")
        
        # Wrap connection to return to pool on close
        class PooledConnection:
            def __init__(self, conn, pool, schema):
                self._conn = conn
                self._pool = pool
                self._schema = schema
                self._closed = False
                self._return_attempted = False  # ✅ FIX 3: Prevent double-return
            
            def close(self):
                """Return to pool instead of closing"""
                if self._closed or self._return_attempted:
                    # Already closed or return attempted - skip
                    return
                
                self._return_attempted = True  # ✅ Mark BEFORE putconn
                
                try:
                    if not self._conn.closed:
                        # ✅ CRITICAL: ALWAYS rollback before testing or returning
                        # This handles aborted transactions that would cause putconn() to fail
                        try:
                            self._conn.rollback()
                        except Exception as rollback_err:
                            print(f"⚠️  [POOL] Rollback failed (connection may be dead): {rollback_err}")
                        
                        # ✅ FIX: Test connection liveness before returning to pool
                        try:
                            test_cursor = self._conn.cursor()
                            test_cursor.execute("SELECT 1")
                            test_cursor.close()
                            # Connection alive - safe to return
                            self._pool.putconn(self._conn)
                            _pool_stats['connections_returned'] += 1
                            self._closed = True
                        except (psycopg2.OperationalError, psycopg2.InterfaceError) as zombie_err:
                            # Connection died during use - don't return zombie to pool
                            print(f"⚠️  [POOL] Discarding zombie connection (died during use): {zombie_err}")
                            try:
                                self._pool.putconn(self._conn, close=True)  # Close instead of return
                            except:
                                pass
                            self._closed = True
                except Exception as e:
                    # ✅ Last resort: Try to rollback and return anyway
                    try:
                        print(f"⚠️  [POOL] Attempting emergency rollback for failed connection: {e}")
                        self._conn.rollback()
                        self._pool.putconn(self._conn)
                        _pool_stats['connections_returned'] += 1
                        self._closed = True
                        print(f"✅ [POOL] Emergency return succeeded for '{self._schema}'")
                    except Exception as final_err:
                        # Truly failed - mark as leaked
                        self._closed = True
                        print(f"❌ [POOL] Failed to return connection to pool: {e}")
                        print(f"   Emergency rollback also failed: {final_err}")
                        print(f"   Schema: {self._schema}")
                        print(f"   This connection is now LEAKED (cannot be returned)")
                        leaked = _pool_stats['connections_acquired'] - _pool_stats['connections_returned']
                        print(f"   Total leaked connections: {leaked}")
            
            def __getattr__(self, name):
                return getattr(self._conn, name)
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.close()
                return False
            
            def __del__(self):
                """Ensure connection returned even if close() not called"""
                if not self._closed and not self._return_attempted:
                    print(f"[WARNING] [POOL] Connection NOT returned in close() - attempting in __del__ for '{self._schema}'")
                    try:
                        self.close()
                    except:
                        print(f"❌ [POOL] Failed to return connection in __del__ - CONNECTION LEAKED")
        
        pooled_conn = PooledConnection(conn, pool_instance, schema_name)
        
        # Wrap with DatabaseConnection for placeholder conversion
        return DatabaseConnection(pooled_conn)
        
    except psycopg2.OperationalError as e:
        # Connection failed - return to pool if acquired
        if conn_acquired and conn is not None:
            try:
                pool_instance.putconn(conn)
                _pool_stats['connections_returned'] += 1
                print(f"✅ [POOL] Returned failed connection to pool")
            except Exception as pool_err:
                print(f"❌ [POOL] Failed to return connection: {pool_err}")
        
        # Detailed error logging
        error_msg = str(e)
        print(f"\n{'='*70}")
        print(f" [DB] SUPABASE CONNECTION FAILED - OPERATIONAL ERROR")
        print(f"{'='*70}")
        print(f"Database: {db_name}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {error_msg}")
        
        # Detailed diagnostics
        if "max clients" in error_msg.lower() or "maxclientsinSessionmode" in error_msg:
            print(f"\n DIAGNOSIS: Too many database connections")
            print(f"   - Supabase free tier has connection limits")
            print(f"   - Close other database connections")
            print(f"   - Restart application to reset connection pool")
            print(f"   - Consider upgrading Supabase plan")
        elif "timeout" in error_msg.lower():
            print(f"\n DIAGNOSIS: Connection timeout")
            print(f"   - Supabase server may be slow or unreachable")
            print(f"   - Network latency too high (>30 seconds)")
            print(f"   - Check internet connection")
        elif "could not connect" in error_msg.lower():
            print(f"\n DIAGNOSIS: Cannot reach Supabase server")
            print(f"   - Check SUPABASE_DB_URL is correct")
            print(f"   - Verify Supabase project is active")
            print(f"   - Check firewall/network settings")
        elif "password" in error_msg.lower() or "authentication" in error_msg.lower():
            print(f"\n DIAGNOSIS: Authentication failed")
            print(f"   - Check database password in SUPABASE_DB_URL")
            print(f"   - Verify credentials haven't expired")
        else:
            print(f"\n DIAGNOSIS: Unknown operational error")
        
        print(f"\n RECOVERY ATTEMPT: Retrying connection once...")
        print(f"{'='*70}\n")
        
        # Single retry attempt
        try:
            time.sleep(2)  # Wait 2 seconds before retry
            
            db_url = os.getenv('SUPABASE_DB_URL')
            if not db_url:
                raise ValueError("SUPABASE_DB_URL not set in environment")
            
            print(f" [DB] Retry attempt for '{db_name}'...")
            conn = psycopg2.connect(
                db_url,
                cursor_factory=RealDictCursor,
                connect_timeout=30,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
                options='-c client_min_messages=ERROR'
            )
            
            schema_name = get_supabase_schema_name(db_name)
            with conn.cursor() as cursor:
                # ✅ FIX: Handle schema creation errors gracefully
                try:
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                    conn.commit()
                except psycopg2.Error as schema_err:
                    # Schema may already exist (concurrent creation) - try to continue
                    try:
                        conn.rollback()
                        print(f" [DB] Schema creation warning for '{schema_name}': {schema_err}")
                    except Exception:
                        # If rollback fails, connection is broken
                        conn.close()
                        raise
                
                cursor.execute(f"SET search_path TO {schema_name}, public")
            
            conn.commit()
            print(f" [DB] RETRY SUCCESSFUL! Connected to Supabase")
            return DatabaseConnection(conn)
            
        except Exception as retry_error:
            print(f" [DB] RETRY FAILED: {retry_error}")
            print(f" [DB] CANNOT PROCEED - Supabase connection required")
            raise ConnectionError(
                f"Supabase connection failed after retry. "
                f"Original error: {error_msg}. "
                f"Retry error: {str(retry_error)}"
            )
    
    except Exception as e:
        # Return connection to pool if acquired before failure
        if conn_acquired and conn is not None:
            try:
                pool_instance.putconn(conn)
                _pool_stats['connections_returned'] += 1
                print(f"✅ [POOL] Returned failed connection to pool")
            except Exception as pool_err:
                print(f"❌ [POOL] Failed to return connection: {pool_err}")
        
        # Catch-all for other exceptions
        print(f"\n{'='*70}")
        print(f" [DB] SUPABASE CONNECTION FAILED - UNEXPECTED ERROR")
        print(f"{'='*70}")
        print(f"Database: {db_name}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*70}\n")
        raise ConnectionError(f"Supabase connection failed: {e}")


# Convenience functions for common databases
def get_ai_infrastructure_connection():
    """Get connection to ai_infrastructure database"""
    return get_database_connection('ai_infrastructure')


def get_sessions_connection():
    """Get connection to sessions database"""
    return get_database_connection('sessions')


def get_synergy_sessions_connection():
    """Get connection to synergy_sessions database"""
    return get_database_connection('synergy_sessions')


def get_stock_data_connection():
    """Get connection to stock_data database"""
    return get_database_connection('stock_data')


def get_kanban_analytics_connection():
    """Get connection to kanban_analytics database"""
    return get_database_connection('kanban_analytics')


def get_auto_increment_sql() -> str:
    """
    Get PostgreSQL auto-increment syntax
    
    Returns:
        'GENERATED ALWAYS AS IDENTITY' for PostgreSQL
    
    Usage:
        CREATE TABLE example (
            id INTEGER PRIMARY KEY {get_auto_increment_sql()},
            ...
        )
    """
    return 'GENERATED ALWAYS AS IDENTITY'


def adapt_sql_for_database(sql: str) -> str:
    """
    Adapt SQL syntax for PostgreSQL
    
    Converts SQLite-style syntax to PostgreSQL:
    - AUTOINCREMENT → GENERATED ALWAYS AS IDENTITY
    - INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY
    
    Args:
        sql: SQL query with SQLite syntax
    
    Returns:
        Adapted SQL for PostgreSQL
    
    Example:
        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, ...)"
        adapted = adapt_sql_for_database(sql)
        # Returns: "CREATE TABLE users (id SERIAL PRIMARY KEY, ...)"
    """
    # PostgreSQL adaptations
    sql = sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    sql = sql.replace('AUTOINCREMENT', '')  # Remove any remaining AUTOINCREMENT
    return sql


def convert_sql_placeholders(sql: str, params: Optional[tuple] = None):
    """
    Convert SQL placeholders to PostgreSQL style (%s)
    
    Args:
        sql: SQL query (supports ? or %s placeholders)
        params: Query parameters tuple (optional)
    
    Returns:
        - If params is None: returns converted SQL string only
        - If params provided: returns tuple of (converted_sql, params)
    
    Example:
        # Simple usage (string only):
        sql = convert_sql_placeholders("SELECT * FROM users WHERE id = ?")
        # Returns: "SELECT * FROM users WHERE id = %s"
        
        # With params (tuple):
        sql, params = convert_sql_placeholders("SELECT * FROM users WHERE id = ?", (123,))
        # Returns: ("SELECT * FROM users WHERE id = %s", (123,))
    """
    # Convert ? to %s for PostgreSQL
    converted_sql = sql.replace('?', '%s')
    
    if params is None:
        return converted_sql
    else:
        return (converted_sql, params)


class DatabaseCursor:
    """
    Cursor wrapper that automatically converts SQL placeholders
    
    Converts ? placeholders to %s for PostgreSQL compatibility.
    
    Usage:
        conn = get_database_connection('ai_infrastructure')
        cursor = DatabaseCursor(conn)
        cursor.execute("SELECT * FROM users WHERE id = %s", (123,))
        # Uses PostgreSQL %s placeholders
    """
    def __init__(self, connection):
        self.connection = connection
        import psycopg2.extras
        self._cursor = connection._wrapped_conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def execute(self, sql, params=None):
        """Execute with automatic placeholder conversion"""
        import re
        # Convert PostgreSQL numbered positional parameters ($1, $2, ...) to %s
        sql = re.sub(r'\$\d+', '%s', sql)
        
        # Convert ? to %s
        if params:
            sql, params = convert_sql_placeholders(sql, params)
        else:
            sql = convert_sql_placeholders(sql)
        
        return self._cursor.execute(sql, params)
    
    def fetchone(self):
        """Fetch one row"""
        return self._cursor.fetchone()
    
    def fetchall(self):
        """Fetch all rows"""
        return self._cursor.fetchall()
    
    def fetchmany(self, size=None):
        """Fetch many rows"""
        return self._cursor.fetchmany(size)
    
    def close(self):
        """Close cursor"""
        return self._cursor.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Delegate other attributes to wrapped cursor
    def __getattr__(self, name):
        return getattr(self._cursor, name)


class DatabaseConnection:
    """
    Connection wrapper that provides automatic SQL placeholder conversion
    
    Wraps psycopg2.Connection and returns DatabaseCursor when cursor() is called,
    which automatically converts ? to %s for PostgreSQL.
    """
    def __init__(self, connection):
        self._wrapped_conn = connection
    
    def cursor(self, *args, **kwargs):
        """Return DatabaseCursor that auto-converts placeholders"""
        if args or kwargs:
            # Pass through cursor factory if specified
            return self._wrapped_conn.cursor(*args, **kwargs)
        return DatabaseCursor(self)
    
    def commit(self):
        return self._wrapped_conn.commit()
    
    def rollback(self):
        return self._wrapped_conn.rollback()
    
    def close(self):
        return self._wrapped_conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._wrapped_conn.__exit__(exc_type, exc_val, exc_tb)
    
    # Delegate other attributes to wrapped connection
    def __getattr__(self, name):
        return getattr(self._wrapped_conn, name)


if __name__ == '__main__':
    """Test Supabase database connection"""
    print("=" * 60)
    print("Supabase Database Connection Test")
    print("=" * 60)
    
    print(f"\nEnvironment: Supabase PostgreSQL")
    print(f"SUPABASE_DB_URL: {'Set' if os.getenv('SUPABASE_DB_URL') else 'NOT SET'}")
    
    # Test connections
    databases = ['ai_infrastructure', 'sessions', 'synergy_sessions']
    
    for db_name in databases:
        print(f"\nTesting {db_name}...")
        try:
            conn = get_database_connection(db_name)
            print(f"   ✓ Connected to Supabase schema: {get_supabase_schema_name(db_name)}")
            conn.close()
        except Exception as e:
            print(f"   ✗ Failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Show pool stats
    stats = get_pool_stats()
    print("\nConnection Pool Statistics:")
    print(f"  Pools created: {stats['pools_created']}")
    print(f"  Pool hits: {stats['pool_hits']}")
    print(f"  Pool misses: {stats['pool_misses']}")
    print(f"  Connections acquired: {stats['connections_acquired']}")
    print(f"  Connections returned: {stats['connections_returned']}")
    print(f"  Avg wait time: {stats['avg_wait_time']*1000:.2f}ms")
    print("=" * 60)


# ==================== EXECUTE QUERY - CANONICAL PATTERN ====================

def execute_query(
    query: str,
    params: tuple = (),
    *,
    fetch_mode: str = 'all',
    schema: str = 'ai_infrastructure'
):
    """
    Execute query with automatic connection management (CANONICAL PATTERN)
    
    This is the RECOMMENDED way to execute database queries. Handles connection
    pooling, cleanup, and error handling automatically. No manual try/finally needed.
    
    Args:
        query: SQL query (use %s placeholders for PostgreSQL)
        params: Query parameters tuple (default: empty tuple)
        fetch_mode: Result fetch mode (keyword-only)
            - 'all': List[Dict] - all rows as list of dictionaries
            - 'one': Dict | None - single row as dictionary or None
            - 'value': Any - single value from first row, first column
            - None: int - affected row count (for INSERT/UPDATE/DELETE)
        schema: Database schema name (keyword-only, default: 'ai_infrastructure')
                Options: 'ai_infrastructure', 'sessions', 'synergy_sessions',
                        'stock_data', 'kanban_analytics'
    
    Returns:
        - fetch_mode='all': List[Dict] (all rows)
        - fetch_mode='one': Dict | None (single row)
        - fetch_mode='value': Any (single value)
        - fetch_mode=None: int (affected row count)
    
    Raises:
        Exception: If query execution fails (connection errors, SQL errors)
    
    Examples:
        # Select all rows
        users = execute_query(
            "SELECT * FROM users WHERE active = %s",
            (True,),
            fetch_mode='all',
            schema='ai_infrastructure'
        )
        # Returns: [{'id': 1, 'name': 'Alice', ...}, {'id': 2, 'name': 'Bob', ...}]
        
        # Select single row
        user = execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetch_mode='one'
        )
        # Returns: {'id': 1, 'name': 'Alice', ...} or None
        
        # Get single value
        count = execute_query(
            "SELECT COUNT(*) FROM users",
            (),
            fetch_mode='value'
        )
        # Returns: 42
        
        # Insert/Update (no fetch)
        affected = execute_query(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user_id,),
            fetch_mode=None
        )
        # Returns: 1 (number of rows affected)
        
        # Use different schema
        threads = execute_query(
            "SELECT * FROM threads WHERE user_id = %s",
            (user_id,),
            fetch_mode='all',
            schema='sessions'
        )
    
    Connection Management:
        - Automatically gets connection from pool
        - Automatically returns connection to pool (even on exceptions)
        - No manual try/finally blocks needed
        - Thread-safe (uses connection pooling)
    
    Performance:
        - Uses connection pool (10-100x faster than creating connections)
        - Minimal overhead compared to manual connection management
        - Automatic cleanup prevents connection leaks
    
    Best Practices:
        - Use this for single-query operations (most common case)
        - Use context manager (with get_database_connection) for:
          * Multi-query transactions (need atomicity)
          * Complex logic requiring multiple queries
          * Custom cursor configuration
    
    See Also:
        - get_database_connection(): For advanced use cases
        - Context manager pattern: For transactions
    """
    conn = None
    cursor = None
    
    try:
        # Get connection from pool
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query, params)
        
        # Fetch results based on mode
        if fetch_mode == 'all':
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        
        elif fetch_mode == 'one':
            row = cursor.fetchone()
            return dict(row) if row else None
        
        elif fetch_mode == 'value':
            row = cursor.fetchone()
            if row:
                # Get first column value
                return row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]
            return None
        
        elif fetch_mode is None:
            # INSERT/UPDATE/DELETE - commit and return row count
            conn.commit()
            return cursor.rowcount
        
        else:
            raise ValueError(
                f"Invalid fetch_mode: '{fetch_mode}'. "
                f"Valid options: 'all', 'one', 'value', None"
            )
    
    except Exception as e:
        # Rollback on error
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        
        # Re-raise with context
        raise Exception(f"Query execution failed: {e}") from e
    
    finally:
        # GUARANTEED cleanup - always executes
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        
        if conn:
            try:
                conn.close()  # Returns to pool, doesn't actually close
            except Exception:
                pass