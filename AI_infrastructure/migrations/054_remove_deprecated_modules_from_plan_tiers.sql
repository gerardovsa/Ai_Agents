-- ============================================================================
-- Migration 054: Remove 3 deprecated in-house-print modules from plan_modules
-- Created: June 15, 2026
-- Purpose: Companion to migration 053.  Removes the 3 archived module names
--          from the plan-tier default list (plan_modules).  org_module_access
--          per-org rows are NOT touched here — they are per-customer data
--          and will become harmless (the underlying module row is now
--          is_active=FALSE, so no UI surface references them) once 053 lands.
--
--          Inhouse-kanban is NOT touched — it stays live and continues to
--          appear in the enterprise tier default list.
--
--          The 'inhouseprint_sql' platform_catalog row is NOT touched here.
--          inhouse-kanban still uses it as its required_platform for
--          credential lookup.
--
--          The 'inhouse_print' MODULE row is soft-deleted (is_active=FALSE)
--          in migration 053, but its module_name reference in plan_modules
--          is hard-deleted here.  This is intentional: the module row is
--          recoverable from git history; the plan-tier mapping is not
--          (it would be a misleading plan default for any new org).
--
-- Idempotent: yes — DELETE with WHERE returns 0 rows on re-run; safe.
-- ============================================================================

-- Step 1: record the rows being deleted for the verify block
DO $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM ai_infrastructure.plan_modules
        WHERE  module_name IN ('inhouse_print', 'quote_calculator', 'stock_management')
        RETURNING 1
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RAISE NOTICE '[Migration 054] Deleted % row(s) from plan_modules (inhouse_print, quote_calculator, stock_management)', deleted_count;
END $$;

-- Step 2: defensive check on org_module_access — log how many org-level
-- overrides reference the archived modules.  We do NOT delete these (per-org
-- data is customer-owned), but we report them so the operator can clean
-- them up via the org admin UI or a one-off query.
DO $$
DECLARE
    override_count INTEGER;
    org_list       TEXT;
BEGIN
    SELECT COUNT(*), STRING_AGG(DISTINCT organisation_id::TEXT, ', ' ORDER BY organisation_id::TEXT)
    INTO   override_count, org_list
    FROM   ai_infrastructure.org_module_access
    WHERE  module_name IN ('inhouse_print', 'quote_calculator', 'stock_management');

    IF override_count = 0 THEN
        RAISE NOTICE '[Migration 054] ✅ No org-level overrides reference the 3 archived modules (clean)';
    ELSE
        RAISE NOTICE '[Migration 054] ℹ️  % org-level override row(s) reference the archived modules (orgs: %).  These are now harmless (module is is_active=FALSE) but can be cleaned up via the org admin UI or: DELETE FROM ai_infrastructure.org_module_access WHERE module_name IN (''inhouse_print'', ''quote_calculator'', ''stock_management'');',
            override_count, org_list;
    END IF;
END $$;

-- Step 3: confirm inhouse-kanban is still in the enterprise plan
DO $$
DECLARE
    kanban_in_plan BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM ai_infrastructure.plan_modules
        WHERE  plan_tier  = 'enterprise'
          AND  module_name = 'inhouse_kanban'
    ) INTO kanban_in_plan;

    IF kanban_in_plan THEN
        RAISE NOTICE '[Migration 054] ✅ inhouse_kanban remains in the enterprise plan (correct — kept for demo)';
    ELSE
        RAISE WARNING '[Migration 054] ❌ inhouse_kanban NOT in enterprise plan — this module should stay enabled';
    END IF;
END $$;
