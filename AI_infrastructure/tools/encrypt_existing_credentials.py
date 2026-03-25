"""
tools/encrypt_existing_credentials.py

One-time script to encrypt all existing plaintext credential values in
organisation_platform_credentials (GAP-L7).

Run this AFTER setting CREDENTIAL_ENCRYPTION_KEY in your .env file.
Rows that already start with "enc:v1:" are skipped (idempotent).

Usage:
    cd AI_agents
    python AI_infrastructure/tools/encrypt_existing_credentials.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from AI_infrastructure.shared.database_utils import execute_query
from AI_infrastructure.shared.credential_crypto import encrypt_credential, is_encryption_enabled

ENC_PREFIX = "enc:v1:"


def main():
    if not is_encryption_enabled():
        print("ERROR: CREDENTIAL_ENCRYPTION_KEY is not set or invalid.")
        print("Set it in your .env file and retry.")
        sys.exit(1)

    rows = execute_query(
        """
        SELECT id, credential_value
        FROM   ai_infrastructure.organisation_platform_credentials
        WHERE  credential_value IS NOT NULL
          AND  credential_value != ''
          AND  credential_value NOT LIKE 'enc:v1:%%'
        """,
        fetch_mode='all'
    ) or []

    if not rows:
        print("No plaintext credentials found — nothing to encrypt.")
        return

    print(f"Found {len(rows)} unencrypted credential rows. Encrypting...")
    updated = 0
    for row in rows:
        encrypted = encrypt_credential(row['credential_value'])
        execute_query(
            "UPDATE ai_infrastructure.organisation_platform_credentials "
            "SET credential_value = %s, updated_at = NOW() WHERE id = %s",
            (encrypted, row['id'])
        )
        updated += 1

    print(f"Done — encrypted {updated} credential rows.")


if __name__ == '__main__':
    main()
