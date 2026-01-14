"""
Connection Leak Monitor - Real-time leak detection and reporting
Monitors Flask logs for connection leak patterns and reports status

Usage:
    python monitor_connection_leaks.py

Features:
- Real-time log monitoring
- Leak pattern detection
- Emergency rollback success tracking
- Connection pool statistics
- Alert when leaks detected

Created: December 24, 2025
Related Fix: CONNECTION_LEAK_ABORTED_TRANSACTION_FIX_DEC24_2025.md
"""

import os
import sys
import time
from pathlib import Path
from collections import defaultdict
import re

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header():
    """Print monitoring header"""
    print("\n" + "=" * 80)
    print(f"{BLUE}CONNECTION LEAK MONITOR - Real-time Tracking{RESET}")
    print("=" * 80)
    print(f"{GREEN}✅ Monitoring: {RESET}AI_infrastructure/flask_app.log")
    print(f"{GREEN}✅ Looking for: {RESET}Leak patterns, emergency recoveries, pool stats")
    print("=" * 80 + "\n")

def parse_pool_stats(line):
    """Extract connection pool statistics from log line"""
    # Example: INFO:connection_monitor:[_global] Acquired: 83, Returned: 81, Leaked: 2
    match = re.search(r'\[(.*?)\] Acquired: (\d+), Returned: (\d+), Leaked: (\d+)', line)
    if match:
        schema = match.group(1)
        acquired = int(match.group(2))
        returned = int(match.group(3))
        leaked = int(match.group(4))
        return {
            'schema': schema,
            'acquired': acquired,
            'returned': returned,
            'leaked': leaked
        }
    return None

def check_emergency_recovery(line):
    """Check if line shows emergency recovery success"""
    if 'Emergency return succeeded' in line:
        match = re.search(r"for '(.*?)'", line)
        if match:
            return match.group(1)
    return None

def check_leak_failure(line):
    """Check if line shows failed connection return"""
    if 'Failed to return connection to pool' in line:
        if 'Emergency rollback also failed' in line:
            return 'CRITICAL'
        return 'WARNING'
    return None

def format_stats(stats):
    """Format connection stats with color coding"""
    if stats['leaked'] == 0:
        status = f"{GREEN}✅ HEALTHY{RESET}"
    elif stats['leaked'] <= 2:
        status = f"{YELLOW}⚠️  WARNING{RESET}"
    else:
        status = f"{RED}❌ CRITICAL{RESET}"
    
    return (
        f"[{stats['schema']:20s}] "
        f"Acquired: {stats['acquired']:3d} | "
        f"Returned: {stats['returned']:3d} | "
        f"Leaked: {stats['leaked']:2d} {status}"
    )

def monitor_logs():
    """Monitor Flask logs in real-time"""
    log_file = Path(__file__).parent / 'AI_infrastructure' / 'flask_app.log'
    
    if not log_file.exists():
        print(f"{RED}❌ Log file not found: {log_file}{RESET}")
        print(f"{YELLOW}💡 Make sure Flask server is running{RESET}")
        return
    
    print_header()
    
    # Track statistics
    last_stats = {}
    emergency_recoveries = defaultdict(int)
    critical_failures = defaultdict(int)
    
    # Follow log file
    with open(log_file, 'r') as f:
        # Seek to end of file
        f.seek(0, 2)
        
        print(f"{BLUE}📡 Monitoring started... (Press Ctrl+C to stop){RESET}\n")
        
        try:
            while True:
                line = f.readline()
                
                if line:
                    # Check for pool statistics
                    stats = parse_pool_stats(line)
                    if stats:
                        last_stats[stats['schema']] = stats
                        print(f"{BLUE}[STATS]{RESET} {format_stats(stats)}")
                        
                        # Alert on new leaks
                        if stats['leaked'] > 0:
                            print(f"{YELLOW}⚠️  LEAK DETECTED in {stats['schema']}: {stats['leaked']} connections{RESET}")
                    
                    # Check for emergency recovery
                    recovery_schema = check_emergency_recovery(line)
                    if recovery_schema:
                        emergency_recoveries[recovery_schema] += 1
                        print(f"{GREEN}✅ [RECOVERY]{RESET} Emergency rollback succeeded for '{recovery_schema}' (Total: {emergency_recoveries[recovery_schema]})")
                    
                    # Check for critical failures
                    failure_type = check_leak_failure(line)
                    if failure_type:
                        if failure_type == 'CRITICAL':
                            print(f"{RED}❌ [CRITICAL]{RESET} Connection truly leaked - emergency rollback failed!")
                            # Extract schema if possible
                            match = re.search(r"Schema: (.*?)$", line)
                            if match:
                                schema = match.group(1).strip()
                                critical_failures[schema] += 1
                        else:
                            print(f"{YELLOW}⚠️  [WARNING]{RESET} Connection return attempted via emergency path")
                
                else:
                    # No new lines, sleep briefly
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            # Print summary on exit
            print("\n" + "=" * 80)
            print(f"{BLUE}MONITORING SUMMARY{RESET}")
            print("=" * 80)
            
            print(f"\n{GREEN}Final Connection Pool Status:{RESET}")
            for schema, stats in sorted(last_stats.items()):
                print(f"  {format_stats(stats)}")
            
            print(f"\n{GREEN}Emergency Recoveries:{RESET}")
            if emergency_recoveries:
                for schema, count in sorted(emergency_recoveries.items()):
                    print(f"  {schema}: {count} successful recoveries")
            else:
                print(f"  {GREEN}None (no aborted transactions encountered){RESET}")
            
            print(f"\n{RED}Critical Failures:{RESET}")
            if critical_failures:
                for schema, count in sorted(critical_failures.items()):
                    print(f"  {RED}❌ {schema}: {count} permanent leaks{RESET}")
            else:
                print(f"  {GREEN}✅ None (all connections recovered successfully){RESET}")
            
            print("\n" + "=" * 80)
            print(f"{GREEN}✅ Monitoring stopped{RESET}")
            print("=" * 80 + "\n")

if __name__ == '__main__':
    try:
        monitor_logs()
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
