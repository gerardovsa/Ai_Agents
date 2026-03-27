-- ============================================================
-- Migration 026: JWT Version Counter for Immediate Role Revocation
-- ============================================================
-- GAP-C4 FIX: When a user's org_role is changed or they are removed from
-- an org, their existing JWT remains valid for 30 days (the token expiry).
-- This migration adds a `jwt_version` counter to the users table.
--
-- HOW IT WORKS:
--   1. At login, `jwt_version` is read from the DB and embedded in the JWT.
--   2. On every authenticated request, `require_auth` decodes the JWT and
--      checks the DB's current `jwt_version` for that user.
--   3. If the DB version is higher than the token version, the token is
--      rejected with 401 ("Session expired — please log in again").
--   4. When an admin changes a user's role or removes them, the role-change
--      endpoint increments `jwt_version`, instantly invalidating all their
--      existing tokens.
--
-- IDEMPOTENT: Safe to run multiple times.
-- ============================================================

-- Add jwt_version column to users table (default 1 so existing users start valid)
ALTER TABLE ai_infrastructure.users
    ADD COLUMN IF NOT EXISTS jwt_version INTEGER NOT NULL DEFAULT 1;

-- Index for fast lookup during every authenticated request
CREATE INDEX IF NOT EXISTS idx_users_jwt_version
    ON ai_infrastructure.users (id, jwt_version);

COMMENT ON COLUMN ai_infrastructure.users.jwt_version IS
    'Monotonic counter incremented on role changes / org removal. '
    'JWT tokens carry this value; if DB > token, the token is rejected.';
