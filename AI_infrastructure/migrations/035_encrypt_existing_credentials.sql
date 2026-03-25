-- Migration 035: Note about credential encryption (GAP-L7)
--
-- The application now encrypts new credential values using Fernet AES
-- (CREDENTIAL_ENCRYPTION_KEY env var). Existing plaintext values are
-- handled transparently at read-time via decrypt_credential(), which
-- returns them unchanged if they lack the "enc:v1:" prefix.
--
-- To encrypt existing rows, run the Python script below from the server:
--   python AI_infrastructure/tools/encrypt_existing_credentials.py
--
-- This SQL migration is informational only — no schema change is required.
-- The enc:v1: prefix acts as a self-describing format for forward compatibility.

DO $$
BEGIN
    RAISE NOTICE 'Migration 035: No schema changes needed.';
    RAISE NOTICE 'Credential encryption (GAP-L7) is handled at the application layer.';
    RAISE NOTICE 'New credentials are encrypted. Existing values are decrypted lazily (passthrough).';
    RAISE NOTICE 'Set CREDENTIAL_ENCRYPTION_KEY in .env to activate encryption.';
    RAISE NOTICE 'Run tools/encrypt_existing_credentials.py to encrypt existing rows.';
END $$;
