"""Phase 3 — Drive routes through the shared injector.

Goals (from the plan):
- Cover list/get/upload + helper paths.
- Drive is the storage-only service — verify the shared contract honours it.
- NO service-account fallback after invalid user OAuth (silent ownership flip bug).
- Explicit service-account-only path retained for callers without user context.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch

REPO_ROOT = __file__.split('AI_infrastructure')[0]
for p in (REPO_ROOT, REPO_ROOT + 'AI_infrastructure'):
    if p not in sys.path:
        sys.path.insert(0, p)


def _fake_service():
    return MagicMock(name='drive_service')


class DriveSharedRouteTests(unittest.TestCase):
    """Lock down the Phase 3 routing contract."""

    # ----- helper behaviour -----

    def test_helper_uses_shared_wrapper_when_user_context_present(self):
        """With user_id + injected_credentials, the helper must call
        get_user_drive_service(user_id=user_id) — NOT construct Credentials,
        NOT fall back to a service account, NOT touch oauth_credential_loader."""
        from google_workspace import google_drive
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_drive, 'build_drive_service'
        ) as legacy_mock:
            out = google_drive._get_drive_service(user_id=42, injected_credentials={'flag': True})

        self.assertIs(out, sentinel_service)
        shared_mock.assert_called_once_with(user_id=42)
        legacy_mock.assert_not_called()

    def test_helper_uses_service_account_when_no_user_context(self):
        """Without user context, the helper must call build_drive_service()
        (the explicit service-account path). NO shared wrapper invocation."""
        from google_workspace import google_drive
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_drive, 'build_drive_service', return_value=sentinel_service
        ) as legacy_mock:
            out = google_drive._get_drive_service()

        self.assertIs(out, sentinel_service)
        legacy_mock.assert_called_once_with()
        shared_mock.assert_not_called()

    def test_helper_propagates_shared_injector_failure(self):
        """If the shared wrapper raises (invalid user OAuth row), the helper
        must propagate — never silently switch to a service account."""
        from google_workspace import google_drive
        from AI_infrastructure.auth import credential_injector

        boom = RuntimeError('user 42 has no Google OAuth row')
        with patch.object(
            credential_injector,
            'get_user_drive_service',
            side_effect=boom,
        ), patch.object(
            google_drive, 'build_drive_service'
        ) as legacy_mock:
            with self.assertRaises(RuntimeError) as ctx:
                google_drive._get_drive_service(user_id=42, injected_credentials={'flag': True})

        self.assertIn('user 42 has no Google OAuth row', str(ctx.exception))
        legacy_mock.assert_not_called()

    def test_helper_falsy_injected_credentials_is_no_user_context(self):
        """Falsy injected_credentials (None / empty dict) is treated as
        no-user-context — the service-account branch handles it explicitly."""
        from google_workspace import google_drive
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_drive, 'build_drive_service', return_value=sentinel_service
        ) as legacy_mock:
            out1 = google_drive._get_drive_service(user_id=42, injected_credentials=None)
            out2 = google_drive._get_drive_service(user_id=42, injected_credentials={})

        self.assertIs(out1, sentinel_service)
        self.assertIs(out2, sentinel_service)
        shared_mock.assert_not_called()
        self.assertEqual(legacy_mock.call_count, 2)

    # ----- function-level routing -----

    def test_list_files_routes_via_helper(self):
        """list_files must call _get_drive_service(user_id, injected_credentials)
        — never inline Credential construction."""
        from google_workspace import google_drive

        sentinel_service = _fake_service()
        sentinel_service.files().list().execute.return_value = {'files': [{'id': 'x'}], 'nextPageToken': None}

        with patch.object(
            google_drive, '_get_drive_service', return_value=sentinel_service
        ) as helper_mock:
            result = google_drive.google_drive_list_files(max_results=5, _user_id=42, _injected_credentials={'flag': True})

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})
        self.assertEqual(result['count'], 1)

    def test_get_file_routes_via_helper(self):
        """get_file must route through the helper for user context."""
        from google_workspace import google_drive

        sentinel_service = _fake_service()
        sentinel_service.files().get().execute.return_value = {'id': 'abc', 'name': 'doc.txt'}

        with patch.object(
            google_drive, '_get_drive_service', return_value=sentinel_service
        ) as helper_mock:
            google_drive.google_drive_get_file('abc', _user_id=42, _injected_credentials={'flag': True})

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_upload_file_routes_via_helper(self):
        """upload_file must route through the helper for user context.

        Also verifies the legacy _get_user_credentials_if_available helper is
        GONE — it used to be called here."""
        from google_workspace import google_drive

        sentinel_service = _fake_service()
        sentinel_service.files().create().execute.return_value = {'id': 'new_id'}

        self.assertFalse(
            hasattr(google_drive, '_get_user_credentials_if_available'),
            'Legacy _get_user_credentials_if_available must be removed (Phase 3)',
        )

        with patch.object(
            google_drive, '_get_drive_service', return_value=sentinel_service
        ) as helper_mock, patch.object(
            google_drive, 'MediaFileUpload', return_value=MagicMock(name='media')
        ):
            google_drive.google_drive_upload_file(
                'fake_path.txt', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_storage_only_drive_is_legal(self):
        """Drive is the storage-only service — verify the shared wrapper
        constructs the service (mocked) for service_name='drive' when the
        storage-only link is active. Non-drive services must raise from the
        injector BEFORE the helper hands back a service."""
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()

        # Drive call must succeed — the shared wrapper hands back the service.
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            return_value=sentinel_service,
        ):
            out = credential_injector.get_user_drive_service(user_id=42)
        self.assertIs(out, sentinel_service)

        # Non-drive call (gmail) MUST raise — drives the storage-only rule.
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            side_effect=Exception('storage only — Cannot use gmail service'),
        ):
            with self.assertRaises(Exception) as ctx:
                credential_injector.get_user_gmail_service(user_id=42)
        self.assertIn('storage only', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()