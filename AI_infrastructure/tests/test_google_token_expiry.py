"""Regression tests for Google OAuth token-expiry normalization."""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

AI_INFRASTRUCTURE_DIR = Path(__file__).resolve().parents[1]
if str(AI_INFRASTRUCTURE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_INFRASTRUCTURE_DIR))

from auth.credential_injector import (
    Credentials,
    _parse_google_token_expiry,
    _save_refreshed_google_token,
    _should_refresh_google_token,
    create_google_service_with_user_credentials,
)


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

    def test_refreshes_inside_proactive_threshold(self):
        expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=4)

        self.assertTrue(_should_refresh_google_token(expiry, threshold_seconds=300))

    def test_does_not_refresh_outside_proactive_threshold(self):
        expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)

        self.assertFalse(_should_refresh_google_token(expiry, threshold_seconds=300))

    def test_missing_expiry_requests_refresh(self):
        self.assertTrue(_should_refresh_google_token(None))

    def test_invalid_expiry_returns_none(self):
        self.assertIsNone(_parse_google_token_expiry("not-a-datetime"))
        self.assertIsNone(_parse_google_token_expiry(None))


class GoogleServiceContractTests(unittest.TestCase):
    @staticmethod
    def _credential_dict(link_purpose="primary"):
        return {
            "token_id": 42,
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "scopes": ["scope"],
            "expires_at": "2099-07-24T05:03:52Z",
            "link_purpose": link_purpose,
        }

    def test_storage_only_credentials_reject_gmail_before_build(self):
        auth_manager = mock.MagicMock()
        auth_manager.get_user_google_oauth_credentials.return_value = self._credential_dict("storage")
        encryptor = mock.MagicMock()
        encryptor.decrypt_dict.side_effect = lambda value: dict(value)

        with mock.patch(
            "auth.credential_injector.UserAuthManager",
            return_value=auth_manager,
        ), mock.patch(
            "AI_infrastructure.auth.credential_encryptor.get_encryptor",
            return_value=encryptor,
        ), mock.patch("auth.credential_injector.build") as build:
            with self.assertRaisesRegex(Exception, "storage only"):
                create_google_service_with_user_credentials(7, "gmail", "v1")

        build.assert_not_called()

    def test_future_token_returns_validated_status(self):
        auth_manager = mock.MagicMock()
        auth_manager.get_user_google_oauth_credentials.return_value = self._credential_dict()
        encryptor = mock.MagicMock()
        encryptor.decrypt_dict.side_effect = lambda value: dict(value)
        service = object()

        with mock.patch(
            "auth.credential_injector.UserAuthManager",
            return_value=auth_manager,
        ), mock.patch(
            "AI_infrastructure.auth.credential_encryptor.get_encryptor",
            return_value=encryptor,
        ), mock.patch(
            "auth.credential_injector.build",
            return_value=service,
        ):
            result = create_google_service_with_user_credentials(
                7,
                "gmail",
                "v1",
                return_refresh_status=True,
            )

        self.assertEqual(result, (service, "validated"))


class GoogleTokenPersistenceTests(unittest.TestCase):
    def test_refresh_updates_exact_row_and_preserves_refresh_token(self):
        cursor = mock.MagicMock()
        cursor.rowcount = 1
        connection = mock.MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        encryptor = mock.MagicMock()
        encryptor.is_encrypted.return_value = False
        credentials = SimpleNamespace(
            token="new-access-token",
            refresh_token=None,
            expiry=datetime(2099, 7, 24, 5, 3, 52),
        )
        original = {
            "token_id": 42,
            "refresh_token": "existing-refresh-token",
        }
        stored = {
            "access_token": "old-access-token",
            "refresh_token": "existing-refresh-token",
        }

        with mock.patch(
            "auth.credential_injector.get_connection",
            return_value=connection,
        ), mock.patch(
            "AI_infrastructure.auth.credential_encryptor.get_encryptor",
            return_value=encryptor,
        ):
            _save_refreshed_google_token(7, credentials, original, stored)

        sql, params = cursor.execute.call_args.args
        self.assertIn("WHERE id = %s", sql)
        self.assertIn("ai_infrastructure.oauth_tokens", sql)
        self.assertEqual(params[1], "existing-refresh-token")
        self.assertEqual(params[-2:], (42, 7))
        connection.commit.assert_called_once_with()

    def test_refresh_persistence_requires_selected_row_id(self):
        credentials = SimpleNamespace(token="new", refresh_token="refresh", expiry=None)

        with self.assertRaisesRegex(ValueError, "row ID is missing"):
            _save_refreshed_google_token(7, credentials, {}, {})


if __name__ == "__main__":
    unittest.main()
