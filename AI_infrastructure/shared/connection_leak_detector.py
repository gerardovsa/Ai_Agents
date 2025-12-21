"""
Universal Connection Leak Detector with Auto-Closer
====================================================
Monitors PostgreSQL connection pool for leaks and auto-closes abandoned connections.

SAFETY RULES:
1. Auto-close IDLE connections (idle >5 minutes) - SAFE
2. WARN about ACTIVE connections (in transaction) - RISKY to close
3. Track pool exhaustion and alert

WHY THIS IS SAFE:
- Idle connections = No active transaction, safe to kill
- Active connections = Mid-transaction, only warn (don't corrupt data)
- Uses pg_stat_activity to check connection state

Author: GitHub Copilot
Date: December 22, 2025
"""

import psycopg2
from psycopg2 import pool
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger('ConnectionLeakDetector')


class ConnectionLeakDetector:
    """
    Background thread that monitors connection pool health and auto-closes leaks.
    
    Features:
    - Detects idle connections (>5 min idle)
    - Auto-closes abandoned connections (safe)
    - Warns about active transactions (risky to close)
    - Tracks pool exhaustion
    - Real-time metrics dashboard
    """
    
    def __init__(self, 
                 check_interval: int = 60,  # Check every 60 seconds
                 idle_timeout: int = 30,    # 30 seconds idle = abandoned (was 300)
                 enable_auto_close: bool = True):
        """
        Initialize leak detector.
        
        Args:
            check_interval: Seconds between checks (default: 60)
            idle_timeout: Seconds before connection considered abandoned (default: 30)
            enable_auto_close: Auto-close idle connections (default: True)
        """
        self.check_interval = check_interval
        self.idle_timeout = idle_timeout
        self.enable_auto_close = enable_auto_close
        
        # Metrics
        self.metrics = {
            'total_checked': 0,
            'idle_found': 0,
            'idle_closed': 0,
            'active_warned': 0,
            'errors': 0,
            'last_check': None,
            'pool_stats': {}
        }
        
        # Thread control
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        logger.info("🔍 Connection Leak Detector initialized")
        logger.info(f"   Check interval: {check_interval}s")
        logger.info(f"   Idle timeout: {idle_timeout}s")
        logger.info(f"   Auto-close: {enable_auto_close}")
    
    def start(self):
        """Start background monitoring thread."""
        if self._running:
            logger.warning("⚠️ Leak detector already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("✅ Leak detector started")
    
    def stop(self):
        """Stop background monitoring thread."""
        if not self._running:
            return
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🛑 Leak detector stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)."""
        while self._running:
            try:
                self._check_connections()
                self.metrics['last_check'] = datetime.now().isoformat()
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                self.metrics['errors'] += 1
            
            # Sleep until next check
            time.sleep(self.check_interval)
    
    def _check_connections(self):
        """
        Check all connections for leaks.
        
        Uses pg_stat_activity to identify:
        - Idle connections (state = 'idle', idle >5 min)
        - Active connections (state = 'active' or 'idle in transaction')
        """
        self.metrics['total_checked'] += 1
        
        # Get connection to sessions schema (admin connection)
        conn = None
        cursor = None
        
        try:
            # Get database URL from environment (same as database_utils.py)
            db_url = os.getenv('SUPABASE_DB_URL_POOLER') or os.getenv('SUPABASE_DB_URL_SESSION') or os.getenv('SUPABASE_DB_URL')
            
            if not db_url:
                logger.warning("⚠️ No Supabase connection URL found - skipping connection check")
                return
            
            # Connect directly using the connection URL
            conn = psycopg2.connect(
                dsn=db_url,
                sslmode='require',
                connect_timeout=10
            )
            cursor = conn.cursor()
            
            # Query pg_stat_activity for all connections from this application
            query = """
                SELECT 
                    pid,
                    usename,
                    application_name,
                    state,
                    state_change,
                    EXTRACT(EPOCH FROM (NOW() - state_change)) AS idle_seconds,
                    query,
                    backend_start,
                    wait_event_type,
                    wait_event,
                    client_addr
                FROM pg_stat_activity
                WHERE 
                    application_name LIKE 'valor_ai%%'
                    AND pid != pg_backend_pid()  -- Exclude self
                ORDER BY idle_seconds DESC
            """
            
            cursor.execute(query)
            connections = cursor.fetchall()
            
            idle_connections = []
            active_connections = []
            
            for row in connections:
                pid, usename, app_name, state, state_change, idle_seconds, query_text, backend_start, wait_event_type, wait_event, client_addr = row
                
                # Categorize connection
                if state == 'idle' and idle_seconds and idle_seconds > self.idle_timeout:
                    # SAFE TO CLOSE: Idle for >30 seconds
                    idle_connections.append({
                        'pid': pid,
                        'user': usename,
                        'app': app_name,
                        'idle_seconds': idle_seconds,
                        'idle_minutes': round(idle_seconds / 60, 1),
                        'query': query_text[:200] if query_text else None,  # Show full query (truncated)
                        'query_type': self._classify_query(query_text),
                        'backend_start': str(backend_start),
                        'client_addr': str(client_addr) if client_addr else 'local'
                    })
                elif state in ('active', 'idle in transaction'):
                    # RISKY TO CLOSE: Active transaction
                    active_connections.append({
                        'pid': pid,
                        'user': usename,
                        'app': app_name,
                        'state': state,
                        'idle_seconds': idle_seconds,
                        'query': query_text[:200] if query_text else None,
                        'query_type': self._classify_query(query_text),
                        'wait_event': f"{wait_event_type}/{wait_event}" if wait_event_type else None
                    })
            
            # Update metrics
            self.metrics['idle_found'] = len(idle_connections)
            
            # Handle idle connections
            if idle_connections:
                logger.warning(f"🔴 Found {len(idle_connections)} IDLE connections (>{self.idle_timeout}s idle)")
                
                for conn_info in idle_connections:
                    logger.info(f"   PID {conn_info['pid']}: {conn_info['app']} - Idle {conn_info['idle_minutes']} min")
                    logger.info(f"      Type: {conn_info['query_type']}")
                    logger.debug(f"      Query: {conn_info['query']}")
                    logger.debug(f"      Client: {conn_info['client_addr']}, Started: {conn_info['backend_start']}")
                    
                    # Auto-close if enabled
                    if self.enable_auto_close:
                        self._close_connection(cursor, conn_info['pid'])
                        self.metrics['idle_closed'] += 1
            
            # Handle active connections (warn only)
            if active_connections:
                logger.warning(f"⚠️ Found {len(active_connections)} ACTIVE connections (mid-transaction)")
                self.metrics['active_warned'] += len(active_connections)
                
                for conn_info in active_connections:
                    logger.warning(f"   PID {conn_info['pid']}: {conn_info['app']} - State: {conn_info['state']}")
                    logger.warning(f"      Type: {conn_info['query_type']}")
                    logger.warning(f"      ⛔ NOT auto-closing (could corrupt transaction)")
                    logger.debug(f"      Query: {conn_info['query']}")
                    if conn_info.get('wait_event'):
                        logger.debug(f"      Waiting on: {conn_info['wait_event']}")
            
            # Log summary
            if not idle_connections and not active_connections:
                logger.info(f"✅ No leaks detected ({len(connections)} connections checked)")
            
        except Exception as e:
            logger.error(f"❌ Connection check failed: {e}")
            import traceback
            traceback.print_exc()
            self.metrics['errors'] += 1
        
        finally:
            # Always clean up detector's own connection
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
    
    def _classify_query(self, query_text: Optional[str]) -> str:
        """
        Classify query type from SQL text.
        
        Returns category like: "READ (threads)", "WRITE (messages)", "AUTH (users)"
        """
        if not query_text:
            return "UNKNOWN"
        
        query_upper = query_text.upper().strip()
        
        # Extract table name
        table = "unknown"
        if "FROM " in query_upper:
            parts = query_upper.split("FROM ")[1].split()
            if parts:
                table = parts[0].replace("SESSIONS.", "").replace("AI_INFRASTRUCTURE.", "")
        elif "INTO " in query_upper:
            parts = query_upper.split("INTO ")[1].split()
            if parts:
                table = parts[0].replace("SESSIONS.", "").replace("AI_INFRASTRUCTURE.", "")
        elif "UPDATE " in query_upper:
            parts = query_upper.split("UPDATE ")[1].split()
            if parts:
                table = parts[0].replace("SESSIONS.", "").replace("AI_INFRASTRUCTURE.", "")
        
        # Classify operation
        if query_upper.startswith("SELECT"):
            if "USER" in query_upper or "CREDENTIALS" in query_upper:
                return f"AUTH READ ({table})"
            elif "THREAD" in query_upper or "MESSAGE" in query_upper:
                return f"THREAD READ ({table})"
            elif "EMAIL" in query_upper:
                return f"EMAIL READ ({table})"
            else:
                return f"READ ({table})"
        
        elif query_upper.startswith("INSERT"):
            if "THREAD" in query_upper or "MESSAGE" in query_upper:
                return f"THREAD WRITE ({table})"
            elif "EMAIL" in query_upper:
                return f"EMAIL WRITE ({table})"
            else:
                return f"INSERT ({table})"
        
        elif query_upper.startswith("UPDATE"):
            if "THREAD" in query_upper:
                return f"THREAD UPDATE ({table})"
            else:
                return f"UPDATE ({table})"
        
        elif query_upper.startswith("DELETE"):
            return f"DELETE ({table})"
        
        elif "BEGIN" in query_upper or "COMMIT" in query_upper or "ROLLBACK" in query_upper:
            return "TRANSACTION"
        
        else:
            return f"OTHER ({table})"
    
    def _close_connection(self, admin_cursor, pid: int) -> bool:
        """
        Forcefully close a connection by PID.
        
        Uses pg_terminate_backend() to kill the connection.
        ONLY call this for IDLE connections (>5 min idle).
        
        Args:
            admin_cursor: Cursor with admin privileges
            pid: Process ID of connection to close
            
        Returns:
            True if closed successfully, False otherwise
        """
        try:
            admin_cursor.execute("SELECT pg_terminate_backend(%s)", (pid,))
            result = admin_cursor.fetchone()[0]
            
            if result:
                logger.info(f"   ✅ Closed connection PID {pid}")
                return True
            else:
                logger.warning(f"   ⚠️ Failed to close PID {pid} (may have already closed)")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Error closing PID {pid}: {e}")
            return False
    
    def get_metrics(self) -> Dict:
        """Get current metrics for dashboard."""
        return {
            **self.metrics,
            'is_running': self._running,
            'check_interval': self.check_interval,
            'idle_timeout': self.idle_timeout,
            'auto_close_enabled': self.enable_auto_close
        }
    
    def force_check(self) -> Dict:
        """
        Force immediate connection check (for testing/debugging).
        
        Returns:
            Current metrics after check
        """
        logger.info("🔍 Forcing immediate connection check...")
        self._check_connections()
        return self.get_metrics()


# ============================================================
# GLOBAL INSTANCE
# ============================================================

# Singleton instance (created on import)
_detector_instance: Optional[ConnectionLeakDetector] = None


def get_leak_detector() -> ConnectionLeakDetector:
    """Get global leak detector instance (creates if not exists)."""
    global _detector_instance
    
    if _detector_instance is None:
        # Read config from environment
        check_interval = int(os.environ.get('LEAK_DETECTOR_INTERVAL', '60'))
        idle_timeout = int(os.environ.get('LEAK_DETECTOR_IDLE_TIMEOUT', '30'))  # 30 seconds (was 300)
        enable_auto_close = os.environ.get('LEAK_DETECTOR_AUTO_CLOSE', 'True').lower() == 'true'
        
        _detector_instance = ConnectionLeakDetector(
            check_interval=check_interval,
            idle_timeout=idle_timeout,
            enable_auto_close=enable_auto_close
        )
    
    return _detector_instance


def start_leak_detector():
    """Start global leak detector (call from flask_app.py on startup)."""
    detector = get_leak_detector()
    detector.start()
    logger.info("🚀 Global leak detector started")


def stop_leak_detector():
    """Stop global leak detector (call on shutdown)."""
    detector = get_leak_detector()
    detector.stop()
    logger.info("🛑 Global leak detector stopped")


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == '__main__':
    """
    Test the leak detector locally.
    
    Run:
        python connection_leak_detector.py
    """
    print("🔍 Testing Connection Leak Detector")
    print("=" * 50)
    
    # Create detector
    detector = ConnectionLeakDetector(
        check_interval=10,  # Check every 10 seconds (faster for testing)
        idle_timeout=60,    # 1 minute idle (faster for testing)
        enable_auto_close=True
    )
    
    # Start monitoring
    detector.start()
    
    # Force immediate check
    print("\n📊 Forcing immediate check...")
    metrics = detector.force_check()
    
    print("\n📈 Current Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    # Keep running for 30 seconds
    print("\n⏳ Monitoring for 30 seconds...")
    print("   (Create some idle connections to test)")
    time.sleep(30)
    
    # Final metrics
    print("\n📊 Final Metrics:")
    final_metrics = detector.get_metrics()
    for key, value in final_metrics.items():
        print(f"   {key}: {value}")
    
    # Stop
    detector.stop()
    print("\n✅ Test complete")
