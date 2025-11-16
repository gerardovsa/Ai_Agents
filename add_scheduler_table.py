import os
import psycopg2

SUPABASE_DB_URL = "postgresql://postgres:inhouseprint@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres"

conn = psycopg2.connect(SUPABASE_DB_URL)
cur = conn.cursor()

cur.execute('CREATE SCHEMA IF NOT EXISTS ai_infrastructure')
conn.commit()

cur.execute('''
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
)
''')
conn.commit()
print('✅ scheduled_tasks created')

cur.execute('''
CREATE TABLE IF NOT EXISTS ai_infrastructure.automation_executions (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES ai_infrastructure.scheduled_tasks(id),
    user_id INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running',
    result TEXT,
    error TEXT
)
''')
conn.commit()
print('✅ automation_executions created')

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'ai_infrastructure' AND table_name IN ('scheduled_tasks', 'automation_executions')")
print(f'✅ Found: {[r[0] for r in cur.fetchall()]}')

conn.close()
