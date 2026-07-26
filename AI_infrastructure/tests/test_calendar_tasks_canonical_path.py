"""Canonical-path tests for Calendar and Tasks Google modules.

These tests prove that Calendar and Tasks construct services through the
shared named wrappers (`get_user_calendar_service`, `get_user_tasks_service`)
exactly once per request, and that they preserve user-facing missing-credential
and storage-only errors.

Mocking strategy: patch the named wrappers on the `credential_injector` module
the platform code already imports from, and patch the lower-level creator on
the same module to count and forbid direct calls.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)


class CalendarCanonicalPathTests(unittest.TestCase):
    def test_google_calendar_service_uses_named_wrapper_once(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_calendar_service",
            return_value=object(),
        ) as wrapper, mock.patch(
            "AI_infrastructure.auth.credential_injector.create_google_service_with_user_credentials",
            side_effect=AssertionError("Calendar must not call the lower-level creator directly"),
        ):
            from google_workspace.google_calendar import GoogleCalendarTools

            tools = GoogleCalendarTools(_user_id=11, _injected_credentials=True)
            service = tools._get_service()

        wrapper.assert_called_once_with(user_id=11, _user_id=11)
        self.assertIsNotNone(service)

    def test_google_calendar_picks_user_id_from_kwargs(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_calendar_service",
            return_value=object(),
        ) as wrapper, mock.patch(
            "AI_infrastructure.auth.credential_injector.create_google_service_with_user_credentials",
            side_effect=AssertionError("Calendar must not call the lower-level creator directly"),
        ):
            from google_workspace.google_calendar import GoogleCalendarTools

            tools = GoogleCalendarTools()  # no _user_id at construction
            service = tools._get_service(_user_id=42, _injected_credentials=True)

        wrapper.assert_called_once_with(user_id=42, _user_id=42)
        self.assertIsNotNone(service)

    def test_google_calendar_missing_user_id_raises(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_calendar_service",
            side_effect=AssertionError("Wrapper must not be reached without _user_id"),
        ):
            from google_workspace.google_calendar import GoogleCalendarTools

            tools = GoogleCalendarTools()
            with self.assertRaisesRegex(Exception, "OAuth credentials required"):
                tools._get_service()

    def test_google_calendar_propagates_storage_only_error(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_calendar_service",
            side_effect=Exception("Google account linked for storage only"),
        ):
            from google_workspace.google_calendar import GoogleCalendarTools

            tools = GoogleCalendarTools(_user_id=11, _injected_credentials=True)
            with self.assertRaisesRegex(Exception, "storage only"):
                tools._get_service()


class TasksCanonicalPathTests(unittest.TestCase):
    def test_build_tasks_service_uses_named_wrapper_once(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_tasks_service",
            return_value=object(),
        ) as wrapper, mock.patch(
            "AI_infrastructure.auth.credential_injector.create_google_service_with_user_credentials",
            side_effect=AssertionError("Tasks must not call the lower-level creator directly"),
        ):
            from google_workspace.google_tasks import build_tasks_service

            service = build_tasks_service(_user_id=11, _injected_credentials=True)

        wrapper.assert_called_once_with(user_id=11, _user_id=11)
        self.assertIsNotNone(service)

    def test_build_tasks_service_missing_user_id_raises(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_tasks_service",
            side_effect=AssertionError("Wrapper must not be reached without _user_id"),
        ):
            from google_workspace.google_tasks import build_tasks_service

            with self.assertRaisesRegex(Exception, "Google Tasks requires database OAuth"):
                build_tasks_service()

    def test_build_tasks_service_propagates_storage_only_error(self):
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_tasks_service",
            side_effect=Exception("Google account linked for storage only"),
        ):
            from google_workspace.google_tasks import build_tasks_service

            with self.assertRaisesRegex(Exception, "storage only"):
                build_tasks_service(_user_id=11, _injected_credentials=True)

    def test_google_tasks_list_task_lists_invokes_wrapper_through_helper(self):
        # The tool function wraps its body in try/except Exception and returns
        # an error dict on any failure, so we don't need to fake a complete
        # Google API service tree. The contract we care about is that the
        # public tool function reaches the named wrapper exactly once.
        with mock.patch(
            "AI_infrastructure.auth.credential_injector.get_user_tasks_service",
            return_value=mock.Mock(),
        ) as wrapper:
            from google_workspace.google_tasks import google_tasks_list_task_lists

            google_tasks_list_task_lists(_user_id=11, _injected_credentials=True)

        wrapper.assert_called_once_with(user_id=11, _user_id=11)


if __name__ == "__main__":
    unittest.main()
