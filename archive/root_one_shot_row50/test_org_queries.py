#!/usr/bin/env python3
"""Test the exact queries used in get_user_org_context and get_org_info"""

from AI_infrastructure.shared.database_utils import execute_query

print("=" * 80)
print("TEST 1: Direct query to organisations table")
print("=" * 80)
org_direct = execute_query(
    "SELECT id, name, slug FROM ai_infrastructure.organisations WHERE id = %s",
    (1,),
    fetch_mode='one'
)
print(f"Result: {org_direct}")
print(f"Type: {type(org_direct)}")

print("\n" + "=" * 80)
print("TEST 2: Query used in get_org_info()")
print("=" * 80)
org_info_query = execute_query(
    """
    SELECT id, name, slug, plan_tier, display_name, logo_url,
           timezone, country_code, is_active, created_at,
           description, visibility, allowed_domains,
           ai_provider, ai_model, ai_max_tokens
    FROM ai_infrastructure.organisations WHERE id = %s
    """,
    (1,),
    fetch_mode='one'
)
print(f"Result: {org_info_query}")

print("\n" + "=" * 80)
print("TEST 3: Query used in get_user_org_context() - LEFT JOIN")
print("=" * 80)
org_context = execute_query(
    """
    SELECT
        u.organisation_id,
        u.org_role,
        o.name             AS org_name,
        o.slug             AS org_slug,
        o.vault_password_hash
    FROM ai_infrastructure.users u
    LEFT JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
    WHERE u.id = %s
    """,
    (12,),
    fetch_mode='one'
)
print(f"Result: {org_context}")

print("\n" + "=" * 80)
print("TEST 4: Check organisations table columns")
print("=" * 80)
# Get table info
columns = execute_query(
    """SELECT column_name, data_type FROM information_schema.columns 
       WHERE table_schema='ai_infrastructure' AND table_name='organisations'
       ORDER BY ordinal_position""",
    (),
    fetch_mode='all'
)
print("Organisations table columns:")
for col in columns:
    print(f"  {col['column_name']}: {col['data_type']}")
