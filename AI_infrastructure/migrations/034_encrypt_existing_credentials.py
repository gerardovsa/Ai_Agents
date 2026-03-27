"""
Migration 034: Encrypt existing plaintext credential values at rest (GAP-L7)

PURPOSE:
    Finds all rows in organisation_platform_credentials that still hold a
    plaintext credential_value (i.e. no 'enc:v1:' prefix) and re-encrypts
    them using the Fernet key configured in CREDENTIAL_ENCRYPTION_KEY.

PREREQUISITES:
    1. Set CREDENTIAL_ENCRYPTION_KEY in your .env file:
           python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    2. Keep the key in a secure secrets manager (never commit it to git).

IDEMPOTENT:
    Already-encrypted values (prefixed with 'enc:v1:') are skipped.
    Safe to run multiple times.

ROLLBACK:
    If you need to decrypt all values back to plaintext, unset
    CREDENTIAL_ENCRYPTION_KEY and re-run with --decrypt flag (see below).
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query
from shared.credential_crypto import encrypt_credential, decrypt_credential, is_encryption_enabled

_ENC_PREFIX = 'enc:v1:'


def encrypt_existing(dry_run: bool = False) -> None:
    if not is_encryption_enabled():
        print("WARNING: CREDENTIAL_ENCRYPTION_KEY is not set.")
        print("  Set it in .env and re-run to encrypt stored values.")
        print("  Generate a key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        return

    rows = execute_query(
        """
        SELECT id, credential_value
        FROM ai_infrastructure.organisation_platform_credentials
        WHERE credential_value IS NOT NULL
          AND credential_value != ''
          AND credential_value NOT LIKE 'enc:v1:%'
        """,
        fetch_mode='all'
    ) or []

    if not rows:
        print("OK: No plaintext credentials found — all values are already encrypted or empty.")
        return

    print(f"Found {len(rows)} plaintext credential(s) to encrypt.")
    if dry_run:
        print("DRY RUN — no changes written.")
        for r in rows:
            print(f"  Would encrypt id={r['id']}")
        return

    ok = fail = 0
    for row in rows:
        try:
            encrypted = encrypt_credential(row['credential_value'])
            execute_query(
                "UPDATE ai_infrastructure.organisation_platform_credentials "
                "SET credential_value = %s WHERE id = %s",
                (encrypted, row['id'])
            )
            print(f"  Encrypted id={row['id']}")
            ok += 1
        except Exception as e:
            print(f"  FAILED id={row['id']}: {e}")
            fail += 1

    print(f"\nDone: {ok} encrypted, {fail} failed.")


def decrypt_existing(dry_run: bool = False) -> None:
    """Reverse operation — strips encryption back to plaintext.
    Only useful when rotating to a new encryption scheme or removing encryption.
    """
    if not is_encryption_enabled():
        print("WARNING: CREDENTIAL_ENCRYPTION_KEY not set — cannot decrypt.")
        return

    rows = execute_query(
        """
        SELECT id, credential_value
        FROM ai_infrastructure.organisation_platform_credentials
        WHERE credential_value LIKE 'enc:v1:%'
        """,
        fetch_mode='all'
    ) or []

    if not rows:
        print("OK: No encrypted credentials found.")
        return

    print(f"Found {len(rows)} encrypted credential(s) to decrypt.")
    if dry_run:
        print("DRY RUN — no changes written.")
        for r in rows:
            print(f"  Would decrypt id={r['id']}")
        return

    ok = fail = 0
    for row in rows:
        try:
            plaintext = decrypt_credential(row['credential_value'])
            if not plaintext:
                print(f"  SKIP id={row['id']} — decryption returned empty (wrong key?)")
                fail += 1
                continue
            execute_query(
                "UPDATE ai_infrastructure.organisation_platform_credentials "
                "SET credential_value = %s WHERE id = %s",
                (plaintext, row['id'])
            )
            print(f"  Decrypted id={row['id']}")
            ok += 1
        except Exception as e:
            print(f"  FAILED id={row['id']}: {e}")
            fail += 1

    print(f"\nDone: {ok} decrypted, {fail} failed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migration 034 — credential encryption at rest')
    parser.add_argument('--decrypt', action='store_true', help='Reverse: strip encryption back to plaintext')
    parser.add_argument('--dry-run', action='store_true', help='Report what would change without writing')
    args = parser.parse_args()

    if args.decrypt:
        decrypt_existing(dry_run=args.dry_run)
    else:
        encrypt_existing(dry_run=args.dry_run)
