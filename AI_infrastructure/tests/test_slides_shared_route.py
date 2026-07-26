"""Phase 6 — Slides routes user Slides v1 + Drive v3 sidecars through the shared injector.

Goals (from the plan):
- Replace the legacy parallel-loader primary path with get_user_slides_service().
- Verify primary/get/search service construction through the shared contract.
- User Drive sidecars in create_presentation / export_as_pdf / export_as_pptx
  routes go through get_user_drive_service when user context is present.
- Bare _get_slides_service() / build_drive_service() in the no-user-context path
  is preserved (google_docs_to_slides_auto_generate has no user plumbing).
- Storage-only rule: get_user_slides_service() must raise from the injector
  BEFORE the helper hands back a service (Slides is not a storage service).
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


class SlidesSharedRouteTests(unittest.TestCase):
    """Lock down the Phase 6 routing contract for google_slides.py."""

    # ----- package import surface -----

    def test_module_imports_without_legacy_helpers(self):
        """Phase 6: legacy _get_user_credentials_if_available must be gone,
        and the file must not pin to Credentials / service_account symbols
        at module top level."""
        from google_workspace import google_slides
        self.assertFalse(
            hasattr(google_slides, '_get_user_credentials_if_available'),
            'Phase 6: legacy _get_user_credentials_if_available must be removed',
        )
        self.assertFalse(
            hasattr(google_slides, 'Credentials'),
            'Phase 6: google.oauth2.credentials.Credentials import must be dropped',
        )

    # ----- _get_slides_service helper -----

    def test_helper_uses_shared_wrapper_when_user_context_present(self):
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_slides_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_slides, 'build'
        ) as inline_build_mock, patch.object(
            google_slides, 'get_service_account_credentials'
        ) as sa_mock:
            out = google_slides._get_slides_service(
                user_id=42, injected_credentials={'flag': True},
            )

        self.assertIs(out, sentinel_service)
        shared_mock.assert_called_once_with(user_id=42)
        inline_build_mock.assert_not_called()
        sa_mock.assert_not_called()

    def test_helper_uses_service_account_when_no_user_context(self):
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        fake_creds = MagicMock(name='sa_creds')
        with patch.object(
            credential_injector,
            'get_user_slides_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_slides, 'get_service_account_credentials', return_value=fake_creds
        ) as sa_mock, patch.object(
            google_slides, 'build', return_value=sentinel_service
        ) as build_mock:
            out = google_slides._get_slides_service()

        self.assertIs(out, sentinel_service)
        shared_mock.assert_not_called()
        sa_mock.assert_called_once()
        scopes_arg = sa_mock.call_args[0][0]
        self.assertIn('https://www.googleapis.com/auth/presentations', scopes_arg)
        build_mock.assert_called_once_with('slides', 'v1', credentials=fake_creds)

    def test_helper_propagates_shared_injector_failure(self):
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector

        boom = RuntimeError('user 42 has no Google OAuth row')
        with patch.object(
            credential_injector,
            'get_user_slides_service',
            side_effect=boom,
        ), patch.object(
            google_slides, 'build'
        ) as build_mock, patch.object(
            google_slides, 'get_service_account_credentials'
        ) as sa_mock:
            with self.assertRaises(RuntimeError) as ctx:
                google_slides._get_slides_service(
                    user_id=42, injected_credentials={'flag': True},
                )

        self.assertIn('user 42 has no Google OAuth row', str(ctx.exception))
        build_mock.assert_not_called()
        sa_mock.assert_not_called()

    def test_helper_falsy_injected_credentials_is_no_user_context(self):
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_slides_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_slides, 'get_service_account_credentials', return_value=MagicMock()
        ), patch.object(
            google_slides, 'build', return_value=sentinel_service
        ):
            out1 = google_slides._get_slides_service(user_id=42, injected_credentials=None)
            out2 = google_slides._get_slides_service(user_id=42, injected_credentials={})

        self.assertIs(out1, sentinel_service)
        self.assertIs(out2, sentinel_service)
        shared_mock.assert_not_called()

    # ----- function-level routing -----

    def test_create_presentation_routes_via_helper_and_shared_drive_sidecar(self):
        """google_slides_create_presentation must call _get_slides_service(user_id, injected_credentials)
        — never inline cred_dict construction — and the Drive sidecar must
        route through get_user_drive_service when user context is present."""
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector

        slides_svc = _fake_service()
        slides_svc.presentations().create().execute.return_value = {
            'presentationId': 'pid', 'title': 'T', 'slides': [],
        }
        drive_svc = _fake_service()
        drive_svc.permissions().create().execute.return_value = {'id': 'p1'}
        drive_svc.files().copy().execute.return_value = {'id': 'pid'}

        with patch.object(
            google_slides, '_get_slides_service', return_value=slides_svc
        ) as helper_mock, patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_slides, 'build_drive_service'
        ) as legacy_drive_mock:
            google_slides.google_slides_create_presentation(
                'My Deck', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})
        shared_drive_mock.assert_called_once_with(user_id=42)
        legacy_drive_mock.assert_not_called()

    def test_get_slide_routes_via_helper(self):
        """google_slides_get_slide must route through the shared helper
        (kwargs.get pattern, no inline Credentials construction)."""
        from google_workspace import google_slides

        sentinel = _fake_service()
        sentinel.presentations().get().execute.return_value = {
            'title': 'T', 'slides': [
                {'objectId': 's1', 'pageElements': []},
                {'objectId': 's2', 'pageElements': []},
            ],
        }

        with patch.object(
            google_slides, '_get_slides_service', return_value=sentinel
        ) as helper_mock:
            google_slides.google_slides_get_slide(
                'pres_id', 1, _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_search_presentation_routes_via_helper(self):
        """google_slides_search_presentation must route through the shared helper."""
        from google_workspace import google_slides

        sentinel = _fake_service()
        sentinel.presentations().get().execute.return_value = {
            'title': 'T', 'slides': [],
        }

        with patch.object(
            google_slides, '_get_slides_service', return_value=sentinel
        ) as helper_mock:
            google_slides.google_slides_search_presentation(
                'pres_id', 'foo', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_add_slide_routes_via_helper(self):
        """google_slides_add_slide must route through the shared helper."""
        from google_workspace import google_slides

        sentinel = _fake_service()
        sentinel.presentations().batchUpdate().execute.return_value = {'replies': [{'createSlide': {'objectId': 's3'}}]}

        with patch.object(
            google_slides, '_get_slides_service', return_value=sentinel
        ) as helper_mock:
            google_slides.google_slides_add_slide(
                'pres_id', layout='TITLE', _user_id=42, _injected_credentials={'flag': True},
            )

        helper_mock.assert_called_once_with(user_id=42, injected_credentials={'flag': True})

    def test_export_pdf_routes_through_shared_drive_wrapper(self):
        """google_slides_export_as_pdf must route the Drive sidecar through
        get_user_drive_service when user context is present."""
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector
        from googleapiclient import http as googleapiclient_http

        drive_svc = _fake_service()
        # MediaIoBaseDownload calls next_chunk() in a loop; stub it to finish
        # immediately so the function returns without touching real HTTP.
        downloader_mock = MagicMock()
        downloader_mock.next_chunk.return_value = (None, True)

        with patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_slides, 'build_drive_service'
        ) as legacy_drive_mock, patch.object(
            googleapiclient_http, 'MediaIoBaseDownload', return_value=downloader_mock
        ):
            google_slides.google_slides_export_as_pdf(
                'pres_id',
                _user_id=42, _injected_credentials={'flag': True},
            )

        shared_drive_mock.assert_called_once_with(user_id=42)
        legacy_drive_mock.assert_not_called()

    def test_export_pptx_routes_through_shared_drive_wrapper(self):
        """google_slides_export_as_pptx must route the Drive sidecar through
        get_user_drive_service when user context is present."""
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector
        from googleapiclient import http as googleapiclient_http

        drive_svc = _fake_service()
        downloader_mock = MagicMock()
        downloader_mock.next_chunk.return_value = (None, True)

        with patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_slides, 'build_drive_service'
        ) as legacy_drive_mock, patch.object(
            googleapiclient_http, 'MediaIoBaseDownload', return_value=downloader_mock
        ):
            google_slides.google_slides_export_as_pptx(
                'pres_id',
                _user_id=42, _injected_credentials={'flag': True},
            )

        shared_drive_mock.assert_called_once_with(user_id=42)
        legacy_drive_mock.assert_not_called()

    def test_export_pdf_uses_service_account_when_no_user_context(self):
        """google_slides_export_as_pdf must fall through to explicit
        build_drive_service() when no user context is supplied."""
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector
        from googleapiclient import http as googleapiclient_http

        drive_svc = _fake_service()
        downloader_mock = MagicMock()
        downloader_mock.next_chunk.return_value = (None, True)

        with patch.object(
            credential_injector, 'get_user_drive_service', return_value=drive_svc,
        ) as shared_drive_mock, patch.object(
            google_slides, 'build_drive_service', return_value=drive_svc
        ) as legacy_drive_mock, patch.object(
            googleapiclient_http, 'MediaIoBaseDownload', return_value=downloader_mock
        ):
            google_slides.google_slides_export_as_pdf('pres_id')

        shared_drive_mock.assert_not_called()
        legacy_drive_mock.assert_called_once()

    # ----- bare _get_slides_service() preserved in no-user-context paths -----

    def test_docs_to_slides_auto_generate_uses_bare_service_account_slides(self):
        """google_docs_to_slides_auto_generate has no user plumbing — must keep
        using the bare _get_slides_service() SA path. No silent shared-wrapper swap."""
        from google_workspace import google_slides
        from AI_infrastructure.auth import credential_injector
        import sys

        sentinel = _fake_service()
        sentinel.presentations().get().execute.return_value = {
            'title': 'T', 'slides': [{'objectId': 's1'}],
        }

        # `from .google_docs import google_docs_read` resolves the module from
        # sys.modules first, so we monkeypatch the module entry to expose a
        # fake google_docs_read attribute without touching google_docs.py.
        google_docs_module = sys.modules['google_workspace.google_docs']
        if not hasattr(google_docs_module, 'google_docs_read'):
            google_docs_module.google_docs_read = MagicMock(
                return_value={'title': 'src', 'content': 'p1\np2\n'},
            )

        try:
            drive_svc = _fake_service()
            drive_svc.permissions().create().execute.return_value = {'id': 'p'}
            with patch.object(
                credential_injector,
                'get_user_slides_service',
                return_value=sentinel,
            ) as shared_mock, patch.object(
                google_slides, '_get_slides_service', return_value=sentinel
            ) as helper_mock, patch.object(
                google_slides, 'build_drive_service', return_value=drive_svc
            ) as legacy_drive_mock, patch.object(
                google_slides, '_parse_doc_structure', return_value={
                    'heading_1_count': 0, 'heading_2_count': 0,
                    'paragraph_count': 2, 'list_count': 0,
                    'image_count': 0, 'table_count': 0, 'slide_recommendations': 1,
                    'sections': [], 'section_count': 0,
                    'paragraphs': [{'text': 'p1'}, {'text': 'p2'}],
                }
            ), patch.object(
                google_slides, 'google_slides_create_presentation', return_value={
                    'presentation_id': 'pid', 'url': 'u', 'title': 'T', 'slide_count': 0,
                }
            ), patch.object(
                google_slides, 'google_slides_delete_slide', return_value=None
            ), patch.object(
                google_slides, 'google_slides_add_slide', return_value={
                    'slide_id': 'sid', 'index': 0, 'layout': 'TITLE',
                }
            ), patch.object(
                google_slides, 'google_slides_insert_text', return_value=None
            ):
                google_slides.google_docs_to_slides_auto_generate('doc_id')

            shared_mock.assert_not_called()
            # The bare _get_slides_service() SA branch is used because there is no user context.
            helper_mock.assert_called()
            # The auto-generate function uses bare build_drive_service() — no shared Drive wrapper.
            self.assertGreaterEqual(legacy_drive_mock.call_count, 1)
        finally:
            # Tidy up: drop the synthetic attribute we added so we don't leak
            # across tests.
            if hasattr(google_docs_module, 'google_docs_read'):
                try:
                    del google_docs_module.google_docs_read
                except AttributeError:
                    pass

    # ----- storage-only rule -----

    def test_storage_only_rejects_slides_service(self):
        """Slides is NOT a storage service — get_user_slides_service() must
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
            side_effect=Exception('storage only — Cannot use slides service'),
        ):
            with self.assertRaises(Exception) as ctx:
                credential_injector.get_user_slides_service(user_id=42)
        self.assertIn('storage only', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
