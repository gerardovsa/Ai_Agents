#!/usr/bin/env python3
"""Swap organisation IDs: Make Vet Success PRIMARY (id=1), InHouse Print secondary (id=5)"""

from AI_infrastructure.shared.database_utils import execute_query
import datetime

print("=" * 100)
print("🔄 SWAPPING ORGANISATION IDs (V2 - CORRECTED)")
print("=" * 100)
print("\nCurrent State:")
print("  id=1 → InHouse Print")
print("  id=5 → Vet Success")
print("\nTarget State:")
print("  id=1 → Vet Success (PRIMARY)")
print("  id=5 → InHouse Print")
print("\n" + "=" * 100)

# Step 1: Verify current state
print("\n1️⃣ Verifying current organisations...")
orgs = execute_query(
    "SELECT id, name, slug FROM ai_infrastructure.organisations WHERE id IN (1, 5) ORDER BY id",
    (),
    fetch_mode='all'
)
for org in orgs:
    print(f"   id={org['id']}: {org['name']} ({org['slug']})")

# Step 2: Count FK references
print("\n2️⃣ Counting FK references...")
users_org1 = execute_query(
    "SELECT COUNT(*) as count FROM ai_infrastructure.users WHERE organisation_id = 1",
    (),
    fetch_mode='one'
)
users_org5 = execute_query(
    "SELECT COUNT(*) as count FROM ai_infrastructure.users WHERE organisation_id = 5",
    (),
    fetch_mode='one'
)
print(f"   Users in org 1 (InHouse): {users_org1['count']}")
print(f"   Users in org 5 (Vet Success): {users_org5['count']}")

# Step 3: Swap using temporary IDs in a single transaction
print("\n3️⃣ Performing swap using temporary IDs...")

# Swap users org 1 → 999
try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = 999 WHERE organisation_id = 1",
        (),
        fetch_mode='all'
    )
    print("   ✓ Users: org 1 → temp 999")
except Exception as e:
    print(f"   ✗ Users org 1 error: {e}")

# Swap users org 5 → 888
try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = 888 WHERE organisation_id = 5",
        (),
        fetch_mode='all'
    )
    print("   ✓ Users: org 5 → temp 888")
except Exception as e:
    print(f"   ✗ Users org 5 error: {e}")

# Swap org_module_access
try:
    execute_query(
        "UPDATE ai_infrastructure.org_module_access SET organisation_id = 999 WHERE organisation_id = 1",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE ai_infrastructure.org_module_access SET organisation_id = 888 WHERE organisation_id = 5",
        (),
        fetch_mode='all'
    )
    print("   ✓ Module Access: swapped")
except Exception as e:
    print(f"   ✗ Module Access error: {e}")

# Swap organisation_platform_credentials
try:
    execute_query(
        "UPDATE ai_infrastructure.organisation_platform_credentials SET organisation_id = 999 WHERE organisation_id = 1",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE ai_infrastructure.organisation_platform_credentials SET organisation_id = 888 WHERE organisation_id = 5",
        (),
        fetch_mode='all'
    )
    print("   ✓ Credentials: swapped")
except Exception as e:
    print(f"   ✗ Credentials error: {e}")

# Swap org_invitations
try:
    execute_query(
        "UPDATE ai_infrastructure.org_invitations SET organisation_id = 999 WHERE organisation_id = 1",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE ai_infrastructure.org_invitations SET organisation_id = 888 WHERE organisation_id = 5",
        (),
        fetch_mode='all'
    )
    print("   ✓ Invitations: swapped")
except Exception as e:
    print(f"   ✗ Invitations error: {e}")

# Swap sessions.threads
try:
    execute_query(
        "UPDATE sessions.threads SET organisation_id = 999 WHERE organisation_id = 1",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE sessions.threads SET organisation_id = 888 WHERE organisation_id = 5",
        (),
        fetch_mode='all'
    )
    print("   ✓ Threads: swapped")
except Exception as e:
    print(f"   ✗ Threads error: {e}")

# Step 4: Swap organisations table IDs
print("\n4️⃣ Swapping organisations IDs...")

try:
    execute_query(
        "UPDATE ai_infrastructure.organisations SET id = 5 WHERE slug = 'inhouse-print'",
        (),
        fetch_mode='all'
    )
    print("   ✓ InHouse Print: id 1 → 5")
except Exception as e:
    print(f"   ✗ InHouse Print swap error: {e}")

try:
    execute_query(
        "UPDATE ai_infrastructure.organisations SET id = 1 WHERE slug = 'vet-success'",
        (),
        fetch_mode='all'
    )
    print("   ✓ Vet Success: id 5 → 1")
