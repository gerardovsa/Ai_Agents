-- ============================================================================
-- Migration 060: Store Detected Location Coordinates
-- Created: 2026-07-24
-- Purpose: Persist login-time latitude and longitude for weather context without
--          repeating IP geolocation during chat requests.
-- Idempotent: Yes; columns are added only when absent.
-- ============================================================================

ALTER TABLE ai_infrastructure.user_preferences
    ADD COLUMN IF NOT EXISTS detected_latitude DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS detected_longitude DOUBLE PRECISION;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name = 'user_preferences'
          AND column_name = 'detected_latitude'
    ) AND EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name = 'user_preferences'
          AND column_name = 'detected_longitude'
    ) THEN
        RAISE NOTICE 'Migration 060 verified: detected location coordinates are available';
    ELSE
        RAISE EXCEPTION 'Migration 060 verification failed';
    END IF;
END $$;
