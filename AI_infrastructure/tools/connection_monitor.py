"""
Database Connection Pool Monitor
==================================

Background monitoring service that:
1. Tracks real-time connection pool statistics
2. Detects connection leaks (acquired > returned)
3. Logs warnings when thresholds exceeded
4. Runs periodic connection audits
5. Records events to monitoring log file

Usage:
    # Start monitoring thread (called from flask_app.py)
    from tools.connection_monitor import start_connection_monitor
    monitor_thread = start_connection_monitor()

    # Stop monitoring (on shutdown)
    monitor_thread.stop()

Configuration:
    CHECK_INTERVAL = 60        # Check every 60 seconds
    AUDIT_INTERVAL = 1800      # Full audit every 30 minutes
    LEAK_THRESHOLD = 5         # Alert if >5 leaked connections
    LOG_FILE = 'logs/connection_monitor.log'
"""

import os
import sys
import io

# Fix Windows console encoding for emoji support in logging
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from shared.database_utils import get_pool_stats, get_all_pool_stats
except ImportError:
    # Fallback if running standalone
    def get_pool_stats():
        return {}
    def get_all_pool_stats():
        return {}


# ================================================================
# CONFIGURATION
# ================================================================

CHECK_INTERVAL = 60          # Check pool stats every 60 seconds
AUDIT_INTERVAL = 1800        # Run full audit every 30 minutes (1800s)
LEAK_THRESHOLD = 5           # Alert if leaked connections > 5
WARNING_THRESHOLD = 3        # Warning if leaked connections > 3
LOG_FILE = 'logs/connection_monitor.log'

# Ensure logs directory exists
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Setup logger
logger = logging.getLogger('connection_monitor')
logger.setLevel(logging.INFO)

# File handler (with UTF-8 encoding for emoji support)
log_path = LOG_DIR / 'connection_monitor.log'
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler (for debugging)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Only warnings/errors to console
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


# ================================================================
# MONITORING THREAD
# ================================================================

