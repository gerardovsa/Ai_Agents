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
           timezone, country_code, is_active, created_at, updated_at,
           vault_password_hash, metadata,
           description, visibility, allowed_domains,
           ai_provider, ai_model, ai_max_tokens,
           COALESCE(is_personal_org, FALSE) AS is_personal_org
    FROM ai_infrastructure.organisations WHERE id = %s
    """,
    (1,),
    fetch_mode='one'
)
print(f"Result: {org_info_query}")
required_org_info_keys = {
    'id', 'name', 'slug', 'plan_tier', 'display_name', 'logo_url',
    'timezone', 'country_code', 'is_active', 'created_at', 'updated_at',
    'vault_password_hash', 'metadata', 'description', 'visibility',
    'allowed_domains', 'ai_provider', 'ai_model', 'ai_max_tokens',
    'is_personal_org',
}
assert org_info_query is not None, "Current get_org_info() query returned no row"
missing_org_info_keys = required_org_info_keys - set(org_info_query)
assert not missing_org_info_keys, (
    f"Current get_org_info() query is missing keys: {sorted(missing_org_info_keys)}"
)

print("\n" + "=" * 80)
print("TEST 3: Query used in get_user_org_context() - LEFT JOIN")
print("=" * 80)
org_context = execute_query(
    """
    SELECT
        u.organisation_id,
        u.org_role,
        u.role             AS system_role,
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

column_names = {col['column_name'] for col in columns}
required_org_columns = required_org_info_keys - {'id'}
required_org_columns.add('id')
missing_org_columns = required_org_columns - column_names
assert not missing_org_columns, (
    f"organisations table is missing columns required by /api/org/info: "
    f"{sorted(missing_org_columns)}"
)

print("\n" + "=" * 80)
print("TEST 5: Migration 054 helper and backfill invariants")
print("=" * 80)
helper = execute_query(
    """
    SELECT pg_get_functiondef(p.oid) AS definition
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'ai_infrastructure'
      AND p.proname = 'create_personal_org'
    """,
    (),
    fetch_mode='one'
)
assert helper is not None, "create_personal_org() is missing"
assert 'ON CONFLICT (slug)' in helper['definition'], (
    "create_personal_org() must use the unique organisations.slug conflict target"
)
assert 'ON CONFLICT (name)' not in helper['definition'], (
    "create_personal_org() still uses the non-unique organisations.name target"
)

personal_org_invariants = execute_query(
    """
    SELECT
        (SELECT COUNT(*)
         FROM ai_infrastructure.users
         WHERE organisation_id IS NULL
           AND (is_sub_user IS NULL OR is_sub_user = FALSE)) AS users_without_org,
        (SELECT COUNT(*)
         FROM ai_infrastructure.organisations
         WHERE is_personal_org IS TRUE) AS personal_orgs,
        (SELECT COUNT(*)
         FROM ai_infrastructure.org_module_access oma
         JOIN ai_infrastructure.organisations o
           ON o.id = oma.organisation_id
         WHERE o.is_personal_org IS TRUE
           AND oma.is_enabled IS TRUE
           AND oma.module_name IN (
               'core_chat', 'documents', 'prompt_library',
               'notifications', 'synergy'
           )) AS enabled_core_module_rows
    """,
    (),
    fetch_mode='one'
)
print(f"Migration 054 invariants: {personal_org_invariants}")
assert personal_org_invariants['users_without_org'] == 0, (
    "Eligible solo users remain without an organisation"
)
print("All organisation query and migration invariants passed")

