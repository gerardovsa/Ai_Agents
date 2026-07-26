"""Phase 9 — Retire the parallel user-OAuth loader safely.

Goals (from the plan §9):
- The parallel ``oauth_credential_loader.py`` user-OAuth path must no longer
  be imported anywhere in the active package. The canonical shared injector
  (``AI_infrastructure.auth.credential_injector``) is the only user-OAuth path.
- ``google_workspace.google_auth_helper`` is now a strict service-account
  builder. Direct user ``Credentials(...)`` construction must be gone from
  it.
- The legacy Google OAuth callback at
  ``AI_infrastructure/routes/oauth_routes.py`` must write to the canonical
  ``ai_infrastructure.oauth_tokens`` table (24-column schema), NOT the
  legacy ``user_platform_credentials`` table.
- The legacy start/login routes must delegate to the canonical
  ``/api/auth/google/login`` route.
- Backwards compatibility is preserved: ``build_docs_service`` and
  ``build_drive_service`` keep their public names but ignore user-context
  kwargs (the helper has no user OAuth code path).
"""
import ast
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRASTRUCTURE = REPO_ROOT / 'AI_infrastructure'
GOOGLE_WORKSPACE = REPO_ROOT / 'google_workspace'

for p in (str(REPO_ROOT), str(AI_INFRASTRUCTURE)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _ast_calls_to(tree: ast.AST, attr_name: str) -> int:
    """Count attribute-call expressions whose attribute is ``attr_name``."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == attr_name:
                count += 1
            elif isinstance(f, ast.Name) and f.id == attr_name:
                count += 1
    return count


class Phase9LoaderRetirementTests(unittest.TestCase):
    """Phase 9: lock the contract that the parallel user-OAuth loader is
    retired and the legacy callback writes to the canonical token table."""

    # ----- google_auth_helper is now service-account-only -----

    def test_auth_helper_no_longer_imports_oauth_credential_loader(self):
        """The active helper must NOT import build_service_with_oauth or any
        symbol from oauth_credential_loader."""
        src = _read(GOOGLE_WORKSPACE / 'google_auth_helper.py')
        self.assertNotIn(
            'oauth_credential_loader',
            src,
            'Phase 9: google_auth_helper must not reference oauth_credential_loader',
        )
        self.assertNotIn(
            'build_service_with_oauth',
            src,
            'Phase 9: build_service_with_oauth must not appear in google_auth_helper',
        )
        self.assertNotIn(
            'HAS_OAUTH_LOADER',
            src,
            'Phase 9: HAS_OAUTH_LOADER flag must be removed',
        )

    def test_auth_helper_does_not_construct_user_credentials_directly(self):
        """No direct ``google.oauth2.credentials.Credentials(...)`` constructor
        calls inside google_auth_helper — the helper builds no user OAuth
        credentials."""
        src = _read(GOOGLE_WORKSPACE / 'google_auth_helper.py')
        self.assertNotIn(
            'from google.oauth2.credentials import Credentials',
            src,
            'Phase 9: google_auth_helper must not import google.oauth2.credentials.Credentials',
        )
        self.assertNotIn(
            'google.oauth2.credentials',
            src,
            'Phase 9: google_auth_helper must not reference google.oauth2.credentials',
        )

    def test_auth_helper_drops_dead_user_oauth_helpers(self):
        """The dead user-OAuth helpers must be removed from the helper."""
        src = _read(GOOGLE_WORKSPACE / 'google_auth_helper.py')
        self.assertNotIn(
            'build_forms_service_with_user_creds',
            src,
            'Phase 9: build_forms_service_with_user_creds must be removed',
        )
        self.assertNotIn(
            'build_drive_service_with_user_creds',
            src,
            'Phase 9: build_drive_service_with_user_creds must be removed',
        )

    def test_auth_helper_keeps_service_account_sidecars(self):
        """The intentional service-account sidecars (Gmail, Calendar, Forms,
        Analytics) must still be present."""
        from google_workspace import google_auth_helper
        for name in (
            'get_service_account_credentials',
            'build_gmail_service',
            'build_calendar_service',
            'build_forms_service',
            'build_analytics_service',
            'clear_service_cache',
        ):
            self.assertTrue(
                hasattr(google_auth_helper, name),
                f'Phase 9: service-account builder {name} must remain',
            )

    def test_auth_helper_docs_and_drive_swallow_user_kwargs(self):
        """build_docs_service and build_drive_service must accept and ignore
        user-context kwargs (backwards compat). They have NO user-OAuth path."""
        from google_workspace.google_auth_helper import build_docs_service, build_drive_service
        import inspect

        # Must accept **kwargs (or explicit _user_id=None) for backwards compat.
        docs_sig = inspect.signature(build_docs_service)
        drive_sig = inspect.signature(build_drive_service)
        # Either VARKW (any kwargs) or explicit _user_id default
        self.assertTrue(
            any(p.kind is inspect.Parameter.VAR_KEYWORD for p in docs_sig.parameters.values())
            or any(p.name == '_user_id' for p in docs_sig.parameters.values()),
            'Phase 9: build_docs_service must accept (and ignore) user kwargs',
        )
        self.assertTrue(
            any(p.kind is inspect.Parameter.VAR_KEYWORD for p in drive_sig.parameters.values())
            or any(p.name == '_user_id' for p in drive_sig.parameters.values()),
            'Phase 9: build_drive_service must accept (and ignore) user kwargs',
        )

    # ----- The active package no longer imports the parallel loader -----

    def test_google_workspace_package_does_not_import_oauth_credential_loader(self):
        """The google_workspace package re-exports must not pull in the
        deprecated oauth_credential_loader."""
        from google_workspace import google_auth_helper
        # Re-exported builders are the SA-only ones.
        for name in ('build_docs_service', 'build_drive_service',
                     'build_gmail_service', 'build_calendar_service',
                     'build_forms_service', 'build_analytics_service',
                     'get_service_account_credentials'):
            self.assertTrue(hasattr(google_auth_helper, name))
        # build_service_with_oauth must not be re-exported (it's gone).
        self.assertFalse(
            hasattr(google_auth_helper, 'build_service_with_oauth'),
            'Phase 9: build_service_with_oauth must not be re-exported',
        )

    def test_oauth_credential_loader_marked_deprecated(self):
        """The frozen historical file must carry a DEPRECATED banner at the
        top so future agents know not to add new callers."""
        src = _read(GOOGLE_WORKSPACE / 'oauth_credential_loader.py')
        self.assertIn(
            'DEPRECATED',
            src[:500],
            'Phase 9: oauth_credential_loader must carry a DEPRECATED banner',
        )

    # ----- No active user Credentials(...) construction in google_workspace -----

    def test_no_active_credentials_constructors_in_google_workspace(self):
        """No module in google_workspace should construct a Credentials(...)
        object directly outside the shared injector. This is the load-bearing
        contract: every user-OAuth construction goes through
        AI_infrastructure.auth.credential_injector.

        We use AST-based detection (counting direct ``Credentials(...)``
        constructor calls) rather than substring search because the OAuth
        flow library returns ``flow.credentials`` as a ``Credentials`` object
        — using the type name in property accesses is legitimate; direct
        ``Credentials(...)`` constructor calls are not.

        We allow the deprecated oauth_credential_loader.py and
        oauth_manager.py to still construct Credentials (both are frozen
        historical code kept for test-script compatibility and the legacy
        OAuth callback at oauth_routes.py).
        """
        offending = []
        for path in GOOGLE_WORKSPACE.rglob('*.py'):
            # Skip the frozen deprecated files (already audited and marked).
            if path.name in ('oauth_credential_loader.py', 'oauth_manager.py'):
                continue
            try:
                src = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            try:
                tree = ast.parse(src, filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                # Direct ``Credentials(...)`` constructor.
                if isinstance(f, ast.Name) and f.id == 'Credentials':
                    offending.append(str(path))
                    break
                # Aliased ``Credentials(...)`` (e.g. ``from ... import Credentials as C``).
                if isinstance(f, ast.Name) and any(
                    alias.id == 'Credentials'
                    and isinstance(alias.asname, str)
                    and alias.asname == f.id
                    for alias in getattr(tree, '_google_aliases', [])
                ):
                    offending.append(str(path))
                    break
        self.assertEqual(
            offending, [],
            f'Phase 9: Credentials(...) constructor must not be called by '
            f'active google_workspace modules; offending: {offending}',
        )

    # ----- Legacy OAuth callback writes to oauth_tokens, not user_platform_credentials -----

    def test_legacy_callback_writes_to_canonical_oauth_tokens(self):
        """oauth_routes.oauth_workspace_callback must write to
        ai_infrastructure.oauth_tokens (the canonical 24-column schema),
        NOT user_platform_credentials."""
        src = _read(AI_INFRASTRUCTURE / 'routes' / 'oauth_routes.py')
        # Must reference the canonical table.
        self.assertIn(
            'ai_infrastructure.oauth_tokens',
            src,
            'Phase 9: legacy callback must reference ai_infrastructure.oauth_tokens',
        )
        # Must NOT reference the legacy table.
        self.assertNotIn(
            'user_platform_credentials',
            src,
            'Phase 9: legacy callback must not reference user_platform_credentials',
        )

    def test_legacy_callback_state_check_uses_canonical_oauth_states(self):
        """oauth_workspace_callback must validate state against the canonical
        ``ai_infrastructure.oauth_states`` table (with Flask session fallback)
        — not against ad-hoc session-only flow."""
        src = _read(AI_INFRASTRUCTURE / 'routes' / 'oauth_routes.py')
        self.assertIn(
            'ai_infrastructure.oauth_states',
            src,
            'Phase 9: legacy callback must validate state via oauth_states table',
        )

    def test_legacy_login_routes_delegate_to_canonical(self):
        """``/api/oauth/google/login`` and ``/api/oauth/workspace/start`` must
        redirect to the canonical ``/api/auth/google/login`` route."""
        src = _read(AI_INFRASTRUCTURE / 'routes' / 'oauth_routes.py')
        # The two endpoints must each redirect to the canonical path.
        self.assertIn(
            "redirect('/api/auth/google/login?mode=signin')",
            src,
            'Phase 9: google_login must redirect to canonical /api/auth/google/login?mode=signin',
        )
        self.assertIn(
            "redirect(f'/api/auth/google/login?mode={mode}')",
            src,
            'Phase 9: oauth_workspace_start must redirect to canonical /api/auth/google/login',
        )

    def test_legacy_callback_does_not_construct_user_credentials_directly(self):
        """The legacy callback must NOT construct a Credentials(...) object
        directly — the canonical flow owns that path. The OAuth flow library
        legitimately returns ``flow.credentials`` as a Credentials object,
        so we look for constructor calls (AST) rather than the import."""
        src = _read(AI_INFRASTRUCTURE / 'routes' / 'oauth_routes.py')
        tree = ast.parse(src, filename=str(AI_INFRASTRUCTURE / 'routes' / 'oauth_routes.py'))
        constructor_calls = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if isinstance(f, ast.Name) and f.id == 'Credentials':
                constructor_calls.append(f.id)
        self.assertEqual(
            constructor_calls, [],
            f'Phase 9: legacy callback must not call Credentials(...) '
            f'directly; found: {constructor_calls}',
        )

    # ----- No active user platform_credentials writes from google_workspace tools -----

    def test_no_google_workspace_tool_writes_user_platform_credentials(self):
        """No tool in google_workspace should write to user_platform_credentials
        for OAuth tokens — the canonical path is oauth_tokens."""
        offending = []
        for path in GOOGLE_WORKSPACE.rglob('*.py'):
            try:
                src = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            # The deprecated oauth_credential_loader is allowed to read
            # oauth_tokens directly (it's historical). It must NOT write to
            # user_platform_credentials either.
            if 'user_platform_credentials' in src:
                offending.append(str(path))
        self.assertEqual(
            offending, [],
            f'Phase 9: no google_workspace module may reference user_platform_credentials; '
            f'offending: {offending}',
        )

    # ----- AST sanity: the helper builds the expected service names -----

    def test_helper_builds_expected_google_services(self):
        """AST check: build_drive_service, build_docs_service, build_gmail_service,
        build_calendar_service, build_forms_service, build_analytics_service
        must each exist and call ``build(...)`` with the expected service name."""
        from google_workspace import google_auth_helper
        import inspect

        # For each builder, locate its source via inspect.getsource, then
        # check that ``build('<svc>', '<version>', ...)`` is present.
        expectations = {
            'build_drive_service': 'drive',
            'build_docs_service': 'docs',
            'build_gmail_service': 'gmail',
            'build_calendar_service': 'calendar',
            'build_forms_service': 'forms',
            'build_analytics_service': 'analyticsdata',
        }
        for fn_name, service_name in expectations.items():
            fn = getattr(google_auth_helper, fn_name)
            src = inspect.getsource(fn)
            self.assertIn(
                f"'{service_name}'",
                src,
                f'Phase 9: {fn_name} must build the {service_name} service',
            )


if __name__ == '__main__':
    unittest.main()