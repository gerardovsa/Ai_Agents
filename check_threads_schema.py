"""Check current threads table schema in Supabase"""

import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).parent
env_file = root_dir / '.env.master'
load_dotenv(env_file)

try:
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not found in environment")
        exit(1)
    
    print(f"Connecting to: {db_url[:50]}...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema='sessions' AND table_name='threads'
        ORDER BY ordinal_position
    """)
    
    cols = cur.fetchall()
    
    print("\n" + "="*80)
    print("THREADS TABLE SCHEMA (sessions.threads)")
    print("="*80)
    
    for col in cols:
        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
        print(f"  {col[0]:30} {col[1]:20} {nullable}")
    
    print(f"\nTotal columns: {len(cols)}")
    print("="*80 + "\n")
    
    # Check for missing columns
    expected_cols = ['workflow_id', 'workflow_name', 'synergy_card_id', 'synergy_card_name']
    existing_col_names = [c[0] for c in cols]
    
    missing = [col for col in expected_cols if col not in existing_col_names]
    
    if missing:
        print("MISSING COLUMNS:")
        for col in missing:
            print(f"  - {col}")
    else:
        print("All expected columns present")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
