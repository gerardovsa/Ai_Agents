-- ============================================================================
-- Migration 055: VSA organisation-to-hospital mapping
-- Created:    2026-07-22
-- Purpose:    Define which hospital_code values (as used in the external VSA
--             Supabase project at wuwmvtslltqhaycyukxk.supabase.co) belong to
--             which platform organisation. The VSA V4 proxy reads this table
--             on every request and scopes its Supabase queries by the
--             allowed hospital codes for the caller's org.
--
--             Why this exists:
--             The external VSA project uses `key_hospital_code` as the
--             natural discriminator between hospitals. One platform
--             organisation may own N hospitals. Each hospital's data
--             lives under one of: ALGESTER, COMPTONRD, MTGRAVATT,
--             WINDAROO, UNKNOWN (the codes from public.hospital_codes).
--
--             When you onboard a second customer, you give them a row set
--             that scopes them to THEIR hospital codes - either in the
--             shared Supabase project (Option A) or in a dedicated Supabase
--             project (Option B). The proxy does not care which option you
--             pick - the contract is the same: (org_id, hospital_code) list.
--
-- Idempotent: yes (CREATE TABLE IF NOT EXISTS, INSERT ... ON CONFLICT DO NOTHING)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.vsa_org_hospitals (
    organisation_id  INTEGER      NOT NULL,
    hospital_code    TEXT         NOT NULL,
    display_name     TEXT,                                    -- optional human-readable label
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    added_by_user_id INTEGER,                                 -- nullable; the dev who seeded it
    notes            TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (organisation_id, hospital_code),
    CONSTRAINT vsa_org_hospitals_org_fk FOREIGN KEY (organisation_id)
        REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS vsa_org_hospitals_org_idx
    ON ai_infrastructure.vsa_org_hospitals (organisation_id)
    WHERE is_active = TRUE;

-- Auto-touch updated_at on row update
CREATE OR REPLACE FUNCTION ai_infrastructure.vsa_org_hospitals_touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS vsa_org_hospitals_touch_updated_at_trg
    ON ai_infrastructure.vsa_org_hospitals;

CREATE TRIGGER vsa_org_hospitals_touch_updated_at_trg
    BEFORE UPDATE ON ai_infrastructure.vsa_org_hospitals
    FOR EACH ROW EXECUTE FUNCTION ai_infrastructure.vsa_org_hospitals_touch_updated_at();

-- Seed: organisation_id=1 ("Vet Success Academy", owned by user 12 / Gerardo)
-- owns ALL existing hospital codes from the external VSA project.
-- UNKNOWN is included so rows that haven't been classified yet still
-- surface in the proxy for this org.
INSERT INTO ai_infrastructure.vsa_org_hospitals
    (organisation_id, hospital_code, display_name, added_by_user_id, notes)
VALUES
    (1, 'ALGESTER',  'Algester Veterinary Hospital',  12, 'Seeded 2026-07-22 from VSA Supabase public.hospital_codes'),
    (1, 'COMPTONRD', 'Compton Road Veterinary Hospital', 12, 'Seeded 2026-07-22 from VSA Supabase public.hospital_codes'),
    (1, 'MTGRAVATT', 'Mt Gravatt Veterinary Hospital', 12, 'Seeded 2026-07-22 from VSA Supabase public.hospital_codes'),
    (1, 'WINDAROO',  'Windaroo Veterinary Hospital',   12, 'Seeded 2026-07-22 from VSA Supabase public.hospital_codes'),
    (1, 'UNKNOWN',   'Unclassified hospital code',    12, 'Seeded 2026-07-22 - catch-all for rows with no hospital_code set')
ON CONFLICT (organisation_id, hospital_code) DO NOTHING;

-- Verify
DO $$
DECLARE
    row_count INTEGER;
    org_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count FROM ai_infrastructure.vsa_org_hospitals;
    SELECT COUNT(DISTINCT organisation_id) INTO org_count FROM ai_infrastructure.vsa_org_hospitals;
    RAISE NOTICE 'vsa_org_hospitals: % rows across % organisation(s)', row_count, org_count;
END $$;
