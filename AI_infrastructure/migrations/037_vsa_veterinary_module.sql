-- =========================================================================
-- Migration 037: VSA Veterinary Alerts Module
-- Date: March 26, 2026
-- Purpose: Add vsa_veterinary to module_catalog so it can be enabled
--          per-org via org_module_access. The tab-content div
--          (tab-vsa-veterinary-alerts) and sidebar button already exist
--          in the frontend and are gated by data-module="vsa_veterinary".
--
-- Run in Supabase SQL Editor.
-- Idempotent: ON CONFLICT (module_name) DO NOTHING
-- =========================================================================

INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('vsa_veterinary',
     'VSA Veterinary Alerts',
     'Veterinary practice alert management — patient reminders, vaccination schedules, and clinical notifications. Org-specific module for veterinary clients.',
     'fas fa-stethoscope',
     '#10B981',
     'operations',
     'enterprise',
     ARRAY['supabase_vsa'],
     48)

ON CONFLICT (module_name) DO NOTHING;

-- =========================================================================
-- Verification query — should return 1 row after running this migration
-- =========================================================================
-- SELECT module_name, display_name, min_plan_tier, required_platforms
-- FROM ai_infrastructure.module_catalog
-- WHERE module_name = 'vsa_veterinary';
