from shared.database_utils import execute_query

# Check RLS status and policies on oauth_tokens
rls = execute_query(
    "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='ai_infrastructure' AND tablename='oauth_tokens'",
    fetch_mode='one'
)
print('oauth_tokens RLS:', rls)

policies = execute_query(
    "SELECT policyname, cmd, roles, qual FROM pg_policies WHERE schemaname='ai_infrastructure' AND tablename='oauth_tokens'",
    fetch_mode='all'
)
print('oauth_tokens policies:', policies)
