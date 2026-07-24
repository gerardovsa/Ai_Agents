"""Regression tests for Google OAuth token-expiry normalization."""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

AI_INFRASTRUCTURE_DIR = Path(__file__).resolve().parents[1]
if str(AI_INFRASTRUCTURE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_INFRASTRUCTURE_DIR))

from auth.credential_injector import Credentials, _parse_google_token_expiry


class GoogleTokenExpiryTests(unittest.TestCase):
    def test_z_suffix_is_converted_to_naive_utc(self):
        expiry = _parse_google_token_expiry("2026-07-24T05:03:52Z")

        self.assertEqual(expiry, datetime(2026, 7, 24, 5, 3, 52))
        self.assertIsNone(expiry.tzinfo)

    def test_offset_timestamp_is_shifted_to_naive_utc(self):
        expiry = _parse_google_token_expiry("2026-07-24T15:03:52+10:00")

        self.assertEqual(expiry, datetime(2026, 7, 24, 5, 3, 52))
        self.assertIsNone(expiry.tzinfo)

    def test_aware_datetime_is_converted_to_naive_utc(self):
        expires_at = datetime(2026, 7, 24, 5, 3, 52, tzinfo=timezone.utc)

        expiry = _parse_google_token_expiry(expires_at)

        self.assertEqual(expiry, datetime(2026, 7, 24, 5, 3, 52))
        self.assertIsNone(expiry.tzinfo)

    def test_naive_datetime_remains_naive(self):
        expires_at = datetime(2026, 7, 24, 5, 3, 52)

        self.assertIs(_parse_google_token_expiry(expires_at), expires_at)

    def test_normalized_expiry_is_compatible_with_google_auth_valid_check(self):
        expiry = _parse_google_token_expiry("2099-07-24T05:03:52Z")
        credentials = Credentials(token="test-token", expiry=expiry)

        self.assertTrue(credentials.valid)

    def test_invalid_expiry_returns_none(self):
        self.assertIsNone(_parse_google_token_expiry("not-a-datetime"))
        self.assertIsNone(_parse_google_token_expiry(None))


if __name__ == "__main__":
    unittest.main()
