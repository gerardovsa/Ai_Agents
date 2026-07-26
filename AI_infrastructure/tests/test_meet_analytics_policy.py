"""Phase 8 — Meet/Analytics policy-preserving cleanup.

Goals (from the plan):
- Keep Calendar-backed user meetings on the shared Calendar v3 OAuth path.
- Keep native Meet v2 Spaces API explicitly service-account owned.
- Keep `google_analytics.py` service-account only.
- Assert the policy is preserved: Calendar-backed Meet uses user OAuth,
  native Meet v2 uses service account, Analytics uses service account.
- The Phase 8 renames must not break existing callers — both new and
  legacy helpers must be reachable.
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


class MeetAnalyticsPolicyTests(unittest.TestCase):
    """Phase 8: lock the policy that Calendar-backed Meet uses user OAuth,
    native Meet v2 uses service account, and Analytics is service-account only."""

    # ----- Meet: Calendar-backed (user OAuth) -----

    def test_calendar_service_for_user_uses_shared_injector(self):
        """When user context is present, _get_calendar_service_for_user must
        route through the shared user OAuth injector (create_google_service_with_user_credentials)."""
        from google_workspace import google_meet
        from AI_infrastructure.auth import credential_injector

        sentinel = _fake_service()
        with patch.object(
            credential_injector,
            'create_google_service_with_user_credentials',
            return_value=sentinel,
        ) as shared_mock:
            out = google_meet._get_calendar_service_for_user(
                _user_id=42, _injected_credentials={'flag': True},
            )

        self.assertIs(out, sentinel)
        shared_mock.assert_called_once_with(
            user_id=42, service_name='calendar', version='v3',
        )

    def test_calendar_service_for_user_falls_back_to_service_account(self):
        """Without user context, the helper must fall back to a service-account
        Calendar client (intentional — spaces callers need a meeting without
        a logged-in user)."""
        from google_workspace import google_meet
        from google.oauth2 import service_account as sa

        sentinel = _fake_service()
        with patch.object(
            google_meet.service_account.Credentials, 'from_service_account_file',
            return_value=MagicMock(),
        ) as sa_mock, patch.object(
            google_meet, 'build', return_value=sentinel,
        ) as build_mock:
            out = google_meet._get_calendar_service_for_user()

        self.assertIs(out, sentinel)
        sa_mock.assert_called_once()
        # scopes arg must contain the calendar scope
        scopes_arg = sa_mock.call_args.kwargs.get('scopes') or sa_mock.call_args.args[1]
        self.assertIn('https://www.googleapis.com/auth/calendar', scopes_arg)
        build_mock.assert_called_once_with('calendar', 'v3', credentials=sa_mock.return_value)

    def test_calendar_service_alias_preserved(self):
        """Phase 8: legacy alias _get_calendar_service must still resolve."""
        from google_workspace import google_meet
        self.assertIs(
            google_meet._get_calendar_service,
            google_meet._get_calendar_service_for_user,
        )

    # ----- Meet: native Meet v2 Spaces (service-account) -----

    def test_native_meet_service_uses_service_account(self):
        """Native Meet v2 Spaces API must use a service account — NOT user OAuth."""
        from google_workspace import google_meet
        from google.oauth2 import service_account as sa

        sentinel = _fake_service()
        with patch.object(
            google_meet.service_account.Credentials, 'from_service_account_file',
            return_value=MagicMock(),
        ) as sa_mock, patch.object(
            google_meet, 'build', return_value=sentinel,
        ) as build_mock:
            out = google_meet._get_native_meet_service_with_service_account()

        self.assertIs(out, sentinel)
        sa_mock.assert_called_once()
        scopes_arg = sa_mock.call_args.kwargs.get('scopes') or sa_mock.call_args.args[1]
        # Both space scopes must be present.
        self.assertIn('https://www.googleapis.com/auth/meetings.space.created', scopes_arg)
        self.assertIn('https://www.googleapis.com/auth/meetings.space.readonly', scopes_arg)
        build_mock.assert_called_once_with('meet', 'v2', credentials=sa_mock.return_value)

    def test_native_meet_service_alias_preserved(self):
        """Phase 8: legacy alias _get_meet_service must still resolve."""
        from google_workspace import google_meet
        self.assertIs(
            google_meet._get_meet_service,
            google_meet._get_native_meet_service_with_service_account,
        )

    def test_native_meet_service_does_not_invoke_user_oauth(self):
        """Native Meet v2 must NEVER call the user OAuth injector — it's
        service-account-only by policy."""
        from google_workspace import google_meet
        from AI_infrastructure.auth import credential_injector

        sentinel = _fake_service()
        with patch.object(
            credential_injector, 'create_google_service_with_user_credentials',
            return_value=_fake_service(),
        ) as shared_mock, patch.object(
            google_meet.service_account.Credentials, 'from_service_account_file',
            return_value=MagicMock(),
        ), patch.object(
            google_meet, 'build', return_value=sentinel,
        ):
            google_meet._get_native_meet_service_with_service_account()

        shared_mock.assert_not_called()

    # ----- Calendar-backed meeting must use Calendar helper, not native Meet helper -----

    def test_calendar_backed_meeting_uses_calendar_helper_not_native_meet(self):
        """google_meet_create_meeting must call the Calendar-backed helper
        (via the legacy alias _get_calendar_service), not the native Meet v2
        helper — meeting creation is via Calendar's conferenceData path.
        We patch at the helper boundary so the test proves the routing
        contract without depending on a real service-account JSON file."""
        from google_workspace import google_meet

        sentinel_cal = _fake_service()
        sentinel_cal.events().insert().execute.return_value = {
            'id': 'evt_id',
            'summary': 'T',
            'start': {'dateTime': '2026-01-01T10:00:00Z'},
            'end': {'dateTime': '2026-01-01T11:00:00Z'},
            'status': 'confirmed',
            'conferenceData': {
                'conferenceId': 'cid',
                'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/abc'}],
            },
        }

        with patch.object(
            google_meet, '_get_calendar_service', return_value=sentinel_cal,
        ) as cal_mock, patch.object(
            google_meet, '_get_meet_service',
            return_value=_fake_service(),
        ) as native_mock:
            google_meet.google_meet_create_meeting(
                title='T',
                start_time='2026-01-01T10:00:00Z',
                _user_id=42, _injected_credentials={'flag': True},
            )

        # The production call sites use the legacy alias, so we patch the
        # alias and verify that the legacy alias resolves to the Calendar
        # helper (which is the policy).
        cal_mock.assert_called_once_with(
            _user_id=42, _injected_credentials={'flag': True},
        )
        native_mock.assert_not_called()

    def test_create_space_uses_native_meet_helper_not_calendar(self):
        """google_meet_create_space must use the native Meet v2 helper
        (Spaces API), NOT the Calendar-backed helper. We patch at the
        helper boundary so the test proves the routing contract without
        depending on a real service-account JSON file."""
        from google_workspace import google_meet

        sentinel_native = _fake_service()
        sentinel_native.spaces().create().execute.return_value = {
            'name': 'spaces/space_id',
            'meetingUri': 'https://meet.google.com/abc-defg-hij',
            'meetingCode': 'abc-defg-hij',
            'config': {'entryPointAccess': 'ALL', 'accessType': 'OPEN'},
        }

        with patch.object(
            google_meet, '_get_meet_service', return_value=sentinel_native,
        ) as native_mock, patch.object(
            google_meet, '_get_calendar_service',
            return_value=_fake_service(),
        ) as cal_mock:
            google_meet.google_meet_create_space(display_name='Standup')

        native_mock.assert_called_once_with()
        cal_mock.assert_not_called()

    # ----- Analytics: service-account-only -----

    def test_analytics_service_uses_service_account(self):
        """_get_analytics_service_with_service_account must build
        with service-account credentials (NOT user OAuth)."""
        from google_workspace import google_analytics
        from google.oauth2 import service_account as sa

        sentinel = _fake_service()
        with patch.object(
            google_analytics, 'build_analytics_service', return_value=sentinel,
        ) as helper_mock, patch.object(
            google_analytics, 'get_service_account_credentials',
            return_value=MagicMock(),
        ) as sa_helper_mock:
            out = google_analytics._get_analytics_service_with_service_account()

        self.assertIs(out, sentinel)
        helper_mock.assert_called_once_with()
        # The legacy `get_service_account_credentials` helper is not used by
        # this path — the Analytics helper uses its own internal SA flow.
        sa_helper_mock.assert_not_called()

    def test_analytics_admin_service_uses_service_account(self):
        """_get_analytics_admin_service_with_service_account must build
        with service-account credentials."""
        from google_workspace import google_analytics

        sentinel = _fake_service()
        with patch.object(
            google_analytics, 'get_service_account_credentials', return_value=MagicMock(),
        ) as sa_mock, patch.object(
            google_analytics, 'build', return_value=sentinel,
        ) as build_mock:
            out = google_analytics._get_analytics_admin_service_with_service_account()

        self.assertIs(out, sentinel)
        sa_mock.assert_called_once()
        scopes_arg = sa_mock.call_args.args[0]
        self.assertIn('https://www.googleapis.com/auth/analytics.readonly', scopes_arg)
        build_mock.assert_called_once_with(
            'analyticsadmin', 'v1beta', credentials=sa_mock.return_value,
        )

    def test_analytics_does_not_invoke_user_oauth(self):
        """Analytics must NEVER call the user OAuth injector — it's
        service-account-only by policy."""
        from google_workspace import google_analytics
        from AI_infrastructure.auth import credential_injector

        with patch.object(
            credential_injector, 'create_google_service_with_user_credentials',
            return_value=_fake_service(),
        ) as shared_mock, patch.object(
            google_analytics, 'build_analytics_service', return_value=_fake_service(),
        ):
            google_analytics._get_analytics_service_with_service_account()
        shared_mock.assert_not_called()

    def test_analytics_aliases_preserved(self):
        """Phase 8: legacy aliases _get_analytics_service and
        _get_analytics_admin_service must still resolve."""
        from google_workspace import google_analytics

        self.assertIs(
            google_analytics._get_analytics_service,
            google_analytics._get_analytics_service_with_service_account,
        )
        self.assertIs(
            google_analytics._get_analytics_admin_service,
            google_analytics._get_analytics_admin_service_with_service_account,
        )

    def test_analytics_drops_dead_credentials_import(self):
        """Phase 8: the unused google.oauth2.credentials.Credentials import
        must be dropped from google_analytics."""
        from google_workspace import google_analytics
        self.assertFalse(
            hasattr(google_analytics, 'Credentials'),
            'Phase 8: google_analytics must not import google.oauth2.credentials.Credentials',
        )


if __name__ == '__main__':
    unittest.main()
