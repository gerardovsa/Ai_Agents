"""Check if authenticated role has SELECT on oauth_tokens"""
from shared.database_utils import execute_query

# Check grants on oauth_tokens
grants = execute_query(
    """
    SELECT grantee, privilege_type, is_grantable
    FROM information_schema.role_table_grants
    WHERE table_schema = 'ai_infrastructure'
    AND table_name = 'oauth_tokens'
    ORDER BY grantee, privilege_type
    """,
    fetch_mode='all'
)
print('oauth_tokens grants:')
for g in grants:
    print(f"  {g['grantee']}: {g['privilege_type']}")

# Direct connection (superuser) test - simulate what authenticated role would get
import os
import psycopg2
try:
    from dotenv import load_dotenv
    load_dotenv('c:\\Users\\gpoli\\GIT\\AI_Agents_V11\\AI_agents\\.env')
except: pass

db_url = os.environ.get('SUPABASE_DB_URL_SESSION') or os.environ.get('SUPABASE_DB_URL')
if db_url:
    db_url = db_url.replace(':6543/', ':5432/')
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        # Try to set role and query
        cur.execute("SET ROLE authenticated")
        cur.execute("SELECT user_id FROM ai_infrastructure.oauth_tokens WHERE user_id = 12 LIMIT 1")
        row = cur.fetchone()
        print(f'\nAuthenticated role can SELECT oauth_tokens: {row}')
    except Exception as e:
        print(f'\nAuthenticated role SELECT oauth_tokens FAILED: {e}')
    finally:
        cur.execute("RESET ROLE")
        cur.close()
        conn.close()
