"""Phase 7 — Forms routes user Forms v1 + Drive v3 sidecars through the shared injector.

Goals (from the plan):
- Replace the legacy `build_forms_service_with_user_creds` /
  `build_drive_service_with_user_creds` paths with the shared
  `get_user_forms_service()` / `get_user_drive_service()` wrappers.
- Drop the broken `_get_user_credentials_if_available(kwargs)` branch in
  `google_forms_search_responses` (Plan Phase 7) and use the shared helper
  like every other entry point.
- Remove the silent service-account fallback: the Forms API cannot be
  authorized without domain-wide delegation, so the helper must raise a
  clear authentication error instead of falling back to a known-broken SA path.
- Storage-only rule: a storage-only link must NOT be allowed to mint a
  Forms service (only Drive is a storage service).
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


class FormsSharedRouteTests(unittest.TestCase):
    """Lock down the Phase 7 routing contract for google_forms.py."""

    # ----- package import surface -----

    def test_module_imports_without_legacy_helpers(self):
        """Phase 7: legacy `_get_user_credentials_if_available` and the oauth
        loader helpers must be gone from google_forms."""
        from google_workspace import google_forms
        self.assertFalse(
            hasattr(google_forms, '_get_user_credentials_if_available'),
            'Phase 7: legacy _get_user_credentials_if_available must be removed',
        )
        self.assertFalse(
            hasattr(google_forms, 'Credentials'),
            'Phase 7: google.oauth2.credentials.Credentials import must be dropped',
        )

    def test_module_does_not_pin_to_legacy_loader_builders(self):
        """Phase 7: google_forms must not import build_forms_service /
        build_drive_service from google_auth_helper anymore — those are the
        legacy parallel-loader builders."""
        from google_workspace import google_forms
        # `build_forms_service` should not be present as a module-level
        # symbol (not imported by google_forms).
        for name in ('build_forms_service', 'build_drive_service',
                     'build_forms_service_with_user_creds',
                     'build_drive_service_with_user_creds'):
            self.assertFalse(
                hasattr(google_forms, name),
                f'Phase 7: legacy {name} must not be imported in google_forms',
            )

    # ----- _get_forms_service helper -----

    def test_forms_helper_uses_shared_wrapper_when_user_context_present(self):
        """With user_id + injected_credentials, the helper must call
        get_user_forms_service(user_id=user_id) and never fall back to a
        service account."""
        from google_workspace import google_forms
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_forms_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_forms, 'HAS_FORMS_API', True,
        ):
            out = google_forms._get_forms_service(
                _user_id=42, _injected_credentials={'flag': True},
            )

        self.assertIs(out, sentinel_service)
        shared_mock.assert_called_once_with(user_id=42)

    def test_forms_helper_raises_when_no_user_context(self):
        """Without user context, the helper must raise a clear authentication
        error (the Forms API cannot be authorized with a service account
        without domain-wide delegation)."""
        from google_workspace import google_forms
        from AI_infrastructure.auth import credential_injector

        with patch.object(
            credential_injector,
            'get_user_forms_service',
            return_value=_fake_service(),
        ) as shared_mock, patch.object(
            google_forms, 'HAS_FORMS_API', True,
        ):
            with self.assertRaises(Exception) as ctx:
                google_forms._get_forms_service()

        self.assertIn('Google Forms tools require an authenticated user', str(ctx.exception))
        shared_mock.assert_not_called()

    def test_forms_helper_falsy_injected_credentials_is_no_user_context(self):
        """Falsy injected_credentials (None / empty dict) is treated as
        no-user-context — the helper raises a clear auth error."""
        from google_workspace import google_forms
        from AI_infrastructure.auth import credential_injector

        with patch.object(
            credential_injector,
            'get_user_forms_service',
            return_value=_fake_service(),
        ) as shared_mock, patch.object(
            google_forms, 'HAS_FORMS_API', True,
        ):
            with self.assertRaises(Exception):
                google_forms._get_forms_service(_user_id=42, _injected_credentials=None)
            with self.assertRaises(Exception):
                google_forms._get_forms_service(_user_id=42, _injected_credentials={})

        shared_mock.assert_not_called()

    def test_forms_helper_propagates_shared_injector_failure(self):
        """If the shared wrapper raises (no user OAuth row), the helper must
        propagate — never silently switch to a service account."""
        from google_workspace import google_forms
        from AI_infrastructure.auth import credential_injector

        boom = RuntimeError('user 42 has no Google OAuth row')
        with patch.object(
            credential_injector,
            'get_user_forms_service',
            side_effect=boom,
        ), patch.object(
            google_forms, 'HAS_FORMS_API', True,
        ):
            with self.assertRaises(RuntimeError) as ctx:
                google_forms._get_forms_service(
                    _user_id=42, _injected_credentials={'flag': True},
                )

        self.assertIn('user 42 has no Google OAuth row', str(ctx.exception))

    # ----- _get_drive_service helper -----

    def test_drive_helper_uses_shared_wrapper_when_user_context_present(self):
        """With user_id + injected_credentials, the Drive sidecar must call
        get_user_drive_service(user_id=user_id)."""
        from google_workspace import google_forms
        from AI_infrastructure.auth import credential_injector

        sentinel_service = _fake_service()
        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=sentinel_service,
        ) as shared_mock, patch.object(
            google_forms, 'HAS_FORMS_API', True,
        ):
            out = google_forms._get_drive_service(
                _user_id=42, _injected_credentials={'flag': True},
            )

        self.assertIs(out, sentinel_service)
        shared_mock.assert_called_once_with(user_id=42)

    def test_drive_helper_raises_when_no_user_context(self):
        """Without user context, the Drive sidecar helper must raise a clear
        authentication error (no Forms service-account path)."""
        from google_workspace import google_forms
        from AI_infrastructure.auth import credential_injector

        with patch.object(
            credential_injector,
            'get_user_drive_service',
            return_value=_fake_service(),
        ) as shared_mock, patch.object(
            google_forms, 'HAS_FORMS_API', True,
        ):
            with self.assertRaises(Exception) as ctx:
                google_forms._get_drive_service()

        self.assertIn('Google Drive sidecar from Forms requires an authenticated user',
                      str(ctx.exception))
        shared_mock.assert_not_called()

    # ----- Phase 7 bug fix: google_forms_search_responses -----

    def test_search_responses_uses_shared_helper_directly(self):
        """google_forms_search_responses must call _get_forms_service(**kwargs)
        — NOT the undefined `build('forms', 'v1', credentials=...)` branch that
        previously referenced the never-defined _get_user_credentials_if_available
        helper. Verify the helper is invoked and the legacy build call is gone."""
        from google_workspace import google_forms

        sentinel = _fake_service()
        sentinel.forms().responses().list().execute.return_value = {
            'responses': [
                {'responseId': 'r1', 'answers': {'q1': {'textAnswers': {'answers': [{'value': 'foo bar'}]}}}},
                {'responseId': 'r2', 'answers': {'q1': {'textAnswers': {'answers': [{'value': 'baz'}]}}}},
            ],
        }

        with patch.object(
            google_forms, '_get_forms_service', return_value=sentinel
        ) as helper_mock, patch(
            'google_workspace.google_forms.build', create=True,
        ) as build_mock:
            out = google_forms.google_forms_search_responses(
                'form_id', 'foo',
                _user_id=42, _injected_credentials={'flag': True},
            )

        # The shared helper is invoked with **kwargs (which propagates the
        # user context flags).
        helper_mock.assert_called_once()
        self.assertIn('total_matches', out)
        # The legacy direct `build('forms', 'v1', credentials=...)` branch
        # must NOT be hit — there is no `build` symbol on google_forms
        # anymore.
        build_mock.assert_not_called()

    def test_search_responses_has_no_legacy_build_call(self):
        """Phase 7: ensure the legacy `build(` import is not in google_forms
        module namespace — `build_forms_service_with_user_creds` is gone and
        so is the direct `build` constructor call."""
        from google_workspace import google_forms
        self.assertFalse(
            hasattr(google_forms, 'build'),
            'Phase 7: google_forms must not import googleapiclient.discovery.build',
        )

    # ----- function-level routing -----

    def test_create_form_routes_via_helper(self):
        """google_forms_create_form must route through _get_forms_service(**kwargs)
        and the Drive sidecar must route through _get_drive_service(**kwargs)."""
        from google_workspace import google_forms

        sentinel = _fake_service()
        sentinel.forms().create().execute.return_value = {
            'formId': 'new_id',
            'info': {'title': 'My Form'},
            'responderUri': 'https://docs.google.com/forms/d/e/new_id/viewform',
        }
        # Drive sidecar: google_forms_create_form's body eventually calls
        # _get_drive_service too — stub both.
        sentinel_drive = _fake_service()
        sentinel_drive.permissions().create().execute.return_value = {'id': 'p1'}

        with patch.object(
            google_forms, '_get_forms_service', return_value=sentinel
        ) as forms_mock, patch.object(
            google_forms, '_get_drive_service', return_value=sentinel_drive
        ) as drive_mock:
            out = google_forms.google_forms_create_form(
                'My Form', _user_id=42, _injected_credentials={'flag': True},
            )

        # Forms helper is invoked with kwargs (which carries the user flags).
        forms_mock.assert_called_once()
        drive_mock.assert_called_once()
        self.assertEqual(out['form_id'], 'new_id')
        self.assertTrue(out['shareable'])

    # ----- storage-only rule -----

    def test_storage_only_rejects_forms_service(self):
        """Forms is NOT a storage service — get_user_forms_service() must
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

        # Forms call MUST raise — storage-only rule.
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            side_effect=Exception('storage only — Cannot use forms service'),
        ):
            with self.assertRaises(Exception) as ctx:
                credential_injector.get_user_forms_service(user_id=42)
        self.assertIn('storage only', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
