"""
Seed the developer tier + fix enterprise plan_modules.

Changes:
1. Add vsa_veterinary to enterprise plan_modules (was missing)
2. Create developer tier with ALL active modules from module_catalog
3. Update Vet Success org (id=1) to plan_tier='developer'

Safe to re-run: every INSERT uses IF NOT EXISTS / ON CONFLICT DO NOTHING.
Run from project root: python seed_developer_tier.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_infrastructure.shared.database_utils import execute_query


def run():
    print("=" * 60)
    print("SEEDING DEVELOPER TIER")
    print("=" * 60)

    # ----------------------------------------------------------------
    # Step 1: Ensure vsa_veterinary is in enterprise tier
    # ----------------------------------------------------------------
    print("\n[1] Adding vsa_veterinary to enterprise plan_modules ...")
    execute_query(
        """
        INSERT INTO ai_infrastructure.plan_modules (plan_tier, module_name)
        VALUES ('enterprise', 'vsa_veterinary')
        ON CONFLICT DO NOTHING
        """,
        (),
        fetch_mode=None
    )
    count = execute_query(
        "SELECT COUNT(*) FROM ai_infrastructure.plan_modules WHERE plan_tier = 'enterprise'",
        fetch_mode='value'
    )
    print(f"  enterprise tier now has {count} modules")

    # ----------------------------------------------------------------
    # Step 2: Create developer tier with ALL active modules
    # ----------------------------------------------------------------
    print("\n[2] Creating developer tier ...")

    # Remove any existing developer rows (idempotent reset)
    execute_query(
        "DELETE FROM ai_infrastructure.plan_modules WHERE plan_tier = 'developer'",
        (),
        fetch_mode=None
    )

    execute_query(
        """
        INSERT INTO ai_infrastructure.plan_modules (plan_tier, module_name)
        SELECT 'developer', module_name
        FROM   ai_infrastructure.module_catalog
        WHERE  is_active = TRUE
        """,
        (),
        fetch_mode=None
    )
    dev_count = execute_query(
        "SELECT COUNT(*) FROM ai_infrastructure.plan_modules WHERE plan_tier = 'developer'",
        fetch_mode='value'
    )
    print(f"  developer tier created with {dev_count} modules")

    # List them
    dev_modules = execute_query(
        "SELECT module_name FROM ai_infrastructure.plan_modules WHERE plan_tier = 'developer' ORDER BY module_name",
        fetch_mode='all'
    ) or []
    for r in dev_modules:
        print(f"    - {r['module_name']}")

    # ----------------------------------------------------------------
    # Step 3: Update Vet Success org to developer tier
    # ----------------------------------------------------------------
    print("\n[3] Updating Vet Success org (id=1) to developer tier ...")
    execute_query(
        "UPDATE ai_infrastructure.organisations SET plan_tier = 'developer' WHERE id = 1",
        (),
        fetch_mode=None
    )
    org = execute_query(
        "SELECT id, name, plan_tier FROM ai_infrastructure.organisations WHERE id = 1",
        fetch_mode='one'
    )
    print(f"  Org {org['id']} ({org['name']}) plan_tier = {org['plan_tier']}")

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    print("\n[Summary]")
    tiers = execute_query(
        """
        SELECT plan_tier, COUNT(*) AS module_count
        FROM ai_infrastructure.plan_modules
        GROUP BY plan_tier
        ORDER BY plan_tier
        """,
        fetch_mode='all'
    ) or []
    for t in tiers:
        print(f"  {t['plan_tier']:<15} {t['module_count']} modules")

    print("\nDone.")


if __name__ == '__main__':
    run()
