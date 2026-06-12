"""Check org schema status in both databases."""
import psycopg2

import os
DATABASES = {
    "InHouse": os.environ.get("INHOUSE_DB_URL", ""),
    "ValorAI": os.environ.get("VALORAI_SUPABASE_DB_URL", os.environ.get("SUPABASE_DB_URL", "")),
}

CHECKS = [
    ("organisations table",          "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='organisations'"),
    ("organisation_platform_creds",  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='organisation_platform_credentials'"),
    ("credential_access_log",        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='credential_access_log'"),
    ("org_invitations table",        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='org_invitations'"),
    ("users.organisation_id col",    "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='users' AND column_name='organisation_id'"),
    ("users.org_role col",           "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='users' AND column_name='org_role'"),
    ("session_members table",        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='synergy_sessions' AND table_name='session_members'"),
    ("synergy_sessions.visibility",  "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='synergy_sessions' AND table_name='synergy_sessions' AND column_name='visibility'"),
    ("orgs seeded",                  "SELECT COUNT(*) FROM ai_infrastructure.organisations"),
    ("users with org",               "SELECT COUNT(*) FROM ai_infrastructure.users WHERE organisation_id IS NOT NULL"),
    ("org credentials",              "SELECT COUNT(*) FROM ai_infrastructure.organisation_platform_credentials"),
    ("pending invitations",          "SELECT COUNT(*) FROM ai_infrastructure.org_invitations"),
]

for db_name, db_url in DATABASES.items():
    print(f"\n{'='*60}")
    print(f"  {db_name}")
    print("=" * 60)
    try:
        conn = psycopg2.connect(db_url, connect_timeout=10)
        cur = conn.cursor()
        for label, query in CHECKS:
            try:
                cur.execute(query)
                val = cur.fetchone()[0]
                status = "OK " if val else "---"
                print(f"  [{status}] {label}: {val}")
            except Exception as e:
                print(f"  [ERR] {label}: {e}")
        conn.close()
    except Exception as e:
        print(f"  CONNECTION FAILED: {e}")

print("\nDone.")
