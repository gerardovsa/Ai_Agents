#!/usr/bin/env python3
"""Check organization status for user 12"""

from AI_infrastructure.shared.database_utils import execute_query

# Check user 12
print("\n=== CHECKING USER 12 ===")
user = execute_query(
    'SELECT id, username, email, organisation_id, org_role, is_sub_user FROM ai_infrastructure.users WHERE id = 12',
    fetch_mode='one'
)
print(f"User: {user}")

# Check org 1
print("\n=== CHECKING ORG 1 ===")
org = execute_query(
    'SELECT id, name, slug, plan_tier, is_active FROM ai_infrastructure.organisations WHERE id = 1',
    fetch_mode='one'
)
print(f"Org: {org}")

# Check credentials
print("\n=== CHECKING CREDENTIALS FOR ORG 1 ===")
creds = execute_query(
    'SELECT id, platform, display_name, is_active FROM ai_infrastructure.organisation_platform_credentials WHERE organisation_id = 1',
    fetch_mode='all'
)
print(f"Credentials: {creds}")

# Check if user_id 12 can fetch org info (simulate the API call)
print("\n=== SIMULATING API CALL: GET /api/org/info ===")
org_ctx = execute_query(
    '''SELECT u.organisation_id, u.org_role, o.name AS org_name, o.slug AS org_slug
       FROM ai_infrastructure.users u
       LEFT JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
       WHERE u.id = 12''',
    fetch_mode='one'
)
print(f"Org context: {org_ctx}")

if org_ctx and org_ctx.get('organisation_id'):
    print(f"✅ User 12 should have access to org {org_ctx['organisation_id']} with role {org_ctx['org_role']}")
else:
    print(f"❌ User 12 has NO organisation_id - cannot access /api/org/info")
