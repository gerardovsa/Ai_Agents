"""
Database Safety Utilities
Adds error handling and corruption prevention for SQLite operations
"""

import sqlite3
import os
import shutil
from datetime import datetime
from functools import wraps
from pathlib import Path

def check_database_health(db_path):
    """Check if database is healthy before operations"""
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check')
        result = cursor.fetchone()
        conn.close()
        return result[0] == 'ok'
    except Exception as e:
        print(f'[DB HEALTH CHECK] Failed: {e}')
        return False

def safe_db_operation(func):
    """Decorator to wrap database operations with safety checks"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract db_path from args or kwargs
        db_path = None
        if args and isinstance(args[0], str) and args[0].endswith('.db'):
            db_path = args[0]
        elif 'db_path' in kwargs:
            db_path = kwargs['db_path']
        
        # Health check before operation
        if db_path and os.path.exists(db_path):
            if not check_database_health(db_path):
                raise sqlite3.DatabaseError(f"Database {db_path} failed health check")
        
        try:
            # Execute the wrapped function
            result = func(*args, **kwargs)
            return result
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                print(f'[DB ERROR] Database locked, retrying...')
                # Retry once after brief delay
                import time
                time.sleep(0.5)
                return func(*args, **kwargs)
            raise
        except sqlite3.DatabaseError as e:
            if 'malformed' in str(e) or 'corrupt' in str(e):
                print(f'[DB ERROR] Database corruption detected: {e}')
                # Create emergency backup
                emergency_backup(db_path)
                raise
            raise
    
    return wrapper

def emergency_backup(db_path):
    """Create emergency backup when corruption detected"""
    try:
        backup_dir = Path(db_path).parent / 'emergency_backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'{Path(db_path).stem}_emergency_{timestamp}.db'
        
        shutil.copy2(db_path, backup_path)
        print(f'[EMERGENCY BACKUP] Created: {backup_path}')
        return str(backup_path)
    except Exception as e:
        print(f'[EMERGENCY BACKUP] Failed: {e}')
        return None

def optimize_database(db_path):
    """Optimize database to prevent corruption"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Set optimized pragmas
        # Skip WAL on Render - ephemeral filesystem doesn't support it
        is_render = os.getenv('RENDER') == 'true' or 'onrender.com' in os.getenv('RENDER_EXTERNAL_URL', '')
        if not is_render:
            try:
                cursor.execute('PRAGMA journal_mode = WAL')  # Write-Ahead Logging
            except sqlite3.OperationalError:
                cursor.execute('PRAGMA journal_mode = DELETE')
        else:
            cursor.execute('PRAGMA journal_mode = DELETE')
        
        cursor.execute('PRAGMA synchronous = NORMAL')  # Faster but safe
        cursor.execute('PRAGMA temp_store = MEMORY')  # Use memory for temp
        
        # Skip mmap on Render
        if not is_render:
            cursor.execute('PRAGMA mmap_size = 30000000000')  # Memory-mapped I/O
        
        cursor.execute('PRAGMA page_size = 4096')  # Optimal page size
        
        # Vacuum to reclaim space and reorganize
        cursor.execute('VACUUM')
        
        # Analyze for query optimization
        cursor.execute('ANALYZE')
        
        conn.commit()
        conn.close()
        
        print(f'[DB OPTIMIZE] Successfully optimized: {db_path}')
        return True
    except Exception as e:
        print(f'[DB OPTIMIZE] Failed: {e}')
        return False

def repair_database(db_path):
    """Attempt to repair a corrupted database"""
    try:
        temp_path = f'{db_path}.temp'
        
        # Try to dump and restore
        old_conn = sqlite3.connect(db_path)
        new_conn = sqlite3.connect(temp_path)
        
        for line in old_conn.iterdump():
            try:
                new_conn.execute(line)
            except:
                pass  # Skip errors
        
        new_conn.commit()
        old_conn.close()
        new_conn.close()
        
        # Replace original with repaired
        backup_path = f'{db_path}.pre_repair'
        shutil.move(db_path, backup_path)
        shutil.move(temp_path, db_path)
        
        print(f'[DB REPAIR] Successfully repaired: {db_path}')
        print(f'[DB REPAIR] Original backed up to: {backup_path}')
        return True
    except Exception as e:
        print(f'[DB REPAIR] Failed: {e}')
        return False

class SafeConnection:
    """Context manager for safe database connections"""
    
    def __init__(self, db_path, timeout=10.0):
        self.db_path = db_path
        self.timeout = timeout
        self.conn = None
    
    def __enter__(self):
        # Health check before connecting
        if not check_database_health(self.db_path):
            raise sqlite3.DatabaseError(f"Database health check failed: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        
        # Skip WAL on Render - ephemeral filesystem doesn't support it
        is_render = os.getenv('RENDER') == 'true' or 'onrender.com' in os.getenv('RENDER_EXTERNAL_URL', '')
        if not is_render:
            try:
                self.conn.execute('PRAGMA journal_mode = WAL')
            except sqlite3.OperationalError:
                self.conn.execute('PRAGMA journal_mode = DELETE')
        else:
            self.conn.execute('PRAGMA journal_mode = DELETE')
        
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                # If database error, create emergency backup
                if isinstance(exc_val, sqlite3.DatabaseError):
                    emergency_backup(self.db_path)
            self.conn.close()
        return False
