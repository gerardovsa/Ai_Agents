#!/bin/bash
# Create threads table in sessions.db on Render
# Run this in Render Shell if sessions.db is missing the threads table

cd /data

echo "Creating threads table in sessions.db..."

python3 << 'PYTHON_SCRIPT'
import sqlite3

conn = sqlite3.connect('/data/sessions.db')
cursor = conn.cursor()

# Create threads table
cursor.execute('''
CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    location TEXT DEFAULT 'prime',
    agent_assignment TEXT,
    model_config TEXT,
    metadata TEXT,
    is_shared INTEGER DEFAULT 0,
    shared_link TEXT,
    shared_at TIMESTAMP
)
''')

# Create device_registry table
cursor.execute('''
CREATE TABLE IF NOT EXISTS device_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL UNIQUE,
    device_name TEXT,
    device_type TEXT,
    user_id INTEGER,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    metadata TEXT
)
''')

conn.commit()
conn.close()

print("[OK] Tables created successfully!")
print("")
print("Verifying...")

conn = sqlite3.connect('/data/sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("Tables in sessions.db:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  - {table[0]} ({count} rows)")

conn.close()

PYTHON_SCRIPT

echo ""
echo "[OK] Done! Threads table created."
echo "Restart your Flask app to pick up the changes."