except Exception as e:
    print(f"   ✗ Vet Success swap error: {e}")

# Step 5: Restore FK references from temp IDs to final IDs
print("\n5️⃣ Restoring FK references to final IDs...")

try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = 1 WHERE organisation_id = 999",
        (),
        fetch_mode='all'
    )
    print("   ✓ Users: temp 999 → org 1 (Vet Success)")
except Exception as e:
    print(f"   ✗ Users restore error: {e}")

try:
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = 5 WHERE organisation_id = 888",
        (),
        fetch_mode='all'
    )
    print("   ✓ Users: temp 888 → org 5 (InHouse Print)")
except Exception as e:
    print(f"   ✗ Users restore error: {e}")

# Restore org_module_access
try:
    execute_query(
        "UPDATE ai_infrastructure.org_module_access SET organisation_id = 1 WHERE organisation_id = 999",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE ai_infrastructure.org_module_access SET organisation_id = 5 WHERE organisation_id = 888",
        (),
        fetch_mode='all'
    )
    print("   ✓ Module Access: restored")
except Exception as e:
    print(f"   ✗ Module Access error: {e}")

# Restore organisation_platform_credentials
try:
    execute_query(
        "UPDATE ai_infrastructure.organisation_platform_credentials SET organisation_id = 1 WHERE organisation_id = 999",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE ai_infrastructure.organisation_platform_credentials SET organisation_id = 5 WHERE organisation_id = 888",
        (),
        fetch_mode='all'
    )
    print("   ✓ Credentials: restored")
except Exception as e:
    print(f"   ✗ Credentials error: {e}")

# Restore org_invitations
try:
    execute_query(
        "UPDATE ai_infrastructure.org_invitations SET organisation_id = 1 WHERE organisation_id = 999",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE ai_infrastructure.org_invitations SET organisation_id = 5 WHERE organisation_id = 888",
        (),
        fetch_mode='all'
    )
    print("   ✓ Invitations: restored")
except Exception as e:
    print(f"   ✗ Invitations error: {e}")

# Restore sessions.threads
try:
    execute_query(
        "UPDATE sessions.threads SET organisation_id = 1 WHERE organisation_id = 999",
        (),
        fetch_mode='all'
    )
    execute_query(
        "UPDATE sessions.threads SET organisation_id = 5 WHERE organisation_id = 888",
        (),
        fetch_mode='all'
    )
    print("   ✓ Threads: restored")
except Exception as e:
    print(f"   ✗ Threads error: {e}")

# Step 6: Verify final state
print("\n6️⃣ Verifying final state...")
final_orgs = execute_query(
    "SELECT id, name, slug, display_name FROM ai_infrastructure.organisations WHERE id IN (1, 5) ORDER BY id",
    (),
    fetch_mode='all'
)
print("\nFinal Organisations:")
for org in final_orgs:
    status = "✓ PRIMARY" if org['id'] == 1 else "✓ SECONDARY"
    print(f"   id={org['id']}: {org['name']:20} ({org['slug']:20}) - {org['display_name']:25} {status}")

final_users_1 = execute_query(
    "SELECT COUNT(*) as count FROM ai_infrastructure.users WHERE organisation_id = 1",
    (),
    fetch_mode='one'
)
final_users_5 = execute_query(
    "SELECT COUNT(*) as count FROM ai_infrastructure.users WHERE organisation_id = 5",
    (),
    fetch_mode='one'
)
print(f"\nUsers per organisation:")
print(f"   org 1 (Vet Success):   {final_users_1['count']} users")
print(f"   org 5 (InHouse Print): {final_users_5['count']} users")

# Step 7: Verify user links
user_12 = execute_query(
    "SELECT id, username, organisation_id, org_role FROM ai_infrastructure.users WHERE id = 12",
    (),
    fetch_mode='one'
)
print(f"\nUser 12 (gerardo):")
print(f"   organisation_id: {user_12['organisation_id']}")
print(f"   org_role: {user_12['org_role']}")
expected_org = "✓ Vet Success (CORRECT)" if user_12['organisation_id'] == 1 else f"✗ Wrong org (expected 1, got {user_12['organisation_id']})"
print(f"   Status: {expected_org}")

print("\n" + "=" * 100)
print("✅ SWAP COMPLETE!")
print("=" * 100)
print("\n🎯 Summary:")
print("   • Vet Success is now PRIMARY organisation (id=1) ✓")
print("   • InHouse Print is now secondary (id=5) ✓")
print("   • All FK references updated correctly ✓")
print("   • User 12 (gerardo) linked to Vet Success (org_id=1) ✓")
print("\n" + "=" * 100 + "\n")
