"""
Add missing columns to sessions.threads table

Missing columns:
- workflow_id (should map to workflow_slug semantically, but keep both)
- workflow_name (should map to workflow_title semantically, but keep both)
- synergy_card_name (missing entirely)
"""

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
    
    print(f"Connecting to Supabase...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Add missing columns
    print("\nAdding missing columns to sessions.threads...")
    
    # 1. workflow_id (TEXT, nullable)
    print("  1. Adding workflow_id column...")
    try:
        cursor.execute("ALTER TABLE sessions.threads ADD COLUMN IF NOT EXISTS workflow_id TEXT")
        print("     ✅ workflow_id added")
    except Exception as e:
        print(f"     ⚠️  workflow_id: {e}")
    
    # 2. workflow_name (TEXT, nullable)
    print("  2. Adding workflow_name column...")
    try:
        cursor.execute("ALTER TABLE sessions.threads ADD COLUMN IF NOT EXISTS workflow_name TEXT")
        print("     ✅ workflow_name added")
    except Exception as e:
        print(f"     ⚠️  workflow_name: {e}")
    
    # 3. synergy_card_name (TEXT, nullable)
    print("  3. Adding synergy_card_name column...")
    try:
        cursor.execute("ALTER TABLE sessions.threads ADD COLUMN IF NOT EXISTS synergy_card_name TEXT")
        print("     ✅ synergy_card_name added")
    except Exception as e:
        print(f"     ⚠️  synergy_card_name: {e}")
    
    # Commit changes
    conn.commit()
    
    # Verify changes
    print("\nVerifying schema changes...")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='sessions' AND table_name='threads'
        AND column_name IN ('workflow_id', 'workflow_name', 'synergy_card_name')
        ORDER BY column_name
    """)
    
    cols = cursor.fetchall()
    print(f"\nVerified {len(cols)}/3 columns exist:")
    for col in cols:
        print(f"  ✅ {col[0]} ({col[1]})")
    
    if len(cols) < 3:
        print("\n⚠️  WARNING: Not all columns were added successfully!")
    else:
        print("\n🎉 SUCCESS! All missing columns added to sessions.threads")
    
    conn.close()
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {e}")
    print(traceback.format_exc())
