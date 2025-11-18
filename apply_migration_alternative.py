"""
Apply Supabase Migration via SQL API (Alternative Method)
Uses Supabase REST API with service role key instead of psycopg2
"""

import requests
import os
from pathlib import Path

# Supabase credentials from test output
SUPABASE_URL = "https://ryoicrdifiqhqpsnjmdo.supabase.co"
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_SERVICE_KEY:
    print("❌ SUPABASE_SERVICE_KEY not set in environment")
    print("   Get it from: Supabase Dashboard → Project Settings → API → service_role key")
    exit(1)

# Read migration SQL
root_dir = Path(__file__).parent
migration_file = root_dir / 'supabase_migrations' / '005_automation_workflow_tables.sql'

if not migration_file.exists():
    print(f"❌ Migration file not found: {migration_file}")
    exit(1)

print(f"📄 Reading migration: {migration_file.name}")
sql = migration_file.read_text(encoding='utf-8')

# Execute via Supabase SQL API
print("🔌 Executing migration via Supabase REST API...")

headers = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# Note: Supabase doesn't have direct SQL execution endpoint via REST
# We need to use the database connection or Supabase CLI

print("""
⚠️  Alternative approach needed:

Option 1 - Supabase CLI:
  1. Install: npm install -g supabase
  2. Login: supabase login
  3. Link project: supabase link --project-ref ryoicrdifiqhqpsnjmdo
  4. Run migration: supabase db push

Option 2 - SQL Editor in Dashboard:
  1. Go to: https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo/sql
  2. Paste contents of: supabase_migrations/005_automation_workflow_tables.sql
  3. Click "Run"

Option 3 - Get correct database connection:
  1. Go to: Supabase Dashboard → Project Settings → Database
  2. Copy "Connection string" (Direct connection mode)
  3. Use that in SUPABASE_DB_URL
""")
