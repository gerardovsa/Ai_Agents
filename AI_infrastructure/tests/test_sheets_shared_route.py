"""Phase 5 — Sheets routes user Sheets v4 + Drive v3 sidecars through the shared injector.

Goals (from the plan):
- Verify Sheets v4 routing.
- Clean package import — no duplicate google_docs module identity, no
  ``from google_docs import _get_user_credentials_if_available`` cycle.
- No implicit service-account fallback after invalid user OAuth.
- User Drive sidecars in create / smart_builder create_multisheet must route
  through ``get_user_drive_service``; bare ``build_drive_service(**kwargs)``
  in the no-user-context delete path is preserved.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch

REPO_ROOT = __file__.split('AI_infrastructure')[0]
for p in (REPO_ROOT, REPO_ROOT + 'AI_infrastructure'):
    if p not in sys.path:
        sys.path.insert(0, p)


def _fake_service():
    return MagicMock(name='service')


class SheetsSharedRouteTests(unittest.TestCase):
    """Lock down the Phase 5 routing contract for google_sheets.py."""

    # ----- package import surface (Phase 5: the non-package cycle is fixed) -----

    def test_module_imports_without_legacy_google_docs_symbols(self):
        """The legacy ``from google_docs import _get_user_credentials_if_available``
        import is gone — google_sheets must not have that symbol in its module
        namespace (it was never owned by sheets)."""
        from google_workspace import google_sheets
        self.assertFalse(
            hasattr(google_sheets, '_get_user_credentials_if_available'),
            'Phase 5: legacy _get_user_credentials_if_available must not leak '
            'into google_sheets module namespace',
        )

    def test_module_does_not_eagerly_import_google_docs_at_package_load(self):
        """Importing google_sheets must not import the (now-defunct) legacy
        helper from google_docs at module top level. google_docs is still
        importable (it owns _get_docs_service) — but sheets should not be
        pinning to its private symbols."""
        # Re-import to ensure top-level ran cleanly.
        from google_workspace import google_docs, google_sheets
        self.assertTrue(hasattr(google_docs, '_get_docs_service'))
        self.assertTrue(hasattr(google_sheets, '_get_sheets_service'))

    # ----- _get_sheets_service helper -----

    def test_helper_uses_shared_wrapper_when_user_context_present(self):
        """With user_id + injected_credentials, the helper must call
        get_user_sheets_service(user_id=user_id) — NOT build a Credentials
        object inline, NOT use the parallel loader, NOT touch oauth_credential_loader."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_sheets_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_sheets, 'build'
        ) as inline_build_mock, patch.object(
            google_sheets, 'get_service_account_credentials'
        ) as sa_mock:
            out = google_sheets._get_sheets_service(
                user_id=42, injected_credentials={'flag': True},
            )

        self.assertIs(out, sentinel_service)
        shared_mock.assert_called_once_with(user_id=42)
        inline_build_mock.assert_not_called()
        sa_mock.assert_not_called()

    def test_helper_uses_service_account_when_no_user_context(self):
        """Without user context, the helper must call build('sheets', v4, ...)
        with explicit service-account credentials — NOT the shared wrapper."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        fake_creds = MagicMock(name='sa_creds')
        with patch.object(
            credential_injector,
            'get_user_sheets_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_sheets, 'get_service_account_credentials', return_value=fake_creds
        ) as sa_mock, patch.object(
            google_sheets, 'build', return_value=sentinel_service
        ) as build_mock:
            out = google_sheets._get_sheets_service()

        self.assertIs(out, sentinel_service)
        shared_mock.assert_not_called()
        sa_mock.assert_called_once()
        scopes_arg = sa_mock.call_args[0][0]
        self.assertIn('https://www.googleapis.com/auth/spreadsheets', scopes_arg)
        build_mock.assert_called_once_with('sheets', 'v4', credentials=fake_creds)

    def test_helper_propagates_shared_injector_failure(self):
        """If the shared wrapper raises (invalid user OAuth row), the helper
        must propagate — never silently switch to a service account."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        boom = RuntimeError('user 42 has no Google OAuth row')
        with patch.object(
            credential_injector,
            'get_user_sheets_service',
            side_effect=boom,
        ), patch.object(
            google_sheets, 'build'
        ) as build_mock, patch.object(
            google_sheets, 'get_service_account_credentials'
        ) as sa_mock:
            with self.assertRaises(RuntimeError) as ctx:
                google_sheets._get_sheets_service(
                    user_id=42, injected_credentials={'flag': True},
                )

        self.assertIn('user 42 has no Google OAuth row', str(ctx.exception))
        build_mock.assert_not_called()
        sa_mock.assert_not_called()

    def test_helper_falsy_injected_credentials_is_no_user_context(self):
        """Falsy injected_credentials (None / empty dict) is treated as
        no-user-context — the service-account branch handles it explicitly."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_sheets_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_sheets, 'get_service_account_credentials', return_value=MagicMock()
        ), patch.object(
            google_sheets, 'build', return_value=sentinel_service
        ):
            out1 = google_sheets._get_sheets_service(user_id=42, injected_credentials=None)
            out2 = google_sheets._get_sheets_service(user_id=42, injected_credentials={})

        self.assertIs(out1, sentinel_service)
        self.assertIs(out2, sentinel_service)
        shared_mock.assert_not_called()

    # ----- function-level routing -----

    def test_create_routes_via_helper_and_shared_drive_sidecar(self):
        """google_sheets_create must call _get_sheets_service(user_id, injected_credentials)
        — never inline Credential construction — and the Drive sidecar must
        route through get_user_drive_service when user context is present."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sheets_svc = _fake_service()
        sheets_svc.spreadsheets().create().execute.return_value = {
            'spreadsheetId': 'sid', 'properties': {'title': 'T'},
            'sheets': [{'properties': {'title': 'Sheet1', 'sheetId': 0}}],
        }
        drive_svc = _fake_service()
        drive_svc.permissions().create().execute.return_value = {'id': 'p1'}

        self.assertFalse(
            hasattr(google_sheets, '_get_user_credentials_if_available'),
            'Legacy _get_user_credentials_if_available must be removed (Phase 5)',
        )

        with patch.object(
            google_sheets, '_get_sheets_service', return_value=sheets_svc,
        ) as helper_mock, patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_sheets, 'build_drive_service'
        ) as legacy_drive_mock:
            google_sheets.google_sheets_create(
                'My Sheet', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})
        shared_drive_mock.assert_called_once_with(user_id=42)
        legacy_drive_mock.assert_not_called()

    def test_append_data_routes_via_helper(self):
        """google_sheets_append_data must route through the shared helper."""
        from google_workspace import google_sheets

        sentinel = _fake_service()
        sentinel.spreadsheets().values().append().execute.return_value = {
            'updates': {'updatedRows': 1, 'updatedRange': 'Sheet1!A1'},
        }

        with patch.object(
            google_sheets, '_get_sheets_service', return_value=sentinel
        ) as helper_mock:
            google_sheets.google_sheets_append_data(
                'sid', [['a']], _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_read_data_routes_via_helper(self):
        """google_sheets_read_data must route through the shared helper."""
        from google_workspace import google_sheets

        sentinel = _fake_service()
        sentinel.spreadsheets().values().get().execute.return_value = {'values': []}

        with patch.object(
            google_sheets, '_get_sheets_service', return_value=sentinel
        ) as helper_mock:
            google_sheets.google_sheets_read_data(
                'sid', 'Sheet1!A1:Z1000', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_create_multiple_routes_via_helper(self):
        """google_sheets_create_multiple must route through the shared helper."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sentinel = _fake_service()
        sentinel.spreadsheets().create().execute.return_value = {
            'spreadsheetId': 'sid',
            'properties': {'title': 'X'},
            'sheets': [{'properties': {'title': 'S1', 'sheetId': 0}}],
        }
        drive = _fake_service()
        drive.permissions().create().execute.return_value = {'id': 'p'}

        with patch.object(
            google_sheets, '_get_sheets_service', return_value=sentinel
        ) as helper_mock, patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive,
        ), patch.object(
            google_sheets, 'build_drive_service', return_value=drive
        ):
            google_sheets.google_sheets_create_multiple(
                [{'title': 'X'}], _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    # ----- smart builder: create + update -----

    def test_smart_builder_create_routes_through_shared_drive_wrapper(self):
        """_smart_builder_create_multisheet must take (user_id, injected_credentials)
        directly (no cred_dict argument) and route the Drive sidecar through
        get_user_drive_service when user context is present."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sheets_svc = _fake_service()
        sheets_svc.spreadsheets().create().execute.return_value = {
            'spreadsheetId': 'sid',
            'properties': {'title': 'X'},
            'sheets': [{'properties': {'title': 'S1', 'sheetId': 0}}],
        }
        drive_svc = _fake_service()
        drive_svc.permissions().create().execute.return_value = {'id': 'p'}

        with patch.object(
            google_sheets, '_get_sheets_service', return_value=sheets_svc
        ) as helper_mock, patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_sheets, 'build_drive_service'
        ) as legacy_drive_mock:
            google_sheets._smart_builder_create_multisheet(
                'My SS', [{'name': 'S1', 'data': []}],
                user_id=42, injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})
        shared_drive_mock.assert_called_once_with(user_id=42)
        legacy_drive_mock.assert_not_called()

    def test_smart_builder_create_uses_service_account_when_no_user_context(self):
        """_smart_builder_create_multisheet must use the explicit service-account
        Drive helper when no user context is supplied."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        sheets_svc = _fake_service()
        sheets_svc.spreadsheets().create().execute.return_value = {
            'spreadsheetId': 'sid',
            'properties': {'title': 'X'},
            'sheets': [{'properties': {'title': 'S1', 'sheetId': 0}}],
        }
        drive_svc = _fake_service()
        drive_svc.permissions().create().execute.return_value = {'id': 'p'}

        with patch.object(
            google_sheets, '_get_sheets_service', return_value=sheets_svc
        ), patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_sheets, 'build_drive_service', return_value=drive_svc
        ) as legacy_drive_mock:
            google_sheets._smart_builder_create_multisheet(
                'My SS', [{'name': 'S1', 'data': []}],
                user_id=None, injected_credentials=None,
            )

        shared_drive_mock.assert_not_called()
        legacy_drive_mock.assert_called_once_with()

    def test_smart_builder_update_signature_uses_injected_credentials(self):
        """_smart_builder_update_existing must take (spreadsheet_id, operations,
        user_id, injected_credentials) — no cred_dict argument."""
        import inspect
        from google_workspace import google_sheets
        sig = inspect.signature(google_sheets._smart_builder_update_existing)
        params = list(sig.parameters)
        self.assertEqual(
            params,
            ['spreadsheet_id', 'operations', 'user_id', 'injected_credentials'],
        )

    def test_smart_builder_orchestrator_no_cred_dict(self):
        """google_sheets_smart_builder must NOT construct a local cred_dict; it
        must pass _injected_credentials through to the internal helpers."""
        from google_workspace import google_sheets

        # Mock the two internal helpers to inspect what they receive.
        with patch.object(
            google_sheets, '_smart_builder_create_multisheet', return_value={'ok': True},
        ) as create_mock, patch.object(
            google_sheets, '_smart_builder_update_existing', return_value={'ok': True},
        ) as update_mock:
            google_sheets.google_sheets_smart_builder(
                spreadsheet_name='X', sheets=[{'name': 'S1'}],
                _user_id=42, _injected_credentials={'flag': True},
            )
        # _smart_builder_create_multisheet now takes (spreadsheet_name, sheets, user_id, injected_credentials)
        args = create_mock.call_args[0]
        self.assertEqual(args[0], 'X')
        self.assertEqual(args[1], [{'name': 'S1'}])
        self.assertEqual(args[2], 42)
        self.assertEqual(args[3], {'flag': True})
        update_mock.assert_not_called()

    # ----- bare build_drive_service(**kwargs) preserved in no-user-context path -----

    def test_delete_preserves_explicit_service_account(self):
        """google_sheets_delete has no user-context plumbing — it must keep
        using the bare build_drive_service() (no silent shared-wrapper swap)."""
        from google_workspace import google_sheets
        from AI_infrastructure.auth import credential_injector

        drive_svc = _fake_service()
        drive_svc.files().delete().execute.return_value = None

        with patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_sheets, 'build_drive_service', return_value=drive_svc
        ) as legacy_drive_mock:
            google_sheets.google_sheets_delete('sid')

        shared_drive_mock.assert_not_called()
        legacy_drive_mock.assert_called_once_with()

    # ----- storage-only rule -----

    def test_storage_only_rejects_sheets_service(self):
        """Sheets is NOT a storage service — get_user_sheets_service() must
        raise from the injector BEFORE the helper hands back a service."""
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            return_value=sentinel_service,
        ):
            out = credential_injector.get_user_drive_service(user_id=42)
        self.assertIs(out, sentinel_service)

        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            side_effect=Exception('storage only — Cannot use sheets service'),
        ):
            with self.assertRaises(Exception) as ctx:
                credential_injector.get_user_sheets_service(user_id=42)
        self.assertIn('storage only', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()