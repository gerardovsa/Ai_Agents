"""Temporary diagnostic script to check DB state for org system analysis."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_infrastructure.shared.database_utils import execute_query

print("=== ORG PLATFORM CREDENTIALS ===")
creds = execute_query(
    "SELECT id, organisation_id, platform, display_name, environment, is_active FROM ai_infrastructure.organisation_platform_credentials ORDER BY organisation_id, platform",
    fetch_mode='all'
)
for c in (creds or []):
    print(c)

print("\n=== CREDENTIAL_ACCESS_LOG - TABLE EXISTS? ===")
has_log = execute_query(
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='credential_access_log'",
    fetch_mode='value'
)
print("credential_access_log exists:", bool(has_log))

print("\n=== ORG_INVITATIONS - TABLE EXISTS? ===")
has_inv = execute_query(
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='org_invitations'",
    fetch_mode='value'
)
print("org_invitations exists:", bool(has_inv))

print("\n=== SESSION_MEMBERS - TABLE EXISTS? ===")
has_sm = execute_query(
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='synergy_sessions' AND table_name='session_members'",
    fetch_mode='value'
)
print("session_members exists:", bool(has_sm))

print("\n=== SYNERGY_SESSIONS COLUMNS ===")
cols = execute_query(
    "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='synergy_sessions' AND table_name='synergy_sessions' ORDER BY ordinal_position",
    fetch_mode='all'
)
for c in (cols or []):
    print(c)

print("\n=== USERS TABLE - KEY COLUMNS ===")
user_cols = execute_query(
    "SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='users' AND column_name IN ('org_role','organisation_id','is_sub_user','parent_user_id','display_name') ORDER BY column_name",
    fetch_mode='all'
)
for c in (user_cols or []):
    print(c)

print("\n=== ORGANISATIONS TABLE COLUMNS ===")
org_cols = execute_query(
    "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='organisations' ORDER BY ordinal_position",
    fetch_mode='all'
)
for c in (org_cols or []):
    print(c)

print("\n=== RLS POLICIES ON ORG TABLES ===")
rls = execute_query(
    "SELECT schemaname, tablename, policyname, cmd FROM pg_policies WHERE schemaname IN ('ai_infrastructure','synergy_sessions') ORDER BY schemaname, tablename",
    fetch_mode='all'
)
for r in (rls or []):
    print(r)

print("\n=== HELPER FUNCTIONS EXIST? ===")
funcs = execute_query(
    "SELECT routine_name FROM information_schema.routines WHERE routine_schema='ai_infrastructure' AND routine_name IN ('get_role_level','mask_credential','user_can_list_credential','user_can_reveal_credential')",
    fetch_mode='all'
)
for f in (funcs or []):
    print(f)

print("\n=== JWT PAYLOAD CHECK (user_auth login query) ===")
# Check if the login query in user_auth.py joins organisations
login_q = execute_query(
    "SELECT id, username, organisation_id, org_role FROM ai_infrastructure.users WHERE id=12",
    fetch_mode='one'
)
print("User 12 (gerardo):", login_q)

print("\n=== VALORAI ORG? ===")
valorai = execute_query(
    "SELECT id, name, slug FROM ai_infrastructure.organisations WHERE slug='valorai'",
    fetch_mode='one'
)
print("valorai org:", valorai)

print("\n=== PLATFORM ORG? ===")
platform_org = execute_query(
    "SELECT id, name, slug FROM ai_infrastructure.organisations WHERE slug='platform'",
    fetch_mode='one'
)
print("platform org:", platform_org)

print("\nDONE")
