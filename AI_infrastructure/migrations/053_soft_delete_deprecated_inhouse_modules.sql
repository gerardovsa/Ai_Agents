-- ============================================================================
-- Migration 053: Soft-delete 3 deprecated in-house-print modules
-- Created: June 15, 2026
-- Purpose: On 2026-06-15 the in-house-print product surface (quote-calculator,
--          stock-management, inhouse-print) was archived to
--          archive/inhouse_print_deprecation/ on branch
--          cleanup/inhouse-print-deprecation.  The inhouse-kanban module
--          stays live (still uses the inhouseprint_sql platform credential).
--
--          This migration sets is_active = FALSE on the 3 corresponding
--          module_catalog rows.  We soft-delete (not hard-delete) so the
--          rows are reversible, and so any analytics or audit queries that
--          reference them by name still resolve.
--
--          Plan-tier rows for these 3 modules are cleaned in migration 054.
--          The platform_catalog row for 'inhouseprint_sql' stays — inhouse-kanban
--          still uses it as its required_platform.
--
-- Idempotent: yes — sets is_active to a known value, no destructive operation.
--             Safe to run multiple times.
-- ============================================================================

UPDATE ai_infrastructure.module_catalog
SET    is_active = FALSE
WHERE  module_name IN ('inhouse_print', 'quote_calculator', 'stock_management')
  AND  is_active IS DISTINCT FROM FALSE;   -- skip if already FALSE (idempotent)

-- =========================================================================
-- Verify
-- =========================================================================
DO $$
DECLARE
    still_active_count INTEGER;
    deactivated_count  INTEGER;
BEGIN
    SELECT COUNT(*) INTO still_active_count
    FROM   ai_infrastructure.module_catalog
    WHERE  module_name IN ('inhouse_print', 'quote_calculator', 'stock_management')
      AND  is_active = TRUE;

    SELECT COUNT(*) INTO deactivated_count
    FROM   ai_infrastructure.module_catalog
    WHERE  module_name IN ('inhouse_print', 'quote_calculator', 'stock_management')
      AND  is_active = FALSE;

    IF still_active_count = 0 AND deactivated_count = 3 THEN
        RAISE NOTICE '[Migration 053] ✅ All 3 archived modules soft-deleted (inactive): inhouse_print, quote_calculator, stock_management';
    ELSIF still_active_count > 0 THEN
        RAISE WARNING '[Migration 053] ❌ % of the 3 archived modules are still ACTIVE — check for stale rows', still_active_count;
    ELSE
        RAISE WARNING '[Migration 053] ⚠️  Expected 3 inactive rows, found % (may have been pre-deactivated)', deactivated_count;
    END IF;
END $$;

-- Sanity: confirm inhouse-kanban is still ACTIVE
DO $$
DECLARE
    kanban_status BOOLEAN;
BEGIN
    SELECT is_active INTO kanban_status
    FROM   ai_infrastructure.module_catalog
    WHERE  module_name = 'inhouse_kanban';

    IF kanban_status IS NULL THEN
        RAISE WARNING '[Migration 053] ⚠️  inhouse_kanban row not found in module_catalog';
    ELSIF kanban_status = FALSE THEN
        RAISE WARNING '[Migration 053] ❌ inhouse_kanban is INACTIVE — this module should stay LIVE';
    ELSE
        RAISE NOTICE '[Migration 053] ✅ inhouse_kanban remains ACTIVE (correct — kept for demo)';
    END IF;
END $$;
