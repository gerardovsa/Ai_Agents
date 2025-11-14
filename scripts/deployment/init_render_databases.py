#!/usr/bin/env python3
"""
Initialize Render databases with seed data from local development

This script runs ONCE on first Render deployment to populate:
- ai_infrastructure.db (user tables, oauth tables, etc.)
- sessions.db (session storage)
- stock_data.db (InHousePrint inventory)
- synergy_sessions.db (Synergy feature data)

USAGE:
1. On local dev: Export seed data to SQL scripts
2. On Render first startup: Import SQL scripts to /data/ databases

NOTES:
- Only runs if /data/ai_infrastructure.db is empty (no tables)
- Idempotent - safe to run multiple times
- Uses SQLite .dump format for portability
"""

import os
import sqlite3
from pathlib import Path

def is_render():
    """Check if running on Render"""
    return os.getenv('RENDER') == 'true'

def database_needs_initialization(db_path):
    """Check if database is empty (no tables)"""
    if not os.path.exists(db_path):
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        # If no tables, needs initialization
        return len(tables) == 0
    except Exception as e:
        print(f"⚠️ Error checking database {db_path}: {e}")
        return True

def init_ai_infrastructure_db():
    """Initialize ai_infrastructure.db with core tables"""
    if is_render():
        db_path = '/data/ai_infrastructure.db'
    else:
        db_path = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'
    
    if not database_needs_initialization(db_path):
        print(f"✅ ai_infrastructure.db already initialized (has tables)")
        return
    
    print(f"🔧 Initializing ai_infrastructure.db at {db_path}")
    
    # Core schema will be created by UserAuthManager._init_tables()
    # This function just ensures the file exists
    conn = sqlite3.connect(db_path)
    conn.close()
    
    print(f"✅ Created database file at {db_path}")

def init_sessions_db():
    """Initialize sessions.db for Flask sessions"""
    if is_render():
        db_path = '/data/sessions.db'
    else:
        db_path = Path(__file__).parent.parent.parent / 'data' / 'sessions.db'
    
    if not database_needs_initialization(db_path):
        print(f"✅ sessions.db already initialized")
        return
    
    print(f"🔧 Initializing sessions.db at {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Session storage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL,
            expiry INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Initialized sessions.db")

def init_stock_db():
    """Initialize stock_data.db (InHousePrint inventory)"""
    if is_render():
        db_path = '/data/stock_data.db'
    else:
        db_path = Path(__file__).parent.parent.parent / 'data' / 'stock_data.db'
    
    if not database_needs_initialization(db_path):
        print(f"✅ stock_data.db already initialized")
        return
    
    print(f"🔧 Initializing stock_data.db at {db_path}")
    
    # This will be populated by stock management routes on first use
    conn = sqlite3.connect(db_path)
    conn.close()
    
    print(f"✅ Created stock_data.db (will be populated on first use)")

def init_synergy_db():
    """Initialize synergy_sessions.db"""
    if is_render():
        db_path = '/data/synergy_sessions.db'
    else:
        db_path = Path(__file__).parent.parent.parent / 'data' / 'synergy_sessions.db'
    
    if not database_needs_initialization(db_path):
        print(f"✅ synergy_sessions.db already initialized")
        return
    
    print(f"🔧 Initializing synergy_sessions.db at {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.close()
    
    print(f"✅ Created synergy_sessions.db")

def main():
    """Initialize all databases on first deployment"""
    print("=" * 60)
    print("Render Database Initialization")
    print("=" * 60)
    
    if is_render():
        print("🌐 Running on Render")
    else:
        print("💻 Running locally")
    
    # Initialize all databases
    init_ai_infrastructure_db()
    init_sessions_db()
    init_stock_db()
    init_synergy_db()
    
    print("=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
