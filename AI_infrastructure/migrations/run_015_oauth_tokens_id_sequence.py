"""
Migration 015: Fix oauth_tokens.id sequence
Date: March 24, 2026

Issue: oauth_tokens.id was 'integer not null' with no DEFAULT/sequence.
       Every Google/Microsoft OAuth callback INSERT failed → users couldn't log in.

Fix: Attach ai_infrastructure.oauth_tokens_id_seq as DEFAULT on the id column.
Idempotent: Safe to run multiple times.
"""

import sys
import os
from pathlib import Path

# Add project root and AI_infrastructure to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

from dotenv import load_dotenv
env_file = project_root / '.env.master'
if env_file.exists():
    load_dotenv(env_file)

from AI_infrastructure.shared.database_utils import get_database_connection


def run_migration():
    conn = get_database_connection('ai_infrastructure')
    try:
        with conn.cursor() as cursor:

            # Step 1: Create sequence if missing
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_sequences
                        WHERE schemaname = 'ai_infrastructure'
                        AND sequencename = 'oauth_tokens_id_seq'
                    ) THEN
                        CREATE SEQUENCE ai_infrastructure.oauth_tokens_id_seq;
                        RAISE NOTICE 'Created sequence: ai_infrastructure.oauth_tokens_id_seq';
                    ELSE
                        RAISE NOTICE 'Sequence already exists - skipping creation';
                    END IF;
                END
                $$;
            """)

            # Step 2: Attach as DEFAULT on id column
            cursor.execute("""
                ALTER TABLE ai_infrastructure.oauth_tokens
                    ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.oauth_tokens_id_seq');
            """)
            print("✅ Set DEFAULT on oauth_tokens.id")

            # Step 3: Set ownership so sequence drops with table
            cursor.execute("""
                ALTER SEQUENCE ai_infrastructure.oauth_tokens_id_seq
                OWNED BY ai_infrastructure.oauth_tokens.id;
            """)
            print("✅ Set sequence ownership")

            # Step 4: Sync to current max id
            cursor.execute("""
                SELECT setval(
                    'ai_infrastructure.oauth_tokens_id_seq',
                    COALESCE((SELECT MAX(id) FROM ai_infrastructure.oauth_tokens), 0) + 1,
                    false
                );
            """)
            result = cursor.fetchone()
            seq_val = result[0] if result else 'unknown'
            print(f"✅ Sequence synced - next id will be: {seq_val}")

            # Verify
            cursor.execute("""
                SELECT column_default
                FROM information_schema.columns
                WHERE table_schema = 'ai_infrastructure'
                  AND table_name   = 'oauth_tokens'
                  AND column_name  = 'id';
            """)
            row = cursor.fetchone()
            default_val = row[0] if row else None
            if default_val:
                print(f"✅ Verified: oauth_tokens.id DEFAULT = {default_val}")
            else:
                print("❌ WARNING: oauth_tokens.id still has no DEFAULT - check manually")

        conn.commit()
        print("\n✅ Migration 015 complete - OAuth token INSERT will now work for all users")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Migration 015: Fix oauth_tokens.id sequence")
    print("=" * 60)
    run_migration()
