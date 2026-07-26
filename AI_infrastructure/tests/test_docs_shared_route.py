"""Phase 4 — Docs routes user Docs v1 + Drive v3 sidecars through the shared injector.

Goals (from the plan):
- Cover representative user-context Docs tool entry points.
- User-owned Drive sidecars (make-shareable, docx-conversion-v2 upload,
  export-as-pdf/html/markdown template-copy) must route through
  get_user_drive_service.
- Intentional service-account-only paths (chart builders) must keep using
  build_drive_service() / build('sheets', v4, ...) directly.
- NO service-account fallback after a missing/invalid user OAuth row.
- Storage-only rule: get_user_docs_service() must NOT be allowed when
  link_purpose != 'storage' (Docs is not a storage service — only Drive is).
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


class DocsSharedRouteTests(unittest.TestCase):
    """Lock down the Phase 4 routing contract for google_docs.py."""

    # ----- _get_docs_service helper -----

    def test_helper_uses_shared_wrapper_when_user_context_present(self):
        """With user_id + injected_credentials, the helper must call
        get_user_docs_service(user_id=user_id). No inline Credentials construction."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_docs_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_docs, 'build_docs_service'
        ) as legacy_mock:
            out = google_docs._get_docs_service(user_id=42, injected_credentials={'flag': True})

        self.assertIs(out, sentinel_service)
        shared_mock.assert_called_once_with(user_id=42)
        legacy_mock.assert_not_called()

    def test_helper_uses_service_account_when_no_user_context(self):
        """Without user context, the helper must call build_docs_service()
        (the explicit service-account path)."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_docs_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_docs, 'build_docs_service', return_value=sentinel_service
        ) as legacy_mock:
            out = google_docs._get_docs_service()

        self.assertIs(out, sentinel_service)
        legacy_mock.assert_called_once_with()
        shared_mock.assert_not_called()

    def test_helper_propagates_shared_injector_failure(self):
        """If the shared wrapper raises (no user OAuth row), the helper must
        propagate — NEVER silently switch to a service account."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        boom = RuntimeError('user 42 has no Google OAuth row')
        with patch.object(
            credential_injector,
            'get_user_docs_service',
            side_effect=boom,
        ), patch.object(
            google_docs, 'build_docs_service'
        ) as legacy_mock:
            with self.assertRaises(RuntimeError) as ctx:
                google_docs._get_docs_service(user_id=42, injected_credentials={'flag': True})

        self.assertIn('user 42 has no Google OAuth row', str(ctx.exception))
        legacy_mock.assert_not_called()

    def test_helper_falsy_injected_credentials_is_no_user_context(self):
        """Falsy injected_credentials (None / empty dict) is treated as
        no-user-context — the service-account branch handles it explicitly."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_docs_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_docs, 'build_docs_service', return_value=sentinel_service
        ) as legacy_mock:
            out1 = google_docs._get_docs_service(user_id=42, injected_credentials=None)
            out2 = google_docs._get_docs_service(user_id=42, injected_credentials={})

        self.assertIs(out1, sentinel_service)
        self.assertIs(out2, sentinel_service)
        shared_mock.assert_not_called()
        self.assertEqual(legacy_mock.call_count, 2)

    # ----- function-level routing -----

    def test_create_document_routes_via_helper(self):
        """google_docs_create_document must call _get_docs_service(user_id, injected_credentials)
        — never the legacy _get_user_credentials_if_available."""
        from google_workspace import google_docs

        sentinel_service = _fake_service()
        sentinel_service.documents().create().execute.return_value = {
            'documentId': 'new_id', 'title': 't', 'revisionId': 'r1',
        }
        sentinel_service.permissions().create().execute.return_value = {'id': 'p1'}

        self.assertFalse(
            hasattr(google_docs, '_get_user_credentials_if_available'),
            'Legacy _get_user_credentials_if_available must be removed (Phase 4)',
        )

        with patch.object(
            google_docs, '_get_docs_service', return_value=sentinel_service
        ) as helper_mock:
            google_docs.google_docs_create_document(
                'Hello Doc', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_get_document_routes_via_helper(self):
        """google_docs_get_document must route through the helper."""
        from google_workspace import google_docs

        sentinel_service = _fake_service()
        sentinel_service.documents().get().execute.return_value = {
            'title': 'T', 'body': {'content': []}, 'revisionId': 'r',
        }

        with patch.object(
            google_docs, '_get_docs_service', return_value=sentinel_service
        ) as helper_mock:
            google_docs.google_docs_get_document(
                'doc_id', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_batch_update_routes_via_helper(self):
        """google_docs_batch_update must route through the helper."""
        from google_workspace import google_docs

        sentinel_service = _fake_service()
        sentinel_service.documents().batchUpdate().execute.return_value = {'replies': []}

        with patch.object(
            google_docs, '_get_docs_service', return_value=sentinel_service
        ) as helper_mock:
            google_docs.google_docs_batch_update(
                'doc_id', [], _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_make_shareable_routes_through_shared_drive_wrapper(self):
        """_make_google_doc_shareable must route through get_user_drive_service
        when user context is present, never through build_drive_service(user_id=...)."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        sentinel_service.permissions().create().execute.return_value = {'id': 'p1'}
        sentinel_service.files().get().execute.return_value = {
            'webViewLink': 'https://docs.google.com/x',
        }

        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_docs, 'build_drive_service'
        ) as legacy_mock:
            result = google_docs._make_google_doc_shareable(
                'doc_id', user_id=42, injected_credentials={'flag': True},
            )

        self.assertTrue(result['success'])
        shared_mock.assert_called_once_with(user_id=42)
        legacy_mock.assert_not_called()

    def test_make_shareable_uses_service_account_when_no_user_context(self):
        """_make_google_doc_shareable must fall through to explicit
        build_drive_service() when no user context is supplied."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        sentinel_service.permissions().create().execute.return_value = {'id': 'p1'}
        sentinel_service.files().get().execute.return_value = {
            'webViewLink': 'https://docs.google.com/x',
        }

        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_docs, 'build_drive_service', return_value=sentinel_service
        ) as legacy_mock:
            result = google_docs._make_google_doc_shareable('doc_id')

        self.assertTrue(result['success'])
        shared_mock.assert_not_called()
        legacy_mock.assert_called_once_with()

    # ----- storage-only rule -----

    def test_storage_only_rejects_docs_service(self):
        """Docs is NOT a storage service — get_user_docs_service() must
        raise from the injector BEFORE the helper hands back a service."""
        from AI_infrastructure.auth import credential_injector

        # Drive call must succeed.
        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            return_value=sentinel_service,
        ):
            out = credential_injector.get_user_drive_service(user_id=42)
        self.assertIs(out, sentinel_service)

        # Docs call MUST raise — storage-only rule.
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            side_effect=Exception('storage only — Cannot use docs service'),
        ):
            with self.assertRaises(Exception) as ctx:
                credential_injector.get_user_docs_service(user_id=42)
        self.assertIn('storage only', str(ctx.exception))

    # ----- explicit service-account paths are preserved -----

    def test_chart_path_uses_explicit_service_account(self):
        """google_charts_create must keep using the explicit service-account
        helper (build_drive_service() / build('sheets', v4, ...)) because
        charts do not carry a user context — no silent shared-wrapper swap."""
        from google_workspace import google_docs
        from AI_infrastructure.auth import credential_injector

        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=_fake_service(),
        ) as shared_drive_mock, patch.object(
            credential_injector,
            'get_user_docs_service',
            return_value=_fake_service(),
        ) as shared_docs_mock:
            # google_charts_create does NOT accept user context.
            self.assertNotIn('_user_id', google_docs.google_charts_create.__code__.co_varnames)
            # Shared wrappers must NOT be invoked.
            shared_drive_mock.assert_not_called()
            shared_docs_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()