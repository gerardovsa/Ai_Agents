"""
Create scheduled_tasks and automation_executions tables in Supabase

Run this once to create the missing scheduler tables
"""

import sys
import os

# Prevent Flask from starting
os.environ['SKIP_FLASK'] = 'true'

from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment
load_dotenv('.env')

# Connect to Supabase
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

if not SUPABASE_DB_URL:
    print("ERROR: SUPABASE_DB_URL not found in .env")
    exit(1)

print(f"Connecting to Supabase...")
conn = psycopg2.connect(SUPABASE_DB_URL)
cursor = conn.cursor()

print("\nCreating ai_infrastructure schema if not exists...")
cursor.execute("""
    CREATE SCHEMA IF NOT EXISTS ai_infrastructure;
""")
conn.commit()

print("\nCreating scheduled_tasks table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_infrastructure.scheduled_tasks (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        task_type TEXT NOT NULL,
        schedule_type TEXT NOT NULL,
        schedule_value TEXT,
        tool_name TEXT NOT NULL,
        tool_params TEXT,
        is_active BOOLEAN DEFAULT true,
        last_run TIMESTAMP,
        next_run TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
print("  ✅ scheduled_tasks table created")

print("\nCreating automation_executions table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_infrastructure.automation_executions (
        id SERIAL PRIMARY KEY,
        task_id INTEGER REFERENCES ai_infrastructure.scheduled_tasks(id),
        user_id INTEGER NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        status TEXT DEFAULT 'running',
        result TEXT,
        error TEXT
    );
""")
conn.commit()
print("  ✅ automation_executions table created")

print("\nVerifying tables exist...")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'ai_infrastructure' 
    AND table_name IN ('scheduled_tasks', 'automation_executions')
    ORDER BY table_name;
""")

tables = cursor.fetchall()
print(f"\nFound {len(tables)} scheduler tables:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
print("\n✅ COMPLETE: Scheduler tables created in Supabase")
