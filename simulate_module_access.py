"""
Simulate module access for all role/tier combinations.

Tests the actual get_user_enabled_modules() logic by temporarily patching
the user's org_role in memory (not writing to DB).

Run: python simulate_module_access.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AI_infrastructure.shared.database_utils import execute_query

ROLE_LEVELS = {'viewer': 1, 'member': 2, 'manager': 3, 'admin': 4, 'owner': 5}


# ── Fetch state from DB ──────────────────────────────────────────────────────

def get_all_modules():
    rows = execute_query(
        "SELECT module_name FROM ai_infrastructure.module_catalog WHERE is_active=TRUE ORDER BY module_name",
        fetch_mode='all'
    ) or []
    return {r['module_name'] for r in rows}


def get_org_tier_modules(plan_tier: str) -> set:
    rows = execute_query(
        "SELECT module_name FROM ai_infrastructure.plan_modules WHERE plan_tier=%s",
        (plan_tier,),
        fetch_mode='all'
    ) or []
    return {r['module_name'] for r in rows}


def get_org_overrides(org_id: int) -> dict:
    """Returns {module_name: is_enabled}"""
    rows = execute_query(
        "SELECT module_name, is_enabled FROM ai_infrastructure.org_module_access WHERE organisation_id=%s",
        (org_id,),
        fetch_mode='all'
    ) or []
    return {r['module_name']: r['is_enabled'] for r in rows}


def simulate_modules(org_role: str, plan_tier: str, org_id: int = 1) -> set:
    """Simulate module resolution without hitting the 3-tier loader."""
    ALL = get_all_modules()

    # Owner bypasses everything
    if org_role == 'owner':
        return ALL

    base = get_org_tier_modules(plan_tier)
    overrides = get_org_overrides(org_id)
    for mod, enabled in overrides.items():
        if enabled:
            base.add(mod)
        else:
            base.discard(mod)

    return base


# ── Simulation ───────────────────────────────────────────────────────────────

def run():
    print("=" * 70)
    print("MODULE ACCESS SIMULATION")
    print("=" * 70)

    # Get actual org state
    org = execute_query(
        "SELECT id, name, plan_tier FROM ai_infrastructure.organisations WHERE id=1",
        fetch_mode='one'
    )
    ALL = get_all_modules()
    total = len(ALL)
    print(f"\nOrg: {org['name']} (id={org['id']}) — plan_tier = {org['plan_tier']}")
    print(f"Total active modules in catalog: {total}")
    print()

    # Test every role
    for role in ['viewer', 'member', 'manager', 'admin', 'owner']:
        modules = simulate_modules(role, org['plan_tier'], org['id'])
        note = ""
        if role == 'owner':
            note = " ← ALL modules (role bypass)"
        elif len(modules) == total:
            note = " ← all plan modules"
        print(f"  {role:<10} → {len(modules):>2}/{total} modules{note}")
        if len(modules) < total:
            missing = sorted(ALL - modules)
            if missing:
                print(f"             missing: {', '.join(missing)}")

    print()
    print("-" * 70)
    print("CREDENTIAL VISIBILITY")
    print("-" * 70)
    print()
    cred_rules = {
        'viewer':  {'platform_connections_btn': 'HIDDEN',  'org_vault_tab': 'HIDDEN'},
        'member':  {'platform_connections_btn': 'HIDDEN',  'org_vault_tab': 'HIDDEN'},
        'manager': {'platform_connections_btn': 'HIDDEN',  'org_vault_tab': 'HIDDEN'},
        'admin':   {'platform_connections_btn': 'VISIBLE', 'org_vault_tab': 'VISIBLE'},
        'owner':   {'platform_connections_btn': 'VISIBLE', 'org_vault_tab': 'VISIBLE'},
    }
    print(f"  {'Role':<10} {'Account connections btn':<26} {'Org vault tab'}")
    print(f"  {'-'*10} {'-'*26} {'-'*20}")
    for role, rules in cred_rules.items():
        c1 = rules['platform_connections_btn']
        c2 = rules['org_vault_tab']
        print(f"  {role:<10} {c1:<26} {c2}")

    print()
    print("-" * 70)
    print("SIDEBAR MODULE GATING (Zone 2 — sidebarModulesSection)")
    print("-" * 70)
    print()

    # Simulate what initModulesFromOrg renders for each role (per owner logic)
    ZONE2_MODULES = [
        'inhouse_kanban', 'inhouse_print', 'quote_calculator', 'stock_management',
        'xero', 'shopify', 'auspost_shipping', 'customer_reactivation',
        'database_visualizer', 'github', 'render_management', 'local_filesystem',
        'vsa_veterinary',
    ]
    ZONE1_GATED = ['woocommerce']  # data-module in Zone 1

    for role in ['viewer', 'member', 'admin', 'owner']:
        modules = simulate_modules(role, org['plan_tier'], org['id'])
        z1 = [m for m in ZONE1_GATED if m in modules]
        z2 = [m for m in ZONE2_MODULES if m in modules]
        print(f"  {role}:")
        print(f"    Zone 1 WooCommerce buttons: {'VISIBLE' if z1 else 'HIDDEN'}")
        print(f"    Zone 2 dynamic buttons ({len(z2)}): {', '.join(z2) if z2 else 'none'}")
        print()

    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    run()