class ConnectionMonitor(threading.Thread):
    """Background thread that monitors database connection pool."""
    
    def __init__(self):
        super().__init__(daemon=True)
        self.running = False
        self.last_audit_time = 0
        self.leak_count_history = []  # Track leak counts over time
        
    def run(self):
        """Main monitoring loop."""
        self.running = True
        logger.info("="*70)
        logger.info("CONNECTION MONITOR STARTED")
        logger.info(f"Check interval: {CHECK_INTERVAL}s")
        logger.info(f"Audit interval: {AUDIT_INTERVAL}s")
        logger.info(f"Leak threshold: {LEAK_THRESHOLD}")
        logger.info("="*70)
        
        while self.running:
            try:
                # Check pool statistics
                self.check_pool_stats()
                
                # Run periodic audit
                current_time = time.time()
                if current_time - self.last_audit_time >= AUDIT_INTERVAL:
                    self.run_audit()
                    self.last_audit_time = current_time
                
                # Sleep until next check
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(CHECK_INTERVAL)  # Continue monitoring
    
    def check_pool_stats(self):
        """Check current pool statistics and detect leaks."""
        try:
            all_stats = get_all_pool_stats()
            
            if not all_stats:
                # No pools active yet
                return
            
            # ✅ FIX: Use ONLY the '_global' entry for totals.
            # get_all_pool_stats() returns the same global _pool_stats dict for every
            # schema key (_global, ai_infrastructure, sessions, ...).  Summing across
            # all keys multiplies the true count by the number of schemas, producing
            # wildly inflated "leaked" numbers (e.g. 2 real leaks → 6 reported).
            global_stats = all_stats.get('_global', {})
            total_acquired = global_stats.get('connections_acquired', 0)
            total_returned = global_stats.get('connections_returned', 0)
            total_leaked = total_acquired - total_returned
            
            # Log per-schema breakdown (informational only, same underlying counter)
            if total_leaked > 0:
                for schema, stats in all_stats.items():
                    acquired = stats.get('connections_acquired', 0)
                    returned = stats.get('connections_returned', 0)
                    leaked = acquired - returned
                    if leaked > 0:
                        logger.info(
                            f"[{schema}] Acquired: {acquired}, "
                            f"Returned: {returned}, "
                            f"Leaked: {leaked} (shares global counter)"
                        )
            
            # Track leak history
            self.leak_count_history.append({
                'timestamp': datetime.now().isoformat(),
                'leaked': total_leaked
            })
            
            # Keep only last 100 entries
            if len(self.leak_count_history) > 100:
                self.leak_count_history.pop(0)
            
            # Alert on thresholds
            if total_leaked >= LEAK_THRESHOLD:
                logger.error(
                    f"🚨 CRITICAL: {total_leaked} connections leaked! "
                    f"(Acquired: {total_acquired}, Returned: {total_returned})"
                )
                self.log_leak_details(all_stats)
                
            elif total_leaked >= WARNING_THRESHOLD:
                logger.warning(
                    f"⚠️  WARNING: {total_leaked} connections leaked "
                    f"(Acquired: {total_acquired}, Returned: {total_returned})"
                )
            
            elif total_leaked > 0:
                logger.info(
                    f"[INFO] Minor leak: {total_leaked} connections "
                    f"(Acquired: {total_acquired}, Returned: {total_returned})"
                )
            else:
                # All good - log summary every 10 checks (10 minutes)
                if len(self.leak_count_history) % 10 == 0:
                    logger.info(
                        f"[OK] Pool healthy: {total_acquired} acquired, "
                        f"{total_returned} returned (0 leaks)"
                    )
        
        except Exception as e:
            logger.error(f"Error checking pool stats: {e}")
    
    def log_leak_details(self, all_stats):
        """Log detailed information about leaked connections."""
        logger.error("-" * 70)
        logger.error("LEAK DETAILS:")
        
        for schema, stats in all_stats.items():
            acquired = stats.get('connections_acquired', 0)
            returned = stats.get('connections_returned', 0)
            leaked = acquired - returned
            
            if leaked > 0:
                logger.error(f"  Schema: {schema}")
                logger.error(f"    Acquired:  {acquired}")
                logger.error(f"    Returned:  {returned}")
                logger.error(f"    Leaked:    {leaked}")
                logger.error(f"    Pool hits: {stats.get('pool_hits', 0)}")
                logger.error(f"    Pool miss: {stats.get('pool_misses', 0)}")
        
        logger.error("-" * 70)
        logger.error("RECOMMENDATION:")
        logger.error("  1. Check Flask logs for connection timeout warnings")
        logger.error("  2. Review recent route changes for missing conn.close()")
        logger.error("  3. Run: python AI_infrastructure/tools/audit_connection_leaks.py")
        logger.error("  4. Restart Flask to reset connection pools")
        logger.error("-" * 70)
    
    def run_audit(self):
        """Run full connection leak audit."""
        logger.info("="*70)
        logger.info("RUNNING PERIODIC CONNECTION AUDIT")
        logger.info("="*70)
        
        try:
            # Path to audit script
            audit_script = Path(__file__).parent / 'audit_connection_leaks.py'
            
            if not audit_script.exists():
                logger.error(f"Audit script not found: {audit_script}")
                return
            
            # Run audit
            result = subprocess.run(
                [sys.executable, str(audit_script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for summary
            output = result.stdout
            
            if 'TOTAL:' in output:
                # Extract total leaks
                import re
                match = re.search(r'TOTAL:\s*(\d+)\s*potential leaks', output)
                if match:
                    total_leaks = int(match.group(1))
                    
                    if total_leaks > 0:
                        logger.warning(
                            f"⚠️  Audit found {total_leaks} potential leak locations "
                            f"(may include false positives)"
                        )
                        
                        # Log files with most leaks
                        file_matches = re.findall(
                            r'\[FILE\]\s+(\S+)\s+\((\d+)\s+potential',
                            output
                        )
                        
                        if file_matches:
                            logger.info("Top files with potential leaks:")
                            for filename, count in sorted(
                                file_matches, 
                                key=lambda x: int(x[1]), 
                                reverse=True
                            )[:5]:
                                logger.info(f"  - {filename}: {count} locations")
                    else:
                        logger.info("✅ Audit clean: No potential leaks found")
            
            logger.info("="*70)
        
        except subprocess.TimeoutExpired:
            logger.error("Audit timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Audit error: {e}")
    
    def stop(self):
        """Stop the monitoring thread."""
        logger.info("="*70)
        logger.info("CONNECTION MONITOR STOPPING")
        logger.info("="*70)
        self.running = False
    
    def get_status(self):
        """Get current monitoring status."""
        return {
            'running': self.running,
            'leak_history': self.leak_count_history[-10:],  # Last 10 entries
            'last_audit': datetime.fromtimestamp(self.last_audit_time).isoformat() 
                         if self.last_audit_time > 0 else None
        }


# ================================================================
# PUBLIC API
# ================================================================

_monitor_instance = None

def start_connection_monitor():
    """
    Start the connection monitoring thread.
    
    Returns:
        ConnectionMonitor: The monitoring thread instance
    """
    global _monitor_instance
    
    if _monitor_instance is not None and _monitor_instance.is_alive():
        logger.warning("Connection monitor already running")
        return _monitor_instance
    
    _monitor_instance = ConnectionMonitor()
    _monitor_instance.start()
    
    return _monitor_instance


def stop_connection_monitor():
    """Stop the connection monitoring thread."""
    global _monitor_instance
    
    if _monitor_instance is not None:
        _monitor_instance.stop()
        _monitor_instance.join(timeout=5)
        _monitor_instance = None


def get_monitor_status():
    """
    Get current monitoring status.
    
    Returns:
        dict: Status information including leak history
    """
    global _monitor_instance
    
    if _monitor_instance is None or not _monitor_instance.is_alive():
        return {
            'running': False,
            'message': 'Monitor not started'
        }
    
    return _monitor_instance.get_status()


# ================================================================
# STANDALONE EXECUTION
# ================================================================

if __name__ == '__main__':
    print("Starting connection monitor in standalone mode...")
    print(f"Log file: {log_path}")
    print("Press Ctrl+C to stop")
    
    try:
        monitor = start_connection_monitor()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        stop_connection_monitor()
        print("Monitor stopped")
