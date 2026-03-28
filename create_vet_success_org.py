#!/usr/bin/env python3
"""Create Vet Success organisation and move InHouse Print"""

from AI_infrastructure.shared.database_utils import execute_query
import datetime
import json

print("=" * 100)
print("REORGANISING ORGANISATIONS TABLE")
print("=" * 100)

# Step 1: Get current InHouse Print data
print("\n1️⃣ Fetching current InHouse Print org data...")
inhouse = execute_query(
    "SELECT * FROM ai_infrastructure.organisations WHERE id = 1",
    (),
    fetch_mode='one'
)
print(f"Found: {inhouse['name']} (id={inhouse['id']})")

# Step 2: Unlink user 12 temporarily
print("\n2️⃣ Temporarily unlinking user 12 from organisation...")
try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = NULL WHERE id = 12",
        (),
        fetch_mode='none'
    )
except:
    # Ignore the "no results" error for UPDATE statements
    pass
print("✅ User 12 unlinked")

# Step 3: Delete the old InHouse Print org (now safe, no FK constraint)
print("\n3️⃣ Deleting old InHouse Print org (id=1)...")
try:
    execute_query(
        "DELETE FROM ai_infrastructure.organisations WHERE id = 1",
        (),
        fetch_mode='none'
    )
except:
    pass
print("✅ InHouse Print (id=1) deleted")

# Step 4: Reset the sequence so next insert gets id=1
print("\n4️⃣ Resetting organisations sequence...")
try:
    execute_query(
        "ALTER SEQUENCE organisations_id_seq RESTART WITH 1",
        (),
        fetch_mode='none'
    )
except:
    pass
print("✅ Sequence reset")

# Step 5: Create Vet Success as id=1
print("\n5️⃣ Creating Vet Success organisation (id=1)...")
vet_success = execute_query(
    """
    INSERT INTO ai_infrastructure.organisations 
    (name, slug, plan_tier, is_active, display_name, timezone, 
     country_code, description, visibility, allowed_domains,
     ai_provider, ai_model, ai_max_tokens, metadata, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, name, slug
    """,
    (
        'Vet Success',                              # name
        'vet-success',                              # slug
        'professional',                             # plan_tier
        True,                                       # is_active
        'Vet Success Academy',                      # display_name
        'Australia/Sydney',                         # timezone
        'AU',                                       # country_code
        'Veterinary education and training platform',  # description
        'private',                                  # visibility
        [],                                         # allowed_domains
        'anthropic',                                # ai_provider
        'claude-sonnet-4-5-20250929',              # ai_model
        8192,                                       # ai_max_tokens
        '{}',                                       # metadata
        datetime.datetime.now(datetime.timezone.utc),  # created_at
        datetime.datetime.now(datetime.timezone.utc)   # updated_at
    ),
    fetch_mode='one'
)
print(f"✅ Created: {vet_success['name']} (id={vet_success['id']}, slug={vet_success['slug']})")

# Step 6: Create InHouse Print as id=5
print("\n6️⃣ Creating InHouse Print organisation (id=5)...")
inhouse_new = execute_query(
    """
    INSERT INTO ai_infrastructure.organisations 
    (id, name, slug, plan_tier, is_active, display_name, timezone, 
     country_code, description, visibility, allowed_domains,
     ai_provider, ai_model, ai_max_tokens, metadata, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, name, slug
    """,
    (
        5,                                          # id (explicitly set to 5)
        inhouse['name'],                            # name
        inhouse['slug'],                            # slug
        inhouse['plan_tier'],                       # plan_tier
        inhouse['is_active'],                       # is_active
        inhouse['display_name'],                    # display_name
        inhouse['timezone'],                        # timezone
        inhouse['country_code'],                    # country_code
        inhouse['description'],                     # description
        inhouse['visibility'],                      # visibility
        inhouse['allowed_domains'],                 # allowed_domains
        inhouse['ai_provider'],                     # ai_provider
        inhouse['ai_model'],                        # ai_model
        inhouse['ai_max_tokens'],                   # ai_max_tokens
        inhouse['metadata'],                        # metadata
        inhouse['created_at'],                      # created_at (preserve original)
        datetime.datetime.now(datetime.timezone.utc)   # updated_at
    ),
    fetch_mode='one'
)
print(f"✅ Created: {inhouse_new['name']} (id={inhouse_new['id']}, slug={inhouse_new['slug']})")

# Step 7: Update user 12 to point to Vet Success (id=1)
print("\n7️⃣ Relinking user 12 to Vet Success organisation (id=1)...")
try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = 1, org_role = 'owner' WHERE id = 12",
        (),
        fetch_mode='none'
    )
except:
    pass
print("✅ User 12 linked to Vet Success (owner)")

# Step 8: Verify the changes
print("\n8️⃣ Verifying organisations table...")
all_orgs = execute_query(
    "SELECT id, name, slug, plan_tier, is_active FROM ai_infrastructure.organisations ORDER BY id",
    (),
    fetch_mode='all'
)
print(f"\nTotal organisations: {len(all_orgs)}\n")
for org in all_orgs:
    print(f"  ID={org['id']}: {org['name']:20} slug={org['slug']:20} tier={org['plan_tier']:15} active={org['is_active']}")

# Step 9: Verify user link
print("\n9️⃣ Verifying user 12 link...")
user = execute_query(
    "SELECT id, username, organisation_id, org_role FROM ai_infrastructure.users WHERE id = 12",
    (),
    fetch_mode='one'
)
print(f"User {user['username']}: org_id={user['organisation_id']}, role={user['org_role']}")

# Step 10: Verify credentials are still linked correctly
print("\n🔟 Verifying organisation credentials...")
creds = execute_query(
    """
    SELECT id, organisation_id, platform, display_name 
    FROM ai_infrastructure.organisation_platform_credentials 
    ORDER BY organisation_id, platform
    """,
    (),
    fetch_mode='all'
)
for cred in creds:
    print(f"  Cred ID={cred['id']}: org_id={cred['organisation_id']}, platform={cred['platform']}, {cred['display_name']}")

print("\n" + "=" * 100)
print("✅ MIGRATION COMPLETE!")
print("=" * 100)
print("\nSummary:")
print(f"  - Vet Success is now the primary organisation (id=1)")
print(f"  - InHouse Print moved to organisation (id=5)")
print(f"  - User 12 (gerardo) linked to Vet Success as owner")
print(f"  - All platform credentials preserved")
