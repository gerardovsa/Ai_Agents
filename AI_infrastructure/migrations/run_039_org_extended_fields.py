"""
Run Migration 039: Add Extended Fields to Organisations Table
Adds: description, visibility, allowed_domains, ai_provider, ai_model, ai_max_tokens
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    print("=" * 70)
    print("Migration 039: Add Extended Fields to ai_infrastructure.organisations")
    print("=" * 70)

    steps = [
        ("description column", """
            ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN IF NOT EXISTS description TEXT
        """),
        ("visibility column", """
            ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN IF NOT EXISTS visibility VARCHAR(50) DEFAULT 'private'
        """),
        ("allowed_domains column", """
            ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN IF NOT EXISTS allowed_domains TEXT[]
        """),
        ("ai_provider column", """
            ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50) DEFAULT 'anthropic'
        """),
        ("ai_model column", """
            ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN IF NOT EXISTS ai_model VARCHAR(255) DEFAULT ''
        """),
        ("ai_max_tokens column", """
            ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN IF NOT EXISTS ai_max_tokens INTEGER DEFAULT 8192
        """),
        ("visibility index", """
            CREATE INDEX IF NOT EXISTS idx_organisations_visibility
            ON ai_infrastructure.organisations(visibility)
        """),
    ]

    for name, sql in steps:
        print(f"\n  Adding {name}...", end=" ")
        try:
            execute_query(sql.strip(), fetch_mode=None)
            print("OK")
        except Exception as e:
            err = str(e)
            if "already exists" in err.lower() or "duplicate" in err.lower():
                print("already exists (OK)")
            else:
                print(f"ERROR: {e}")

    # Verify
    print("\n--- Verification ---")
    try:
        cols = execute_query("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_schema = 'ai_infrastructure'
              AND table_name = 'organisations'
              AND column_name IN ('description','visibility','allowed_domains','ai_provider','ai_model','ai_max_tokens')
            ORDER BY column_name
        """, fetch_mode='all')
        if cols:
            for col in cols:
                print(f"  {col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        else:
            print("  WARNING: No extended columns found — migration may have failed")
    except Exception as e:
        print(f"  Verification query failed: {e}")

    print("\n=== Migration 039 complete ===")

if __name__ == '__main__':
    run_migration()
