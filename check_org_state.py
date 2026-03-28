#!/usr/bin/env python3
"""Check organisations table state and user 12's org link"""

from AI_infrastructure.shared.database_utils import execute_query

# Check current organisations table
orgs = execute_query("SELECT * FROM ai_infrastructure.organisations ORDER BY id", fetch_mode='all')
print(f"Organisations in DB: {len(orgs)} rows")
for org in orgs:
    print(f"  ID={org['id']}: {org['name']} (slug={org['slug']}, is_active={org.get('is_active')})")

# Check user org link
user = execute_query("SELECT id, username, organisation_id, org_role FROM ai_infrastructure.users WHERE id=12", fetch_mode='one')
print(f"\nUser 12 (gerardo):")
print(f"  organisation_id={user['organisation_id']}")
print(f"  org_role={user['org_role']}")

if user['organisation_id']:
    # Check if that org exists
    org_check = execute_query("SELECT id FROM ai_infrastructure.organisations WHERE id=%s", (user['organisation_id'],), fetch_mode='one')
    if org_check:
        print(f"  ✅ Linked organisation exists")
    else:
        print(f"  ❌ ORPHANED: Linked organisation (id={user['organisation_id']}) does NOT exist!")
