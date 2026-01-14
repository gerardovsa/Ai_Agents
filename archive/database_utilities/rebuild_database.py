"""
Rebuild Sessions Database
Creates a fresh sessions.db with proper schema
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/sessions.db'
BACKUP_PATH = f'data/sessions_corrupt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

# Rename old file
if os.path.exists(DB_PATH):
    os.rename(DB_PATH, BACKUP_PATH)
    print(f'[OK] Old database backed up to: {BACKUP_PATH}')

# Create new database
print('[INIT] Creating new sessions.db...')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Threads table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_slug TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        title TEXT DEFAULT 'Untitled Thread',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        archived INTEGER DEFAULT 0,
        tags TEXT DEFAULT '[]',
        synergy_card_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Messages table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        response_time REAL,
        FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
    )
''')

# Thread assignments table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS thread_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        thread_slug TEXT NOT NULL,
        location TEXT NOT NULL,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, thread_slug),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert default user (ID 12)
cursor.execute('''
    INSERT OR IGNORE INTO users (id, email, name) 
    VALUES (12, 'default@example.com', 'Default User')
''')

conn.commit()
conn.close()

print('[OK] Database rebuilt successfully')
print('[INFO] All tables created with proper schema')
print('[INFO] Default user created (ID: 12)')
print('[INFO] You can now restart Flask: BISTART')
